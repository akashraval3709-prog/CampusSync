"""
CampusSync ERP - Email Service
==============================
File: services/email_service.py

Provides services for creating email delivery logs, managing asynchronous 
background email dispatching, tracking delivery statuses (PENDING, SENDING, SENT, FAILED),
and handling single & bulk retries.
"""

import threading
import logging
from datetime import datetime
from flask import current_app

from extensions import db
from models import Student, EmailLog
from mail.student_mail import send_student_welcome_email

logger = logging.getLogger(__name__)


def create_email_log(student_id, recipient_email, email_type='WELCOME'):
    """
    Creates a PENDING email tracking log record in database.
    Returns the created EmailLog instance.
    """
    log_entry = EmailLog(
        student_id=student_id,
        recipient_email=recipient_email,
        email_type=email_type,
        status='PENDING',
        retry_count=0
    )
    db.session.add(log_entry)
    db.session.flush()
    return log_entry


def _background_send_email_queue(app_obj, item_list):
    """
    Background worker thread function.
    item_list is a list of tuples: (student_id, email_log_id, plain_pwd)
    Runs safely inside app_context without sharing SQLAlchemy objects across threads.
    """
    with app_obj.app_context():
        logger.info(f"[Email Background Worker] Starting dispatch of {len(item_list)} emails...")
        for student_id, log_id, plain_pwd in item_list:
            try:
                email_log = db.session.get(EmailLog, log_id)
                student = db.session.get(Student, student_id)

                if not email_log or not student:
                    logger.error(f"[Email Background Worker] Log ID {log_id} or Student ID {student_id} not found.")
                    continue

                # Set status to SENDING
                email_log.status = 'SENDING'
                email_log.updated_at = datetime.utcnow()
                db.session.commit()

                # Dispatch email via student_mail helper
                success = send_student_welcome_email(student, password=plain_pwd)

                if success:
                    email_log.status = 'SENT'
                    email_log.sent_at = datetime.utcnow()
                    email_log.error_message = None
                    logger.info(f"[Email Background Worker] SUCCESS: Email sent to {email_log.recipient_email} (Log ID: {log_id})")
                else:
                    email_log.status = 'FAILED'
                    email_log.error_message = "SMTP delivery failed or template rendering error."
                    logger.warning(f"[Email Background Worker] FAILED: Could not send email to {email_log.recipient_email} (Log ID: {log_id})")

                email_log.updated_at = datetime.utcnow()
                db.session.commit()

            except Exception as err:
                db.session.rollback()
                logger.error(f"[Email Background Worker] Exception for log ID {log_id}: {err}")
                try:
                    email_log = db.session.get(EmailLog, log_id)
                    if email_log:
                        email_log.status = 'FAILED'
                        email_log.error_message = str(err)
                        email_log.updated_at = datetime.utcnow()
                        db.session.commit()
                except Exception as log_err:
                    db.session.rollback()
                    logger.error(f"[Email Background Worker] Failed to update error status for log {log_id}: {log_err}")

        logger.info("[Email Background Worker] Finished sending background welcome emails.")


def dispatch_background_emails(item_list):
    """
    Spawns a daemon thread to process email queue in the background asynchronously.
    item_list: list of tuples (student_id, email_log_id, plain_pwd)
    """
    if not item_list:
        return
    try:
        app_obj = current_app._get_current_object()
        thread = threading.Thread(
            target=_background_send_email_queue,
            args=(app_obj, item_list),
            daemon=True
        )
        thread.start()
    except Exception as e:
        logger.error(f"[Email Service Error] Failed to launch background email thread: {e}")


def get_all_email_logs():
    """
    Returns list of all email logs formatted for admin UI display.
    Joined with Student record to retrieve student_name.
    """
    logs = db.session.query(EmailLog, Student.full_name).outerjoin(
        Student, EmailLog.student_id == Student.id
    ).order_by(EmailLog.id.desc()).all()

    result = []
    for log, full_name in logs:
        result.append({
            "id": log.id,
            "student_id": log.student_id,
            "student_name": full_name or "N/A",
            "recipient_email": log.recipient_email,
            "email_type": log.email_type,
            "status": log.status,
            "error_message": log.error_message,
            "sent_at": log.sent_at.strftime("%Y-%m-%d %H:%M:%S") if log.sent_at else None,
            "retry_count": log.retry_count,
            "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else None,
            "updated_at": log.updated_at.strftime("%Y-%m-%d %H:%M:%S") if log.updated_at else None
        })
    return result


def retry_single_email(log_id):
    """
    Retries sending a single FAILED email in the background.
    Returns (success, message, status_code).
    """
    email_log = db.session.get(EmailLog, log_id)
    if not email_log:
        return False, "Email log record not found.", 404

    if email_log.status != 'FAILED':
        return False, f"Only FAILED emails can be retried. Current status is '{email_log.status}'.", 400

    student = db.session.get(Student, email_log.student_id)
    if not student:
        return False, "Associated student record no longer exists.", 404

    plain_pwd = student.mobile if student.mobile else '0000000000'

    email_log.status = 'SENDING'
    email_log.retry_count += 1
    email_log.updated_at = datetime.utcnow()
    db.session.commit()

    dispatch_background_emails([(student.id, email_log.id, plain_pwd)])
    return True, "Email retry has been started in the background.", 200


def retry_all_failed_emails():
    """
    Retries ALL failed emails in the background.
    Returns (success, message, status_code).
    """
    failed_logs = EmailLog.query.filter_by(status='FAILED').all()
    if not failed_logs:
        return False, "No FAILED emails found to retry.", 400

    items_to_dispatch = []
    for log in failed_logs:
        student = db.session.get(Student, log.student_id)
        if not student:
            continue
        plain_pwd = student.mobile if student.mobile else '0000000000'
        log.status = 'SENDING'
        log.retry_count += 1
        log.updated_at = datetime.utcnow()
        items_to_dispatch.append((student.id, log.id, plain_pwd))

    if not items_to_dispatch:
        return False, "No valid failed emails could be prepared for retry.", 400

    db.session.commit()

    dispatch_background_emails(items_to_dispatch)
    return True, f"Bulk retry started for {len(items_to_dispatch)} failed emails in the background.", 200
