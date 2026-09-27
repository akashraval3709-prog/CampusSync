"""
CampusSync ERP - Student Email Helper
=====================================
File: mail/student_mail.py

Provides reusable functions for rendering HTML email templates and dispatching
transactional emails to students via Flask-Mail and SMTP.
"""

import os
import logging
from flask import render_template, current_app, url_for
from flask_mail import Message
from extensions import mail
from services.college_service import get_college_settings

# Configure logger for email operation tracking and debugging
logger = logging.getLogger(__name__)


def send_student_welcome_email(student, password=None, login_url=None):
    """
    Sends a professional HTML welcome email with portal credentials to a newly inserted Student.
    """
    # 1. Basic validation: Ensure student object and recipient email exist
    if not student or not getattr(student, 'email', None):
        logger.error("Failed to send welcome email: Invalid student object or missing email address.")
        return False

    try:
        # Fetch dynamic college settings
        college = get_college_settings()

        # 2. Extract student attributes with safe fallbacks
        student_name = getattr(student, 'full_name', 'Student')
        recipient_email = student.email
        enrollment_number = getattr(student, 'enrollment_no', 'N/A')
        roll_number = getattr(student, 'roll_number', 'N/A')
        division = getattr(student, 'division', 'N/A')
        
        # Username / Email is student's email address
        username = recipient_email

        # Retrieve password from passed argument, model attribute, or fallback
        if not password:
            password = getattr(student, 'raw_password', getattr(student, 'password', 'N/A'))

        # Resolve login portal URL
        if not login_url:
            try:
                login_url = url_for('student_login', _external=True)
            except Exception:
                login_url = "https://campussync.bkmbca.ac.in/student/login"

        # 3. Configure Email Subject, Sender & Logo URL
        college_name = college.college_name if college else "BKM BCA College"
        subject = f"Welcome to {college_name} - CampusSync Student Portal"
        
        # Sender email from config or default devidparmar8954@gmail.com
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'devidparmar8954@gmail.com')

        # Resolve College Logo path (check uploaded logo first, then static logo)
        logo_path = None
        if college and college.logo and college.logo != 'default-logo.png':
            uploaded_logo = os.path.join(current_app.root_path, 'uploads', 'college', college.logo)
            if os.path.exists(uploaded_logo):
                logo_path = uploaded_logo

        if not logo_path:
            static_logo = os.path.join(current_app.root_path, 'static', 'images', 'college_logo.png')
            if os.path.exists(static_logo):
                logo_path = static_logo

        logo_url = None

        # 4. Render HTML email template using Jinja2
        html_body = render_template(
            'emails/student_welcome.html',
            student=student,
            student_name=student_name,
            username=username,
            password=password,
            roll_number=roll_number,
            enrollment_number=enrollment_number,
            division=division,
            login_url=login_url,
            logo_url=logo_url,
            college=college
        )

        # 5. Fallback plain text version
        support_email = college.email if college and college.email else "support@bkmbca.ac.in"
        support_phone = college.phone if college and college.phone else "+91 XXXXX XXXXX"
        college_web = college.website if college and college.website else "https://campussync.bkmbca.ac.in"

        text_body = f"""Hello {student_name},

Welcome to {college_name}.
Your student account has been created successfully.

Below are your login credentials:
------------------------------------------------
Enrollment Number : {enrollment_number}
Roll Number       : {roll_number}
Division          : {division}
Student Name      : {student_name}
Username / Email  : {username}
Temporary Password: {password}
------------------------------------------------

Login to Student Portal:
{login_url}

Important Information:
✔ Change your password after first login.
✔ Never share your password.
✔ Keep your account secure.
✔ Contact college administrator if login fails.

Need Help:
Email  : {support_email}
Phone  : {support_phone}
Website: {college_web}

© 2026 {college_name} - CampusSync ERP
Student Management System
This is an automated email. Please do not reply.
"""

        # 6. Create Flask-Mail Message object
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=text_body,
            html=html_body,
            sender=sender
        )

        # Attach College Logo inline as CID for instant rendering in email clients
        if logo_path and os.path.exists(logo_path):
            ext = os.path.splitext(logo_path)[1].lower()
            mime_type = 'image/png'
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.gif':
                mime_type = 'image/gif'
            elif ext == '.webp':
                mime_type = 'image/webp'

            with open(logo_path, 'rb') as logo_file:
                msg.attach(
                    filename=os.path.basename(logo_path),
                    content_type=mime_type,
                    data=logo_file.read(),
                    headers={'Content-ID': '<college_logo>'}
                )


        # 7. Dispatch email via SMTP server
        mail.send(msg)
        logger.info(f"SUCCESS: Welcome email sent to {recipient_email} (Enrollment: {enrollment_number})")
        return True

    except Exception as e:
        # Handle any SMTP or template rendering exception gracefully without crashing the loop
        logger.error(f"ERROR: Failed to send welcome email to {getattr(student, 'email', 'Unknown')}. Exception: {str(e)}")
        print(f"[Mail Error] Could not send email to {getattr(student, 'email', 'Unknown')}: {e}")
        return False
