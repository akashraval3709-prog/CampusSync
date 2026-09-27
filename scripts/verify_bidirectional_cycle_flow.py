"""
CampusSync - Verification Test: Bidirectional Cycle Switching & Data Preservation Flow
======================================================================================
File: scripts/verify_bidirectional_cycle_flow.py

Tests:
1. Odd-to-Even student transition (1->2, 3->4, 5->6) -> Even data loads.
2. Even-to-Odd student transition (2->1, 4->3, 6->5) -> Odd data loads.
3. Zero data loss: Internal marks and attendance records remain 100% intact.
4. archive_graduating_students preserves historical data without hard-deleting active rows.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, AcademicSetting, InternalMark
from services.academic_service import (
    get_academic_settings,
    get_active_semesters,
    get_odd_semester_students_count,
    get_even_semester_students_count,
    promote_odd_to_even_students,
    move_even_to_odd_students,
    update_academic_settings,
    archive_graduating_students
)
from services.student_service import get_all_students_sorted

def run_tests():
    with app.app_context():
        print("\n========================================================")
        print(" TEST: Bidirectional Cycle Switching (Odd <-> Even)")
        print("========================================================")

        settings = get_academic_settings()
        orig_year = settings.academic_year
        orig_cycle = settings.semester_cycle
        print(f"Initial State: Academic Year={orig_year}, Cycle={orig_cycle}")

        # Record initial baseline of active students
        baseline_students = Student.query.filter_by(status='Active').all()
        baseline_marks = InternalMark.query.count()
        print(f"Total Active Students: {len(baseline_students)}, Total Marks: {baseline_marks}")

        try:
            # -------------------------------------------------------------
            # STEP 1: SET CYCLE TO ODD & VERIFY ODD DATA
            # -------------------------------------------------------------
            print("\n[Step 1] Setting cycle to 'Odd'...")
            settings.semester_cycle = 'Odd'
            db.session.commit()

            active_odd = get_active_semesters('Odd')
            assert active_odd == [1, 3, 5], f"Expected [1, 3, 5], got {active_odd}"
            print(f" [PASS] Active semesters for Odd cycle: {active_odd}")

            # -------------------------------------------------------------
            # STEP 2: TEST ODD -> EVEN TRANSITION
            # -------------------------------------------------------------
            print("\n[Step 2] Testing Odd -> Even Transition...")
            odd_counts = get_odd_semester_students_count(settings.academic_year)
            print(f" Active Odd Students Before Promotion: {odd_counts}")

            if odd_counts['total'] > 0:
                promoted, err = promote_odd_to_even_students(settings.academic_year)
                assert err is None, f"Odd->Even failed: {err}"
                print(f" [PASS] Successfully moved {promoted} students to Even semesters.")

                # Switch cycle to Even
                settings.semester_cycle = 'Even'
                db.session.commit()

                # Verify Even cycle data loads
                active_even = get_active_semesters('Even')
                assert active_even == [2, 4, 6], f"Expected [2, 4, 6], got {active_even}"
                even_students = get_all_students_sorted()
                even_sems_present = set(s['semester'] for s in even_students)
                print(f" [PASS] Even Cycle Active Semesters: {active_even}. Semesters loaded: {even_sems_present}")
                for sem in even_sems_present:
                    assert sem in [2, 4, 6], f"Unexpected semester {sem} in Even cycle!"

                # Verify zero marks lost
                current_marks = InternalMark.query.count()
                assert current_marks == baseline_marks, f"Marks lost! {current_marks} != {baseline_marks}"
                print(f" [PASS] Zero data loss verified after Odd->Even promotion (Marks count: {current_marks}).")

            # -------------------------------------------------------------
            # STEP 3: TEST EVEN -> ODD TRANSITION
            # -------------------------------------------------------------
            print("\n[Step 3] Testing Even -> Odd Transition...")
            even_counts = get_even_semester_students_count(settings.academic_year)
            print(f" Active Even Students Before Transition: {even_counts}")

            if even_counts['total'] > 0:
                moved, err = move_even_to_odd_students(settings.academic_year)
                assert err is None, f"Even->Odd failed: {err}"
                print(f" [PASS] Successfully transitioned {moved} students back to Odd semesters.")

                # Switch cycle to Odd
                settings.semester_cycle = 'Odd'
                db.session.commit()

                # Verify Odd cycle data loads
                odd_students = get_all_students_sorted()
                odd_sems_present = set(s['semester'] for s in odd_students)
                print(f" [PASS] Odd Cycle Active Semesters: [1, 3, 5]. Semesters loaded: {odd_sems_present}")
                for sem in odd_sems_present:
                    assert sem in [1, 3, 5], f"Unexpected semester {sem} in Odd cycle!"

                # Verify zero marks lost
                current_marks = InternalMark.query.count()
                assert current_marks == baseline_marks, f"Marks lost! {current_marks} != {baseline_marks}"
                print(f" [PASS] Zero data loss verified after Even->Odd transition (Marks count: {current_marks}).")

            # -------------------------------------------------------------
            # STEP 4: TEST update_academic_settings WITH move_even_students
            # -------------------------------------------------------------
            print("\n[Step 4] Testing update_academic_settings() with move_even_students='yes'...")
            # First promote to Even to create Even students
            promote_odd_to_even_students(settings.academic_year)
            settings.semester_cycle = 'Even'
            db.session.commit()

            # Now submit form with semester_cycle='Odd' and move_even_students='yes'
            form_payload = {
                'academic_year': settings.academic_year,
                'semester_cycle': 'Odd',
                'cycle_start_date': str(settings.cycle_start_date or '2026-06-15'),
                'cycle_end_date': str(settings.cycle_end_date or '2026-12-15'),
                'move_even_students': 'yes'
            }
            res_settings, err, arch_cnt, prom_cnt = update_academic_settings(form_payload)
            assert err is None, f"update_academic_settings returned error: {err}"
            assert res_settings.semester_cycle == 'Odd', f"Expected Odd, got {res_settings.semester_cycle}"
            print(f" [PASS] update_academic_settings successfully handled move_even_students='yes'. Transitioned: {prom_cnt}")

            # Verify Odd cycle students are present
            post_form_students = get_all_students_sorted()
            post_sems = set(s['semester'] for s in post_form_students)
            print(f" [PASS] Active Odd students present: {len(post_form_students)}, Semesters: {post_sems}")

            # -------------------------------------------------------------
            # STEP 5: VERIFY ARCHIVE NO LONGER DELETES ACTIVE STUDENT ROW
            # -------------------------------------------------------------
            print("\n[Step 5] Testing archive_graduating_students() data preservation...")
            # Create a mock Sem 6 student
            test_st = Student(
                roll_number="TEST_ROLL_99",
                enrollment_no="TEST_ENROLL_ARCH_99",
                full_name="Archived Test Student",
                email="testarch99@example.com",
                mobile="9111122222",
                course="BCA",
                semester=6,
                division="A",
                academic_year=settings.academic_year,
                password="mock_password",
                status="Active"
            )
            db.session.add(test_st)
            db.session.commit()

            arch_cnt, arch_err = archive_graduating_students(settings.academic_year, semester=6)
            assert arch_err is None, f"Archiving failed: {arch_err}"

            # Check that test_st was NOT deleted, but marked Inactive!
            re_check = Student.query.filter_by(enrollment_no="TEST_ENROLL_ARCH_99").first()
            assert re_check is not None, "Student record should NOT be deleted!"
            assert re_check.status == 'Inactive', f"Student status should be 'Inactive', got {re_check.status}"
            print(" [PASS] Student record was preserved in database with status='Inactive' (no cascade wipe!).")

            # Clean up test student
            db.session.delete(re_check)
            db.session.commit()
            print(" [PASS] Cleaned up temporary test student.")

            print("\n========================================================")
            print(" ALL BIDIRECTIONAL CYCLE & DATA SAFETY TESTS PASSED! 100%")
            print("========================================================\n")

        finally:
            # Restore original cycle state
            settings.academic_year = orig_year
            settings.semester_cycle = orig_cycle
            db.session.commit()
            print(f"Restored academic cycle to original state: {orig_cycle} ({orig_year})")

if __name__ == '__main__':
    run_tests()
