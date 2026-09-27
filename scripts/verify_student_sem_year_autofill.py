"""
CampusSync - Verification Test: Student Semester to Academic Year Auto-Fill
===========================================================================
File: scripts/verify_student_sem_year_autofill.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, AcademicSetting
from services.student_service import create_student
from utils.validators import validate_student_input

def python_calculate_academic_year(sem_value, base_academic_year):
    """Mirroring the JavaScript calculateAcademicYearForSemester logic in student_form.js"""
    if not sem_value or not base_academic_year:
        return base_academic_year or "2026-27"
    start_year = int(base_academic_year.split('-')[0])
    sem = int(sem_value)
    if sem in (1, 2):
        offset = 0
    elif sem in (3, 4):
        offset = 1
    elif sem in (5, 6):
        offset = 2
    else:
        offset = 0

    calc_start = start_year - offset
    calc_end = calc_start + 1
    return f"{calc_start}-{str(calc_end)[-2:]}"

def test_autofill_logic():
    print("=" * 60)
    print("TEST: SEMESTER-BASED ACADEMIC YEAR AUTO-CALCULATION")
    print("=" * 60)

    # Test Case 1: Base Year = 2026-27
    print("\n[Case 1: Central Academic Year = 2026-27]")
    expected_2026 = {
        1: "2026-27",
        2: "2026-27",
        3: "2025-26",
        4: "2025-26",
        5: "2024-25",
        6: "2024-25",
    }
    for sem, expected in expected_2026.items():
        result = python_calculate_academic_year(sem, "2026-27")
        assert result == expected, f"Sem {sem}: expected {expected}, got {result}"
        print(f"  [PASS] Sem {sem} -> Academic Year: {result}")

    # Test Case 2: Base Year = 2027-28
    print("\n[Case 2: Central Academic Year = 2027-28]")
    expected_2027 = {
        1: "2027-28",
        2: "2027-28",
        3: "2026-27",
        4: "2026-27",
        5: "2025-26",
        6: "2025-26",
    }
    for sem, expected in expected_2027.items():
        result = python_calculate_academic_year(sem, "2027-28")
        assert result == expected, f"Sem {sem}: expected {expected}, got {result}"
        print(f"  [PASS] Sem {sem} -> Academic Year: {result}")

    # Test Case 3: Base Year = 2028-29
    print("\n[Case 3: Central Academic Year = 2028-29]")
    expected_2028 = {
        1: "2028-29",
        2: "2028-29",
        3: "2027-28",
        4: "2027-28",
        5: "2026-27",
        6: "2026-27",
    }
    for sem, expected in expected_2028.items():
        result = python_calculate_academic_year(sem, "2028-29")
        assert result == expected, f"Sem {sem}: expected {expected}, got {result}"
        print(f"  [PASS] Sem {sem} -> Academic Year: {result}")

    # Test Case 4: Verify static HTML & JS integration
    print("\n[Case 4: Verifying frontend files]")
    with open("templates/admin/students.html", "r", encoding="utf-8") as f:
        html_content = f.read()
        assert 'data-central-year="{{ academic.academic_year' in html_content
        assert 'Auto-fills based on selected Semester' in html_content
        print("  [PASS] templates/admin/students.html has data-central-year attribute & helper text.")

    with open("static/js/student_form.js", "r", encoding="utf-8") as f:
        js_content = f.read()
        assert 'calculateAcademicYearForSemester' in js_content
        assert 'fields.semester.addEventListener("change"' in js_content
        print("  [PASS] static/js/student_form.js has calculateAcademicYearForSemester & change event listener.")

    # Test Case 5: End-to-end Student Creation using auto-calculated values
    print("\n[Case 5: Database Creation with Auto-Calculated Years]")
    with app.app_context():
        created_students = []
        try:
            for sem in [1, 3, 5]:
                calc_year = python_calculate_academic_year(sem, "2026-27")
                payload = {
                    "full_name": f"Autofill Test Student",
                    "email": f"autofill_sem{sem}@college.edu",
                    "mobile": f"987654321{sem}",
                    "dob": "2005-01-01",
                    "course": "BCA",
                    "semester": str(sem),
                    "division": "A",
                    "academic_year": calc_year
                }
                parsed_data, errors = validate_student_input(payload)
                assert not errors, f"Errors for sem {sem}: {errors}"
                st, err = create_student(
                    full_name=parsed_data['full_name'],
                    email=parsed_data['email'],
                    mobile=parsed_data['mobile'],
                    parsed_dob=parsed_data['dob'],
                    course=parsed_data['course'],
                    parsed_semester=parsed_data['semester'],
                    division=parsed_data['division'],
                    academic_year=parsed_data['academic_year']
                )
                assert err is None, f"Create student failed for sem {sem}: {err}"
                assert st.semester == sem
                assert st.academic_year == calc_year
                created_students.append(st)
                print(f"  [PASS] Successfully created Sem {sem} student with Academic Year '{st.academic_year}' (Roll No: {st.roll_number})")
        finally:
            for st in created_students:
                db.session.delete(st)
            db.session.commit()
            print("  [PASS] Test student records cleaned up.")

    print("\n" + "=" * 60)
    print("ALL AUTO-FILL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 60)

if __name__ == '__main__':
    test_autofill_logic()
