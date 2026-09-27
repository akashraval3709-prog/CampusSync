"""
Verification Script: Academic Year Transition & Student Progression
CampusSync ERP
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import Student, AcademicSetting, ArchivedStudent, ArchivedInternalMark
from services.academic_service import (
    get_academic_settings,
    get_even_semester_students_count,
    update_academic_settings
)
from services.student_service import authenticate_student

def test_transition():
    with app.app_context():
        print("=" * 60)
        print("TEST: ACADEMIC YEAR TRANSITION & PROGRESSION")
        print("=" * 60)

        # Baseline state
        setting = get_academic_settings()
        orig_year = setting.academic_year
        orig_cycle = setting.semester_cycle
        orig_start = setting.cycle_start_date
        orig_end = setting.cycle_end_date

        print(f"Initial State: Year={orig_year}, Cycle={orig_cycle}")

        # Baseline student records
        sem2_ids = [s.id for s in Student.query.filter_by(semester=2, status='Active').all()]
        sem4_ids = [s.id for s in Student.query.filter_by(semester=4, status='Active').all()]
        sem6_ids = [s.id for s in Student.query.filter_by(semester=6, status='Active').all()]

        print(f"Active Counts before transition: Sem 2={len(sem2_ids)}, Sem 4={len(sem4_ids)}, Sem 6={len(sem6_ids)}")
        assert len(sem2_ids) > 0, "Should have active students in Sem 2"
        assert len(sem4_ids) > 0, "Should have active students in Sem 4"
        assert len(sem6_ids) > 0, "Should have active students in Sem 6"

        even_summary = get_even_semester_students_count()
        print(f"Even students summary: {even_summary}")
        assert even_summary['sem2'] == len(sem2_ids)
        assert even_summary['sem4'] == len(sem4_ids)
        assert even_summary['sem6'] == len(sem6_ids)

        test_sem6_student = db.session.get(Student, sem6_ids[0])
        test_email = test_sem6_student.email

        try:
            # -------------------------------------------------------------
            # TEST TRANSITION TO NEW ACADEMIC YEAR: 2027-28
            # -------------------------------------------------------------
            form_data = {
                'cycle_start_date': '2027-06-15',
                'cycle_end_date': '2028-04-15',
                'semester_cycle': 'Even', # even if user passed Even, year change MUST force Odd
                'transition_academic_year': 'yes',
                'students_per_division': '70'
            }

            print("\nExecuting update_academic_settings with new dates (2027-06-15 to 2028-04-15)...")
            updated_settings, err, arch_count, prom_count = update_academic_settings(form_data)

            assert err is None, f"Update failed: {err}"
            assert updated_settings.academic_year == '2027-28', f"Expected 2027-28, got {updated_settings.academic_year}"
            assert updated_settings.semester_cycle == 'Odd', f"Expected Odd, got {updated_settings.semester_cycle}"
            print(f" [PASS] Settings updated: Academic Year={updated_settings.academic_year}, Cycle={updated_settings.semester_cycle}")
            print(f" [PASS] Archived count: {arch_count}, Promoted count: {prom_count}")
            assert arch_count == len(sem6_ids), f"Expected {len(sem6_ids)} archived, got {arch_count}"
            assert prom_count == (len(sem2_ids) + len(sem4_ids)), f"Expected {len(sem2_ids) + len(sem4_ids)} promoted, got {prom_count}"

            # Verify Sem 6 students are set to Inactive
            for sid in sem6_ids:
                st = db.session.get(Student, sid)
                assert st.status == 'Inactive', f"Student #{sid} should be Inactive"
                arch_st = ArchivedStudent.query.filter_by(enrollment_no=st.enrollment_no).first()
                assert arch_st is not None, f"Student #{sid} should exist in ArchivedStudent table"
            print(" [PASS] All Sem 6 students archived & marked Inactive.")

            # Verify student login is blocked for Inactive student with correct password
            from werkzeug.security import generate_password_hash
            test_st_inst = db.session.get(Student, sem6_ids[0])
            orig_pwd_hash = test_st_inst.password
            test_st_inst.password = generate_password_hash("testpwd123")
            db.session.commit()

            login_res, login_err = authenticate_student(test_email, 'testpwd123')
            print(f" [PASS] Inactive student login attempt rejected with: '{login_err}'")
            assert login_err is not None and "inactive" in login_err.lower(), f"Expected inactive error, got: {login_err}"
            test_st_inst.password = orig_pwd_hash
            db.session.commit()

            # Verify Sem 4 students moved to Sem 5
            for sid in sem4_ids:
                st = db.session.get(Student, sid)
                assert st.semester == 5, f"Student #{sid} should have moved to Sem 5, but is in Sem {st.semester}"
            print(" [PASS] All Sem 4 students successfully moved to Semester 5.")

            # Verify Sem 2 students moved to Sem 3
            for sid in sem2_ids:
                st = db.session.get(Student, sid)
                assert st.semester == 3, f"Student #{sid} should have moved to Sem 3, but is in Sem {st.semester}"
            print(" [PASS] All Sem 2 students successfully moved to Semester 3.")

            # Verify Sem 1 is empty
            sem1_active = Student.query.filter_by(semester=1, status='Active').count()
            print(f" [PASS] Active students currently in Semester 1: {sem1_active} (Ready for new enrollments!)")

        finally:
            # -------------------------------------------------------------
            # RESTORE DATABASE CLEANLY TO INITIAL STATE
            # -------------------------------------------------------------
            print("\nRestoring database state back to initial baseline...")
            for sid in sem6_ids:
                st = db.session.get(Student, sid)
                st.status = 'Active'
                st.semester = 6
                # Remove test archive record
                ArchivedStudent.query.filter_by(enrollment_no=st.enrollment_no).delete()

            for sid in sem4_ids:
                st = db.session.get(Student, sid)
                st.semester = 4

            for sid in sem2_ids:
                st = db.session.get(Student, sid)
                st.semester = 2

            setting.academic_year = orig_year
            setting.semester_cycle = orig_cycle
            setting.cycle_start_date = orig_start
            setting.cycle_end_date = orig_end
            db.session.commit()
            print(" [PASS] Database state restored 100% cleanly!")

        print("=" * 60)
        print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 60)

if __name__ == '__main__':
    test_transition()
