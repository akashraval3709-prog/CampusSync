"""
CampusSync ERP - Authentication Service
======================================
File: services/auth_service.py
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin
from extensions import db

def authenticate_admin(username, password):
    """
    Handles Admin Login authentication logic using SQLAlchemy ORM.
    1. Fetches admin by username via Admin.query.
    2. Verifies hashed password using check_password_hash() (with plain text fallback).
    3. Auto-upgrades password hash if needed.
    4. Updates last_login timestamp in database.
    5. Returns Admin instance if valid, None otherwise.
    """
    admin = Admin.query.filter_by(username=username).first()

    is_valid_password = False
    if admin:
        try:
            is_valid_password = check_password_hash(admin.password, password)
        except Exception:
            # Fallback in case stored password is plain text
            is_valid_password = (admin.password == password)

    if admin and is_valid_password and admin.status == 'Active':
        # Auto-upgrade plain text password to Werkzeug hash if needed
        if not admin.password.startswith(('scrypt:', 'pbkdf2:', 'argon2:')):
            admin.password = generate_password_hash(password)

        # Update last_login timestamp in database
        admin.last_login = datetime.utcnow()
        db.session.commit()
        return admin

    return None

def get_admin_by_id(admin_id):
    """Fetches Admin record by ID."""
    return Admin.query.get(admin_id)

def update_admin_profile(admin_id, full_name, email, mobile, profile_photo_filename=None):
    """
    Updates Admin profile details (Full Name, Email, Mobile, Profile Photo).
    Returns (updated_admin, None) on success or (None, error_message) on failure.
    """
    admin = Admin.query.get(admin_id)
    if not admin:
        return None, "Admin user not found."

    # Check for duplicate email (if changed)
    if email and email != admin.email:
        existing = Admin.query.filter_by(email=email).first()
        if existing and existing.id != admin_id:
            return None, "Email address is already in use by another account."

    admin.full_name = full_name
    admin.email = email
    admin.mobile = mobile

    if profile_photo_filename:
        admin.profile_photo = profile_photo_filename

    try:
        db.session.commit()
        return admin, None
    except Exception as e:
        db.session.rollback()
        return None, f"Database update error: {str(e)}"

def change_admin_password(admin_id, current_password, new_password):
    """
    Verifies current password and updates password with a new Werkzeug hash.
    Returns (True, success_message) or (False, error_message).
    """
    admin = Admin.query.get(admin_id)
    if not admin:
        return False, "Admin user not found."

    # Verify current password
    is_valid = False
    try:
        is_valid = check_password_hash(admin.password, current_password)
    except Exception:
        is_valid = (admin.password == current_password)

    if not is_valid:
        return False, "Current password is incorrect."

    # Hash new password and save
    admin.password = generate_password_hash(new_password)

    try:
        db.session.commit()
        return True, "Password updated successfully."
    except Exception as e:
        db.session.rollback()
        return False, f"Database error while saving password: {str(e)}"
