"""
CampusSync ERP - Password Reset Service
=======================================
File: services/password_reset_service.py

Handles secure OTP generation, database hashing, expiration validation,
and password reset for Student, Faculty, and Admin accounts.
"""

import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import Admin, Faculty, Student
from mail.otp_mail import send_password_reset_otp_email


class OtpRequestResult(tuple):
    """
    Subclass of tuple (success, message, email) for 100% backward compatibility
    with callers unpacking 3 values, while providing .blocked and .attempts attributes.
    """
    def __new__(cls, success, message, email=None, blocked=False, attempts=0):
        return super().__new__(cls, (success, message, email))

    def __init__(self, success, message, email=None, blocked=False, attempts=0):
        self.success = success
        self.message = message
        self.email = email
        self.blocked = blocked
        self.attempts = attempts


def _get_user_model_and_role_info(role_type):
    """
    Returns (ModelClass, role_display_name) based on role_type.
    """
    role = role_type.strip().lower()
    if role == 'student':
        return Student, "Student"
    elif role == 'faculty':
        return Faculty, "Faculty"
    elif role == 'admin':
        return Admin, "Administrator"
    return None, None


def _format_remaining_block_time(blocked_until):
    """
    Helper to return a human-readable remaining time string.
    """
    if not blocked_until:
        return "8 hours"
    remaining = blocked_until - datetime.utcnow()
    total_seconds = max(0, int(remaining.total_seconds()))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours > 0:
        return f"{hours} hr {minutes} min"
    return f"{max(1, minutes)} min"


def request_password_reset_otp(role_type, identifier):
    """
    Validates user account, enforces maximum 3 attempts and 8-hour lockout,
    generates 6-digit OTP, stores hashed OTP in DB with 10-minute expiry,
    and dispatches the OTP via email.

    :param role_type: 'student', 'faculty', or 'admin'
    :param identifier: email address (or admin username)
    :return: OtpRequestResult(success: bool, message: str, email: str, blocked: bool, attempts: int)
    """
    if not identifier:
        return OtpRequestResult(False, "Please enter your registered email address.", None)

    clean_id = identifier.strip().lower()
    ModelClass, role_name = _get_user_model_and_role_info(role_type)
    if not ModelClass:
        return OtpRequestResult(False, "Invalid account portal type.", None)

    # Find user record
    if role_type.lower() == 'admin':
        user = ModelClass.query.filter(
            (ModelClass.email == clean_id) | (ModelClass.username == identifier.strip())
        ).first()
    else:
        user = ModelClass.query.filter_by(email=clean_id).first()

    if not user:
        return OtpRequestResult(False, f"No registered {role_name} account found with that email address.", None)

    # Check status if attribute exists
    if hasattr(user, 'status') and user.status != 'Active':
        return OtpRequestResult(False, "Your account is currently inactive. Please contact the college administration.", None)

    user_email = getattr(user, 'email', None)
    if not user_email:
        return OtpRequestResult(False, "No valid email address associated with this account. Please contact Admin.", None)

    now = datetime.utcnow()

    # 1. Check if user is currently blocked for 8 hours
    if getattr(user, 'otp_blocked_until', None):
        if now < user.otp_blocked_until:
            rem_str = _format_remaining_block_time(user.otp_blocked_until)
            return OtpRequestResult(
                False,
                f"Too many OTP attempts (maximum 3 allowed). Password recovery is blocked for 8 hours. Remaining time: {rem_str}.",
                user_email,
                blocked=True,
                attempts=getattr(user, 'otp_attempts', 3)
            )
        else:
            # 8-hour lockout has elapsed! Reset block and attempts
            user.otp_blocked_until = None
            user.otp_attempts = 0
            db.session.commit()

    # 2. Check if user has already reached 3 attempts
    current_attempts = getattr(user, 'otp_attempts', 0) or 0
    if current_attempts >= 3:
        # Lockout for 8 hours
        user.otp_blocked_until = now + timedelta(hours=8)
        db.session.commit()
        return OtpRequestResult(
            False,
            "You have reached the maximum limit of 3 OTP attempts. For security reasons, password recovery is now blocked for 8 hours.",
            user_email,
            blocked=True,
            attempts=3
        )

    try:
        # 3. Increment attempt counter
        new_attempts = current_attempts + 1
        user.otp_attempts = new_attempts

        # If this is the 3rd attempt, lock future OTP requests for 8 hours
        # (user can still use this 3rd OTP within 10 minutes to reset password)
        if new_attempts >= 3:
            user.otp_blocked_until = now + timedelta(hours=8)

        # Generate 6-digit random OTP
        plain_otp = f"{random.randint(100000, 999999)}"

        # Store HASHED OTP in database for high security
        user.reset_otp = generate_password_hash(plain_otp)
        user.otp_expiry = now + timedelta(minutes=10)

        db.session.commit()

        # Send email with plaintext OTP to user
        user_name = getattr(user, 'full_name', role_name)
        mail_sent = send_password_reset_otp_email(
            user_email=user_email,
            user_name=user_name,
            otp=plain_otp,
            role_name=role_name
        )

        if not mail_sent:
            # Revert attempts if dispatch failed
            user.otp_attempts = max(0, current_attempts)
            if new_attempts >= 3:
                user.otp_blocked_until = None
            db.session.commit()
            return OtpRequestResult(
                False,
                "Unable to send email right now. Please check your internet or contact administration.",
                user_email,
                blocked=False,
                attempts=user.otp_attempts
            )

        attempt_info = f"(Attempt {new_attempts} of 3)" if new_attempts < 3 else "(Final Attempt 3 of 3 - Account locked from further OTP requests for 8 hours)"
        return OtpRequestResult(
            True,
            f"A 6-digit verification OTP has been sent to {user_email}. {attempt_info}. It expires in 10 minutes.",
            user_email,
            blocked=(new_attempts >= 3),
            attempts=new_attempts
        )

    except Exception as e:
        db.session.rollback()
        return OtpRequestResult(False, f"System error while generating OTP: {str(e)}", None)


def verify_otp_only(role_type, email, entered_otp):
    """
    Validates entered OTP against stored database hash and verifies expiration.
    Does NOT reset password yet. Used for multi-step verification screen.

    :param role_type: 'student', 'faculty', or 'admin'
    :param email: User's registered email address
    :param entered_otp: Plain 6-digit OTP entered by user
    :return: tuple (success: bool, message: str)
    """
    if not email or not entered_otp:
        return False, "Email address and 6-digit OTP are required."

    clean_email = email.strip().lower()
    clean_otp = str(entered_otp).strip()

    if len(clean_otp) != 6 or not clean_otp.isdigit():
        return False, "Please enter a valid 6-digit numeric OTP."

    ModelClass, role_name = _get_user_model_and_role_info(role_type)
    if not ModelClass:
        return False, "Invalid account portal type."

    user = ModelClass.query.filter_by(email=clean_email).first()
    if not user:
        return False, "Account record not found. Please try again."

    now = datetime.utcnow()

    # If blocked and OTP has expired or doesn't exist, reject
    if getattr(user, 'otp_blocked_until', None) and now < user.otp_blocked_until:
        if not user.reset_otp or not user.otp_expiry or now > user.otp_expiry:
            rem_str = _format_remaining_block_time(user.otp_blocked_until)
            return False, f"Password recovery for this account is blocked for 8 hours. Remaining time: {rem_str}."

    if not user.reset_otp or not user.otp_expiry:
        return False, "No active OTP request found. Please request a new OTP."

    if now > user.otp_expiry:
        user.reset_otp = None
        user.otp_expiry = None
        db.session.commit()
        return False, "Your OTP has expired. Please request a new OTP."

    is_valid_otp = False
    try:
        is_valid_otp = check_password_hash(user.reset_otp, clean_otp)
    except Exception:
        is_valid_otp = (user.reset_otp == clean_otp)

    if not is_valid_otp:
        return False, "Invalid OTP code. Please check and enter the correct 6 digits."

    return True, "OTP verified successfully. You can now set a new password."


def verify_otp_and_reset_password(role_type, email, entered_otp, new_password, confirm_password):
    """
    Validates entered OTP against stored database hash, verifies expiry, and resets password.

    :param role_type: 'student', 'faculty', or 'admin'
    :param email: User's registered email address
    :param entered_otp: Plain 6-digit OTP entered by user
    :param new_password: New password string
    :param confirm_password: Confirmation password string
    :return: tuple (success: bool, message: str)
    """
    if not email or not entered_otp or not new_password:
        return False, "All fields are required. Please fill in all information."

    if new_password != confirm_password:
        return False, "New password and Confirm Password do not match."

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters long."

    clean_email = email.strip().lower()
    clean_otp = str(entered_otp).strip()

    ModelClass, role_name = _get_user_model_and_role_info(role_type)
    if not ModelClass:
        return False, "Invalid account portal type."

    user = ModelClass.query.filter_by(email=clean_email).first()
    if not user:
        return False, "Account record not found. Please try again."

    # Validate OTP existence
    if not user.reset_otp or not user.otp_expiry:
        return False, "No active password reset request found. Please request a new OTP."

    # Validate OTP Expiry
    if datetime.utcnow() > user.otp_expiry:
        # Clear expired OTP
        user.reset_otp = None
        user.otp_expiry = None
        db.session.commit()
        return False, "Your OTP has expired. Please request a new OTP."

    # Validate Hashed OTP
    is_valid_otp = False
    try:
        is_valid_otp = check_password_hash(user.reset_otp, clean_otp)
    except Exception:
        is_valid_otp = (user.reset_otp == clean_otp)

    if not is_valid_otp:
        return False, "Invalid verification OTP. Please check the code and try again."

    # Reset Password securely
    try:
        user.password = generate_password_hash(new_password)
        # Clear reset OTP and expiry, and reset lockout state
        user.reset_otp = None
        user.otp_expiry = None
        user.otp_attempts = 0
        user.otp_blocked_until = None

        if hasattr(user, 'password_changed'):
            # Student uses SmallInteger (0/1), Faculty uses Boolean
            if isinstance(getattr(ModelClass, 'password_changed').type, db.Boolean):
                user.password_changed = True
            else:
                user.password_changed = 1

        db.session.commit()
        return True, "Your password has been reset successfully! Please sign in with your new password."

    except Exception as e:
        db.session.rollback()
        return False, f"Database error while updating password: {str(e)}"
