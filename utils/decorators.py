"""
CampusSync ERP - Session & Authentication Protection Decorators
===============================================================
File: utils/decorators.py
"""

from functools import wraps
from flask import session, redirect, url_for, request, flash, jsonify
from models import Faculty

def _is_api_or_ajax_request():
    """Detects whether current request expects JSON response."""
    if request.path.startswith(('/api/', '/admin/api/', '/faculty/api/', '/student/api/')):
        return True
    if request.is_json:
        return True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    best = request.accept_mimetypes.best
    if best and 'application/json' in best and 'text/html' not in best:
        return True
    return False


def admin_required(f):
    """
    Decorator to protect admin routes.
    Ensures 'admin_id' exists in session; returns 401 JSON for APIs, redirects to admin login for pages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            if _is_api_or_ajax_request():
                return jsonify({"success": False, "message": "Admin session expired. Please refresh and log in again."}), 401
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
    5. Returns 401 JSON for APIs or redirects to faculty login if unauthenticated or inactive.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        faculty_id = session.get("faculty_id")
        if not faculty_id:
            if _is_api_or_ajax_request():
                return jsonify({"success": False, "message": "Faculty session expired. Please refresh and log in again."}), 401
            return redirect(url_for('faculty_login'))

        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            session.pop("faculty_id", None)
            if _is_api_or_ajax_request():
                return jsonify({"success": False, "message": "Faculty account not found. Please log in again."}), 401
            return redirect(url_for('faculty_login'))

        if faculty.status != 'Active':
            session.pop("faculty_id", None)
            if _is_api_or_ajax_request():
                return jsonify({"success": False, "message": "Your faculty account is inactive."}), 403
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
                if _is_api_or_ajax_request():
                    return jsonify({"success": False, "message": "Please change default password first."}), 403
                flash("For security, please change your default password before continuing.", "warning")
                return redirect(url_for('faculty_change_password'))

        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Decorator to protect student routes.
    Ensures 'student_id' exists in session; returns 401 JSON for APIs, redirects to student login for pages.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            if _is_api_or_ajax_request():
                return jsonify({"success": False, "message": "Student session expired. Please refresh and log in again."}), 401
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

