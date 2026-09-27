"""
CampusSync ERP - Common Helper Functions
========================================
File: utils/helpers.py
"""

from datetime import datetime
from models import Student

INSTITUTE_CODE = "152"

def generate_roll_number(semester=None, academic_year=None, course=None):
    """
    Finds highest existing numeric roll_number for a given batch scope
    (academic_year + course + semester) and returns the next roll number as a string.
    Roll numbers restart from 1 when a new batch/semester starts.
    """
    query = Student.query

    if semester is not None:
        query = query.filter(Student.semester == semester)
    if course:
        query = query.filter(Student.course == course)
    if academic_year:
        query = query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))

    students = query.all()
    max_roll = 0

    for s in students:
        try:
            num = int(s.roll_number)
            if num > max_roll:
                max_roll = num
        except (ValueError, TypeError):
            continue

    candidate = max_roll + 1

    # Guarantee uniqueness by checking if candidate roll number already exists in this scope
    check_query = Student.query
    if semester is not None:
        check_query = check_query.filter(Student.semester == semester)
    if course:
        check_query = check_query.filter(Student.course == course)
    if academic_year:
        check_query = check_query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))

    while check_query.filter(Student.roll_number == str(candidate)).first():
        candidate += 1

    return str(candidate)

def generate_enrollment_no(course):
    """
    Auto-generate Enrollment Number
    Format: BCA15224000001
      -> Course Code (3 chars) + Institute Code (3 digits) + Year (2 digits) + Sequence (6 digits)
    """
    course_code = ''.join(course.split()).upper().replace('.', '')[:3] if course else 'GEN'
    year_suffix = str(datetime.utcnow().year)[-2:]
    prefix = f"{course_code}{INSTITUTE_CODE}{year_suffix}"

    existing_count = Student.query.filter(
        Student.enrollment_no.like(f"{prefix}%")
    ).count()

    seq = existing_count + 1
    candidate = f"{prefix}{seq:06d}"

    while Student.query.filter_by(enrollment_no=candidate).first():
        seq += 1
        candidate = f"{prefix}{seq:06d}"

    return candidate

def calculate_division_from_roll(roll_number, students_per_division=70):
    """
    Generates division letter ('A', 'B', 'C', etc.) based on numeric roll_number
    and students_per_division limit.
    """
    try:
        roll_num = int(roll_number)
        limit = int(students_per_division) if students_per_division and int(students_per_division) > 0 else 70
        if roll_num <= 0:
            return 'A'
        idx = (roll_num - 1) // limit
        if idx < 26:
            return chr(ord('A') + idx)
        else:
            first = chr(ord('A') + (idx // 26) - 1)
            second = chr(ord('A') + (idx % 26))
            return f"{first}{second}"
    except (ValueError, TypeError):
        return 'A'

