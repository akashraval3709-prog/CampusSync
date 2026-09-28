"""
CampusSync ERP - OTP Email Helper
==================================
File: mail/otp_mail.py

Sends secure HTML Password Reset OTP emails to Students, Faculty, and Administrators
via Flask-Mail and configured SMTP credentials.
"""

import os
import logging
import threading
from flask import render_template, current_app
from flask_mail import Message
from extensions import mail
from services.college_service import get_college_settings

logger = logging.getLogger(__name__)


def _dispatch_mail_in_background(app_obj, msg, recipient_email, role_name, subject=None, html_body=None, text_body=None, sender=None, college_name=None):
    """
    Background worker function that sends email asynchronously
    without blocking the user's web browser or HTTP response.
    Supports Brevo HTTPS REST API with seamless SMTP fallback.
    """
    with app_obj.app_context():
        try:
            from mail.brevo_service import is_brevo_configured, send_brevo_email
            if is_brevo_configured() and html_body and subject:
                success, info = send_brevo_email(
                    to_email=recipient_email,
                    subject=subject,
                    html_content=html_body,
                    text_content=text_body,
                    sender_email=sender,
                    sender_name=college_name
                )
                if success:
                    logger.info(f"SUCCESS: Background OTP delivered via Brevo to {recipient_email} ({role_name})")
                    return
                else:
                    logger.warning(f"Brevo OTP dispatch failed: {info}. Falling back to standard SMTP...")

            mail.send(msg)
            logger.info(f"SUCCESS: Background OTP email delivered to {recipient_email} ({role_name}) via SMTP")
        except Exception as e:
            logger.error(f"ERROR: Background email delivery failed for {recipient_email}: {str(e)}")
            print(f"[Async OTP Mail Error] Failed to send to {recipient_email}: {e}")


def send_password_reset_otp_email(user_email, user_name, otp, role_name="User"):
    """
    Dispatches a branded HTML OTP email for password reset.
    Runs asynchronously in a background thread for INSTANT response time (< 50ms).
    
    :param user_email: Recipient email address
    :param user_name: Recipient full name
    :param otp: Plain 6-digit OTP string to display in the email
    :param role_name: Role display string (e.g. 'Student', 'Faculty', 'Admin')
    :return: True on success, False on error
    """
    if not user_email:
        logger.error("Failed to send OTP email: Recipient email is missing.")
        return False

    try:
        college = get_college_settings()
        college_name = college.college_name if college and college.college_name else "CampusSync College"
        subject = f"Your Password Reset OTP - {college_name}"

        # Resolve sender email
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'devidparmar8954@gmail.com')

        # Render clean text-first HTML template
        html_body = render_template(
            'emails/password_reset_otp.html',
            user_name=user_name or role_name,
            role_name=role_name,
            otp=otp,
            college=college
        )

        # Plain text fallback
        text_body = f"""Hello {user_name or role_name},

We received a request to reset the password for your {role_name} account on {college_name}.

Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 10 minutes only. Please do not share this OTP with anyone.

If you did not request a password reset, please ignore this email.

Regards,
{college_name} - CampusSync ERP
"""

        # Construct Message (Zero image attachments for lightning-fast delivery)
        msg = Message(
            subject=subject,
            recipients=[user_email.strip()],
            body=text_body,
            html=html_body,
            sender=sender
        )

        # Send ASYNCHRONOUSLY in a background thread (instant response to frontend!)
        app_obj = current_app._get_current_object()
        worker_thread = threading.Thread(
            target=_dispatch_mail_in_background,
            args=(app_obj, msg, user_email, role_name, subject, html_body, text_body, sender, college_name),
            daemon=True
        )
        worker_thread.start()

        logger.info(f"Background OTP email thread spawned for {user_email}")
        return True

    except Exception as e:
        logger.error(f"ERROR: Failed to prepare OTP email for {user_email}: {str(e)}")
        print(f"[OTP Mail Error] Could not prepare email: {e}")
        return False

