"""
CampusSync - Verification Test: Manual Add Student with Custom Academic Year
=============================================================================
File: scripts/verify_manual_add_student.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, AcademicSetting
from services.student_service import create_student
from utils.validators import validate_student_input
import datetime

def test_manual_student_with_custom_academic_year():
    print("\n--- TEST: Manual Add Student with Custom Academic Year & Any Semester ---")
    with app.app_context():
        # Baseline central settings
        settings = AcademicSetting.query.first()
        print(f"Central Settings: Year={settings.academic_year}, Cycle={settings.semester_cycle}")

        # Choose a custom year and semester (e.g. Sem 4 while cycle might be Odd)
        custom_year = "2025-26"
        target_semester = 4
        test_email = "test_custom_year_manual@college.edu"
        test_mobile = "9112233445"

        # 1. Test validator with academic_year
        form_payload = {
            "full_name": "Custom Year Student",
            "email": test_email,
            "mobile": test_mobile,
            "dob": "2005-04-12",
            "course": "BCA",
            "semester": str(target_semester),
            "division": "A",
            "academic_year": custom_year
        }

        parsed_data, errors = validate_student_input(form_payload)
        assert not errors, f"Validation returned errors: {errors}"
        assert parsed_data['academic_year'] == custom_year, f"Expected {custom_year}, got {parsed_data['academic_year']}"
        print(" [PASS] validate_student_input accurately extracted custom academic_year.")

        # 2. Test create_student
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
        assert err is None, f"create_student returned error: {err}"
        assert st is not None, "Student record should be created"
        assert st.academic_year == custom_year, f"Student academic_year mismatch: {st.academic_year} != {custom_year}"
        assert st.semester == target_semester, f"Student semester mismatch: {st.semester} != {target_semester}"
        print(f" [PASS] Student #{st.id} successfully created with custom academic_year='{st.academic_year}' in Semester {st.semester} without modifying central settings ({settings.academic_year})!")

        # 3. Clean up test record
        db.session.delete(st)
        db.session.commit()
        print(" [PASS] Cleaned up test student record.")

        # 4. Verify central settings remained untouched
        settings_after = AcademicSetting.query.first()
        assert settings_after.academic_year == settings.academic_year, "Central settings must remain unchanged"
        print(f" [PASS] Central settings 100% untouched ({settings_after.academic_year}).")

if __name__ == '__main__':
    test_manual_student_with_custom_academic_year()
    print("\nALL MANUAL ADD STUDENT ACADEMIC YEAR TESTS PASSED! [PASS]\n")
