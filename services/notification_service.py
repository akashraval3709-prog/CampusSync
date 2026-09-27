"""
CampusSync ERP - Notification Service
====================================
File: services/notification_service.py
Handles role-based notifications, category filtering, assignment timelines,
attachment uploads, urgency alerts, and live countdown data.
"""

import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import current_app
from extensions import db
from models import Notification, Subject, FacultySubjectAssignment

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'webp', 'gif',
    'pdf', 'doc', 'docx', 'txt', 'zip'
}

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
DOC_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip'}


def allowed_file(filename):
    """Checks if the uploaded file has a permitted extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    """Determines whether file is an image or document."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    elif ext in DOC_EXTENSIONS:
        return 'document'
    return 'other'


def save_notification_file(file_storage):
    """
    Saves uploaded file to 'uploads/notifications/' with a secure unique filename.
    Returns (saved_filename, file_type) or (None, None) if invalid or empty.
    """
    if not file_storage or file_storage.filename == '':
        return None, None

    if not allowed_file(file_storage.filename):
        return None, None

    upload_dir = os.path.join(current_app.root_path, 'uploads', 'notifications')
    os.makedirs(upload_dir, exist_ok=True)

    original_name = secure_filename(file_storage.filename)
    unique_prefix = uuid.uuid4().hex[:10]
    final_filename = f"{unique_prefix}_{original_name}"
    save_path = os.path.join(upload_dir, final_filename)

    file_storage.save(save_path)
    file_type = get_file_type(final_filename)

    return final_filename, file_type


def parse_datetime(dt_str):
    """Parses datetime from standard HTML datetime-local input (YYYY-MM-DDTHH:MM) or Date (YYYY-MM-DD)."""
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None


def create_notification(title, message, category, posted_by_role,
                        admin_id=None, faculty_id=None, target_audience='All',
                        target_semester=None, target_division='All', subject_id=None,
                        start_date=None, end_date=None, priority='Normal',
                        photo_file=None, file_type=None):
    """Creates a new Notification entry in database."""
    # Convert dates if given as strings
    if isinstance(start_date, str):
        start_date = parse_datetime(start_date)
    if isinstance(end_date, str):
        end_date = parse_datetime(end_date)

    if target_semester in ('', 'All', None):
        target_semester = None
    else:
        try:
            target_semester = int(target_semester)
        except (ValueError, TypeError):
            target_semester = None

    if target_division in ('', 'None', None):
        target_division = 'All'

    if subject_id in ('', 'None', None):
        subject_id = None
    else:
        try:
            subject_id = int(subject_id)
        except (ValueError, TypeError):
            subject_id = None

    notification = Notification(
        title=title.strip(),
        message=message.strip(),
        category=category.strip() if category else 'General',
        photo_file=photo_file,
        file_type=file_type,
        start_date=start_date,
        end_date=end_date,
        posted_by_role=posted_by_role,
        admin_id=admin_id,
        faculty_id=faculty_id,
        target_audience=target_audience,
        target_semester=target_semester,
        target_division=target_division,
        subject_id=subject_id,
        priority=priority if priority in ('Normal', 'Important', 'Urgent') else 'Normal',
        is_active=True
    )

    db.session.add(notification)
    db.session.commit()
    return notification


def get_public_notices(limit=10):
    """Fetches active notifications targeted to Guest or All for the college homepage."""
    return Notification.query.filter(
        Notification.target_audience.in_(['Guest', 'All']),
        Notification.is_active == True
    ).order_by(Notification.created_at.desc()).limit(limit).all()


def get_faculty_notices(filter_by_cycle=True):
    """Fetches active campus notices intended for Faculty or All, filtered by active semester cycle."""
    notices = Notification.query.filter(
        Notification.target_audience.in_(['Faculty', 'All']),
        Notification.is_active == True
    ).order_by(Notification.created_at.desc()).all()

    if not filter_by_cycle:
        return notices

    from services.academic_service import get_active_semesters
    active_sems = get_active_semesters()

    filtered = []
    for n in notices:
        if n.target_semester is not None:
            if n.target_semester in active_sems:
                filtered.append(n)
        elif n.subject and n.subject.semester is not None:
            if n.subject.semester in active_sems:
                filtered.append(n)
        else:
            filtered.append(n)
    return filtered


def get_faculty_created_notices(faculty_id, filter_by_cycle=True):
    """Fetches notices posted by this specific faculty member, filtered by active semester cycle."""
    notices = Notification.query.filter_by(
        faculty_id=faculty_id,
        posted_by_role='Faculty'
    ).order_by(Notification.created_at.desc()).all()

    if not filter_by_cycle:
        return notices

    from services.academic_service import get_active_semesters
    active_sems = get_active_semesters()

    filtered = []
    for n in notices:
        if n.target_semester is not None:
            if n.target_semester in active_sems:
                filtered.append(n)
        elif n.subject and n.subject.semester is not None:
            if n.subject.semester in active_sems:
                filtered.append(n)
        else:
            filtered.append(n)
    return filtered


def get_all_admin_notices(filter_by_cycle=True):
    """Fetches all notices (for Admin management table), filtered by active semester cycle."""
    notices = Notification.query.order_by(Notification.created_at.desc()).all()

    if not filter_by_cycle:
        return notices

    from services.academic_service import get_active_semesters
    active_sems = get_active_semesters()

    filtered = []
    for n in notices:
        if n.target_semester is not None:
            if n.target_semester in active_sems:
                filtered.append(n)
        elif n.subject and n.subject.semester is not None:
            if n.subject.semester in active_sems:
                filtered.append(n)
        else:
            filtered.append(n)
    return filtered


def get_student_notices(student, category=None):
    """
    Fetches all active notices visible to a specific student based on
    their enrolled Semester and Division, strictly filtered by the active semester cycle.
    """
    from services.academic_service import get_active_semesters
    active_sems = get_active_semesters()

    sem = student.semester
    div = student.division

    query = Notification.query.filter(
        Notification.is_active == True,
        db.or_(
            Notification.target_audience == 'All',
            db.and_(
                Notification.target_audience == 'Student',
                db.or_(Notification.target_semester == None, Notification.target_semester == sem),
                db.or_(Notification.target_division == None, Notification.target_division == 'All', Notification.target_division == div)
            )
        )
    )

    if category and category != 'All':
        query = query.filter(Notification.category == category)

    notices = query.order_by(Notification.created_at.desc()).all()

    filtered = []
    for n in notices:
        if n.target_semester is not None:
            if n.target_semester in active_sems:
                filtered.append(n)
        elif n.subject and n.subject.semester is not None:
            if n.subject.semester in active_sems:
                filtered.append(n)
        else:
            filtered.append(n)

    return filtered


def calculate_deadline_info(notice):
    """
    Calculates remaining time, urgency, and countdown flags for a notice.
    Alert starts when 2 days (48 hours) or less remain until end_date.
    """
    if not notice.end_date:
        return {
            'has_deadline': False,
            'is_expired': False,
            'is_urgent': False,
            'total_seconds': 0,
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'seconds': 0,
            'countdown_str': '',
            'end_date_iso': None
        }

    now = datetime.utcnow()
    diff = notice.end_date - now
    total_seconds = int(diff.total_seconds())

    if total_seconds <= 0:
        return {
            'has_deadline': True,
            'is_expired': True,
            'is_urgent': False,
            'total_seconds': 0,
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'seconds': 0,
            'countdown_str': 'Deadline Passed',
            'end_date_iso': notice.end_date.strftime('%Y-%m-%dT%H:%M:%S')
        }

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Urgent alert if 2 days (<= 172800 seconds) or less left
    is_urgent = total_seconds <= (2 * 86400)

    countdown_str = f"{days:02d}d : {hours:02d}h : {minutes:02d}m : {seconds:02d}s Left"

    return {
        'has_deadline': True,
        'is_expired': False,
        'is_urgent': is_urgent,
        'total_seconds': total_seconds,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'countdown_str': countdown_str,
        'end_date_iso': notice.end_date.strftime('%Y-%m-%dT%H:%M:%S')
    }


def get_student_urgent_notices(student):
    """
    Returns active notices for this student that have an active deadline
    with 2 days (48 hours) or less remaining.
    """
    all_notices = get_student_notices(student)
    urgent_items = []
    for notice in all_notices:
        info = calculate_deadline_info(notice)
        if info['has_deadline'] and not info['is_expired'] and info['is_urgent']:
            notice.deadline_info = info
            urgent_items.append(notice)
    return urgent_items


def delete_notification(notification_id, requester_role, requester_id):
    """
    Deletes a notification from DB and removes its attachment file if any.
    Admin can delete any notification.
    Faculty can only delete notifications created by themselves.
    """
    notice = Notification.query.get(notification_id)
    if not notice:
        return False, "Notification not found"

    if requester_role == 'Faculty' and (notice.posted_by_role != 'Faculty' or notice.faculty_id != requester_id):
        return False, "Unauthorized to delete this notification"

    # Remove attachment file if exists
    if notice.photo_file:
        try:
            file_path = os.path.join(current_app.root_path, 'uploads', 'notifications', notice.photo_file)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            current_app.logger.warning(f"Could not remove notification file: {e}")

    db.session.delete(notice)
    db.session.commit()
    return True, "Notification deleted successfully"


def toggle_notification_status(notification_id):
    """Toggles active/inactive status of a notification (Admin only)."""
    notice = Notification.query.get(notification_id)
    if not notice:
        return False, "Notification not found"

    notice.is_active = not notice.is_active
    db.session.commit()
    return True, f"Notification marked as {'Active' if notice.is_active else 'Inactive'}"
