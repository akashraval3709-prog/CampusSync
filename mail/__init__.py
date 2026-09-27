"""
CampusSync ERP Email Module
===========================
Exports reusable email helper functions for the application.
"""

from .student_mail import send_student_welcome_email
from .otp_mail import send_password_reset_otp_email

__all__ = ['send_student_welcome_email', 'send_password_reset_otp_email']
