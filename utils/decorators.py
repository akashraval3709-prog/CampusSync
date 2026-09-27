"""
CampusSync ERP - Session & Authentication Protection Decorators
===============================================================
File: utils/decorators.py
"""

from functools import wraps
from flask import session, redirect, url_for, request, flash
from models import Faculty

def admin_required(f):
    """
    Decorator to protect admin routes.
    Ensures 'admin_id' exists in session; redirects to admin login if absent.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def faculty_required(f):
    """
    Decorator to protect faculty routes.
    1. Checks whether 'faculty_id' exists in session.
    2. Fetches faculty from database using session['faculty_id'].
    3. Verifies faculty exists and status is 'Active'.
    4. Enforces first-login password change if password_changed is False.
    5. Redirects to faculty login if unauthenticated or inactive.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        faculty_id = session.get("faculty_id")
        if not faculty_id:
            return redirect(url_for('faculty_login'))

        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            session.pop("faculty_id", None)
            return redirect(url_for('faculty_login'))

        if faculty.status != 'Active':
            session.pop("faculty_id", None)
            flash("Your faculty account is currently inactive. Please contact the administrator.", "danger")
            return redirect(url_for('faculty_login'))

        # If faculty hasn't changed default password, force redirection to change-password
        if not faculty.password_changed:
            allowed_endpoints = [
                'faculty.faculty_change_password',
                'faculty_change_password',
                'faculty.faculty_logout',
                'faculty_logout'
            ]
            if request.endpoint not in allowed_endpoints:
                flash("For security, please change your default password before continuing.", "warning")
                return redirect(url_for('faculty_change_password'))

        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Decorator to protect student routes.
    Ensures 'student_id' exists in session; redirects to student login if absent.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

