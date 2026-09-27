"""
CampusSync ERP - Validation Functions
=====================================
File: utils/validators.py
"""

from datetime import datetime

def validate_student_input(data):
    """
    Server-side validation for student form data.
    Returns tuple: (parsed_data_dict, errors_dict)
    """
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    mobile = (data.get('mobile') or '').strip()
    dob_raw = data.get('dob')
    course = (data.get('course') or '').strip()
    semester = data.get('semester')
    division = (data.get('division') or '').strip()
    academic_year = (data.get('academic_year') or '').strip()

    errors = {}

    if not full_name or len(full_name) < 3:
        errors['full_name'] = "Full name must be at least 3 characters."
    elif not all(c.isalpha() or c.isspace() for c in full_name):
        errors['full_name'] = "Only alphabets and spaces allowed."

    if not email or '@' not in email or '.' not in email:
        errors['email'] = "Enter a valid email address."

    if not mobile or not mobile.isdigit() or len(mobile) != 10:
        errors['mobile'] = "Mobile number must be exactly 10 digits."

    if not course:
        errors['course'] = "Please select a course."

    parsed_semester = None
    if not semester:
        errors['semester'] = "Please select a semester."
    else:
        try:
            parsed_semester = int(semester)
            if not (1 <= parsed_semester <= 8):
                errors['semester'] = "Semester must be between 1 and 8."
        except (ValueError, TypeError):
            errors['semester'] = "Invalid semester value."

    if not division:
        errors['division'] = "Please select a division."

    if not academic_year:
        from services.academic_service import get_academic_settings
        curr_academic = get_academic_settings()
        academic_year = (curr_academic.academic_year if curr_academic and curr_academic.academic_year else '2026-27').strip()
    elif len(academic_year) > 20:
        errors['academic_year'] = "Academic Year cannot exceed 20 characters."

    parsed_dob = None
    if dob_raw:
        try:
            parsed_dob = datetime.strptime(dob_raw, '%Y-%m-%d').date()
            if parsed_dob >= datetime.utcnow().date():
                errors['dob'] = "Date of birth must be in the past."
        except ValueError:
            errors['dob'] = "Invalid date format. Use YYYY-MM-DD."

    parsed_data = {
        'full_name': full_name,
        'email': email,
        'mobile': mobile,
        'dob': parsed_dob,
        'course': course,
        'semester': parsed_semester,
        'division': division,
        'academic_year': academic_year
    }

    return parsed_data, errors
