"""
CampusSync - Verification Test: Academic Lifecycle Student Rules
================================================================
File: scripts/verify_cycle_rules.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, AcademicSetting
from services.academic_service import get_academic_settings, get_active_semesters
from services.student_service import get_all_students_sorted, create_student, bulk_change_semester

def run_tests():
    with app.app_context():
        settings = get_academic_settings()
        original_cycle = settings.semester_cycle
        print(f"Initial Academic Cycle: {original_cycle}")

        try:
            # -------------------------------------------------------------
            # TEST 1: ODD CYCLE RULES
            # -------------------------------------------------------------
            print("\n=== TEST 1: ODD CYCLE ENFORCEMENT ===")
            settings.semester_cycle = 'Odd'
            db.session.commit()

            active_sems = get_active_semesters('Odd')
            print(f"Active Semesters: {active_sems}")
            assert active_sems == [1, 3, 5]

            # 1.1: Verify get_all_students_sorted only returns Sem 1, 3, 5
            students = get_all_students_sorted()
            semesters_present = set(s['semester'] for s in students)
            print(f"Semesters found in get_all_students_sorted(): {semesters_present}")
            for s in students:
                assert s['semester'] in [1, 3, 5], f"Odd cycle contained non-odd student: Sem {s['semester']}"
            print("  [PASS] Only Odd cycle students (Sem 1, 3, 5) returned in directory.")

            # 1.2: Adding a student to Sem 4 must be rejected with 400
            new_st, err = create_student(
                full_name="Invalid Even Student",
                email="invalideven@test.com",
                mobile="9999988881",
                parsed_dob=None,
                course="BCA",
                parsed_semester=4,
                division="A"
            )
            assert new_st is None, "Should not create student in Sem 4 during Odd cycle"
            assert err is not None, "Should return validation error"
            print(f"  [PASS] Blocked adding to Sem 4: '{err[0]}'")

            # 1.3: Adding a student to Sem 2 must be rejected with 400
            new_st, err = create_student(
                full_name="Invalid Sem 2 Student",
                email="invalidsem2@test.com",
                mobile="9999988882",
                parsed_dob=None,
                course="BCA",
                parsed_semester=2,
                division="A"
            )
            assert new_st is None, "Should not create student in Sem 2 during Odd cycle"
            print(f"  [PASS] Blocked adding to Sem 2: '{err[0]}'")

            # 1.4: Bulk moving to Sem 4 must be rejected with 400
            first_student = Student.query.first()
            if first_student:
                res, move_err = bulk_change_semester([first_student.id], 4)
                assert res is None, "Should not move student to Sem 4 during Odd cycle"
                assert move_err[1] == 400, "Error code must be 400"
                print(f"  [PASS] Blocked moving to Sem 4: '{move_err[0]}'")

            # -------------------------------------------------------------
            # TEST 2: EVEN CYCLE RULES
            # -------------------------------------------------------------
            print("\n=== TEST 2: EVEN CYCLE ENFORCEMENT ===")
            settings.semester_cycle = 'Even'
            db.session.commit()

            active_sems_even = get_active_semesters('Even')
            print(f"Active Semesters: {active_sems_even}")
            assert active_sems_even == [2, 4, 6]

            # 2.1: Verify get_all_students_sorted only returns Sem 2, 4, 6
            students_even = get_all_students_sorted()
            semesters_even_present = set(s['semester'] for s in students_even)
            print(f"Semesters found in get_all_students_sorted() for Even cycle: {semesters_even_present}")
            for s in students_even:
                assert s['semester'] in [2, 4, 6], f"Even cycle contained non-even student: Sem {s['semester']}"
            print("  [PASS] Only Even cycle students (Sem 2, 4, 6) returned in directory.")

            # 2.2: Adding a student to Sem 1 must be rejected with 400
            new_st, err = create_student(
                full_name="Invalid Odd Student",
                email="invalidodd@test.com",
                mobile="9999988883",
                parsed_dob=None,
                course="BCA",
                parsed_semester=1,
                division="A"
            )
            assert new_st is None, "Should not create student in Sem 1 during Even cycle"
            print(f"  [PASS] Blocked adding to Sem 1 during Even cycle: '{err[0]}'")

            # 2.3: Bulk moving to Sem 3 must be rejected with 400
            if first_student:
                res, move_err = bulk_change_semester([first_student.id], 3)
                assert res is None, "Should not move student to Sem 3 during Even cycle"
                assert move_err[1] == 400, "Error code must be 400"
                print(f"  [PASS] Blocked moving to Sem 3 during Even cycle: '{move_err[0]}'")

            print("\nALL LIFECYCLE TESTS PASSED! [PASS]")

        finally:
            # Restore original cycle
            settings.semester_cycle = original_cycle
            db.session.commit()
            print(f"\nRestored Academic Cycle to: {original_cycle}")

if __name__ == '__main__':
    run_tests()
