"""
CampusSync ERP - Excel Import Service
====================================
File: services/excel_service.py
"""

import threading
import openpyxl
from datetime import datetime
from datetime import datetime as dt
from werkzeug.security import generate_password_hash
from flask import current_app

from models import Student
from extensions import db
from utils.helpers import generate_roll_number, generate_enrollment_no, calculate_division_from_roll
from mail import send_student_welcome_email
from services.college_service import get_college_settings
from services.academic_service import get_academic_settings, get_active_semesters



def process_excel_student_import(file_storage, selected_semester=1):
    """
    Reads Excel file via openpyxl, validates headers and rows.
    Expected headers:
    full_name | email | mobile | dob

    Auto-generates:
    - course (from active College Settings)
    - academic_year (from active Academic Settings)
    - semester (from Admin selected_semester)
    - roll_number (batch-scoped by academic_year + course)
    - division (calculated from roll_number and students_per_division limit)
    - enrollment_no (globally sequential)
    - password (hashed version of original mobile number)

    Database commit is executed first. Welcome emails are dispatched asynchronously in the background.
    If DB commit fails, transaction is rolled back and no emails are sent.
    """
    try:
        wb = openpyxl.load_workbook(file_storage, data_only=True)
        sheet = wb.active
    except Exception as e:
        return {"message": f"Invalid Excel file. Details: {e}"}, 400

    # Ensure selected_semester is valid integer between 1 and 8
    try:
        target_semester = int(selected_semester)
        if not (1 <= target_semester <= 8):
            target_semester = 1
    except (ValueError, TypeError):
        target_semester = 1

    # Required Excel headers exactly:
    expected_headers = [
        "full_name",
        "email",
        "mobile",
        "dob"
    ]

    rows = list(sheet.iter_rows(min_row=1, values_only=True))

    if not rows:
        return {"message": "Excel file is empty."}, 400

    # Extract non-empty header values from row 0
    raw_header_values = [h for h in rows[0] if h is not None and str(h).strip() != '']
    header_row = [str(h).strip().lower() for h in raw_header_values]

    if header_row != expected_headers:
        return {
            "message": f"Invalid Excel format. Expected columns: {', '.join(expected_headers)}"
        }, 400

    # Fetch active College & Academic settings automatically
    college = get_college_settings()
    course_name = (college.college_type if college and college.college_type else 'BCA').strip()

    academic = get_academic_settings()
    active_semesters = get_active_semesters(academic.semester_cycle if academic else 'Odd')
    if target_semester not in active_semesters:
        cycle_name = academic.semester_cycle if academic else 'Odd'
        allowed_str = ', '.join([f"Semester {s}" for s in active_semesters])
        return {
            "success": False,
            "message": f"Cannot import students into Semester {target_semester}. Current academic cycle is '{cycle_name}', which only permits {allowed_str}."
        }, 400

    academic_year_val = (academic.academic_year if academic and academic.academic_year else '2026-27').strip()
    students_per_div = getattr(academic, 'students_per_division', 70) or 70

    valid_rows = []
    errors = []
    skipped_count = 0

    seen_emails = set()
    seen_mobiles = set()

    for idx, row in enumerate(rows[1:], start=2):
        if not row or all(v is None for v in row):
            continue

        full_name = row[0] if len(row) > 0 else None
        email = row[1] if len(row) > 1 else None
        mobile = row[2] if len(row) > 2 else None
        dob = row[3] if len(row) > 3 else None

        if not full_name or not email:
            errors.append(f"Row {idx}: Missing required fields (full_name/email).")
            skipped_count += 1
            continue

        full_name = str(full_name).strip()
        email = str(email).strip().lower()

        if '@' not in email or '.' not in email:
            errors.append(f"Row {idx}: Invalid email format ({email}).")
            skipped_count += 1
            continue

        # Check duplicate email in uploaded Excel file
        if email in seen_emails:
            errors.append(f"Row {idx}: Duplicate email ({email}) found within uploaded Excel file.")
            skipped_count += 1
            continue

        # Check duplicate email in database
        if Student.query.filter_by(email=email).first():
            errors.append(f"Row {idx}: Duplicate email ({email}) already exists in system.")
            skipped_count += 1
            continue

        mobile_clean = str(mobile).strip() if mobile is not None else None
        if mobile_clean:
            if mobile_clean.endswith('.0'):
                mobile_clean = mobile_clean[:-2]
            if not mobile_clean.isdigit() or len(mobile_clean) != 10:
                errors.append(f"Row {idx}: Invalid mobile number ({mobile}). Must be 10 digits.")
                skipped_count += 1
                continue

            # Check duplicate mobile in uploaded Excel file
            if mobile_clean in seen_mobiles:
                errors.append(f"Row {idx}: Duplicate mobile number ({mobile_clean}) found within uploaded Excel file.")
                skipped_count += 1
                continue

            # Check duplicate mobile in database
            if Student.query.filter_by(mobile=mobile_clean).first():
                errors.append(f"Row {idx}: Duplicate mobile number ({mobile_clean}) already exists in system.")
                skipped_count += 1
                continue

        parsed_dob = None
        if dob is not None and str(dob).strip():
            if isinstance(dob, datetime):
                parsed_dob = dob.date()
            else:
                try:
                    parsed_dob = dt.strptime(str(dob).strip(), '%Y-%m-%d').date()
                except ValueError:
                    try:
                        parsed_dob = dt.strptime(str(dob).strip(), '%d-%m-%Y').date()
                    except ValueError:
                        errors.append(f"Row {idx}: Invalid DOB format ({dob}). Use YYYY-MM-DD.")
                        skipped_count += 1
                        continue

        # Mark email & mobile as seen for this batch
        seen_emails.add(email)
        if mobile_clean:
            seen_mobiles.add(mobile_clean)

        valid_rows.append({
            "full_name": full_name,
            "email": email,
            "mobile": mobile_clean,
            "dob": parsed_dob
        })

    if not valid_rows:
        return {
            "message": f"No valid rows to import. {skipped_count} skipped.",
            "added": 0, "skipped": skipped_count, "errors": errors
        }, 400

    # Sort all valid Excel students by full_name ascending A-Z before assigning roll numbers
    valid_rows.sort(key=lambda r: r["full_name"].lower())

    added_count = 0
    created_students = []

    # Get starting roll number for (academic_year + course) batch
    next_roll_num = int(
        generate_roll_number(
            academic_year=academic_year_val,
            course=course_name
        )
    )

    for student_data in valid_rows:
        roll_number = str(next_roll_num)
        next_roll_num += 1

        # Generate division automatically using roll_number and students_per_division limit
        auto_division = calculate_division_from_roll(roll_number, students_per_division=students_per_div)

        # Generate enrollment number automatically
        enrollment_no = generate_enrollment_no(course_name)

        # Temporary password is student's original mobile number (stored hashed only)
        original_mobile = student_data["mobile"] if student_data["mobile"] else '0000000000'
        hashed_password = generate_password_hash(original_mobile)

        new_student = Student(
            roll_number=roll_number,
            enrollment_no=enrollment_no,
            full_name=student_data["full_name"],
            email=student_data["email"],
            mobile=student_data["mobile"],
            dob=student_data["dob"],
            course=course_name,
            semester=target_semester,
            division=auto_division,
            academic_year=academic_year_val,
            password=hashed_password,
            status='Active',
            password_changed=0
        )
        db.session.add(new_student)
        db.session.flush()

        created_students.append((new_student, original_mobile))
        added_count += 1

    # Database commit & Rollback safety for student records
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"message": f"Database error: {e}"}, 500

    # Create EmailLog records for newly created students AFTER student DB commit
    if created_students:
        try:
            from services.email_service import create_email_log, dispatch_background_emails
            email_dispatch_items = []
            for student_obj, plain_pwd in created_students:
                log_entry = create_email_log(student_obj.id, student_obj.email, email_type='WELCOME')
                email_dispatch_items.append((student_obj.id, log_entry.id, plain_pwd))
            db.session.commit()

            # Launch background thread AFTER email logs are committed
            dispatch_background_emails(email_dispatch_items)
        except Exception as email_log_err:
            print(f"[Excel Service Error] Error setting up email logs: {email_log_err}")

    message = f"Students imported successfully. {added_count} students added (Semester: {target_semester}, Course: '{course_name}', Academic Year: '{academic_year_val}', auto-generated Roll/Enrollment/Division). Welcome emails are being sent in the background."
    if errors:
        message += f" First issue: {errors[0]}"

    return {
        "success": True,
        "message": message,
        "added": added_count,
        "skipped": skipped_count,
        "errors": errors
    }, 200
