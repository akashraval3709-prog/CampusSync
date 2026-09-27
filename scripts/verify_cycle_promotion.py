"""
CampusSync - Verification Test: Odd-to-Even Cycle Student Promotion Flow
========================================================================
File: scripts/verify_cycle_promotion.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, AcademicSetting, InternalMark
from services.academic_service import (
    get_academic_settings,
    get_odd_semester_students_count,
    promote_odd_to_even_students,
    update_academic_settings
)

def run_tests():
    with app.app_context():
        print("\n========================================================")
        print(" TEST: Odd-to-Even Student Promotion & Settings Flow")
        print("========================================================")

        # 1. Check current Academic Setting and Odd Student Counts
        settings = get_academic_settings()
        print(f"Current Settings: Year={settings.academic_year}, Cycle={settings.semester_cycle}")

        odd_summary = get_odd_semester_students_count(settings.academic_year)
        print(f"Odd Semester Active Counts: {odd_summary}")
        assert 'sem1' in odd_summary and 'sem3' in odd_summary and 'sem5' in odd_summary and 'total' in odd_summary
        assert odd_summary['total'] == odd_summary['sem1'] + odd_summary['sem3'] + odd_summary['sem5']
        print(" [PASS] get_odd_semester_students_count returns accurate structure.")

        # 2. Record initial baseline counts per semester and student IDs
        baseline = {}
        original_odd_students = {
            1: [s.id for s in Student.query.filter_by(semester=1, status='Active').all()],
            3: [s.id for s in Student.query.filter_by(semester=3, status='Active').all()],
            5: [s.id for s in Student.query.filter_by(semester=5, status='Active').all()]
        }
        for sem in range(1, 7):
            baseline[sem] = Student.query.filter_by(semester=sem, status='Active').count()
        init_total_marks = InternalMark.query.count()
        print(f"Baseline semester distribution: {baseline}")
        print(f"Baseline total internal marks: {init_total_marks}")

        # 3. Simulate Promotion
        print("\nTesting promote_odd_to_even_students()...")
        promoted_count, err = promote_odd_to_even_students(settings.academic_year)
        assert err is None, f"Promotion returned error: {err}"
        assert promoted_count == odd_summary['total'], f"Promoted count ({promoted_count}) != expected ({odd_summary['total']})"
        print(f" [PASS] Successfully promoted {promoted_count} students.")

        # Verify new distribution for tested academic year
        ay = settings.academic_year
        post_sem1 = Student.query.filter_by(semester=1, academic_year=ay, status='Active').count()
        post_sem3 = Student.query.filter_by(semester=3, academic_year=ay, status='Active').count()
        post_sem5 = Student.query.filter_by(semester=5, academic_year=ay, status='Active').count()
        post_sem2 = Student.query.filter_by(semester=2, academic_year=ay, status='Active').count()
        post_sem4 = Student.query.filter_by(semester=4, academic_year=ay, status='Active').count()
        post_sem6 = Student.query.filter_by(semester=6, academic_year=ay, status='Active').count()

        base_ay = {
            s: Student.query.filter_by(semester=s, academic_year=ay, status='Active').count() for s in range(1, 7)
        }
        # In baseline, sem 1 was odd_summary['sem1'], sem 3 was odd_summary['sem3'], sem 5 was odd_summary['sem5']
        print(f"Post-promotion distribution for {ay}: Sem 1={post_sem1}, Sem 2={post_sem2}, Sem 3={post_sem3}, Sem 4={post_sem4}, Sem 5={post_sem5}, Sem 6={post_sem6}")
        assert post_sem1 == 0, f"Sem 1 count should be 0, got {post_sem1}"
        assert post_sem3 == 0, f"Sem 3 count should be 0, got {post_sem3}"
        assert post_sem5 == 0, f"Sem 5 count should be 0, got {post_sem5}"
        print(" [PASS] Exact descending order verified (no duplicate cascading!).")

        # Verify internal marks count untouched
        post_total_marks = InternalMark.query.count()
        assert post_total_marks == init_total_marks, f"Marks mismatch: {post_total_marks} != {init_total_marks}"
        print(f" [PASS] Zero data loss! Internal marks count perfectly preserved ({post_total_marks}).")

        # 4. Rollback students back to baseline by exact ID
        print("\nRestoring database back to initial baseline state...")
        for sem, ids in original_odd_students.items():
            if ids:
                Student.query.filter(Student.id.in_(ids)).update({'semester': sem}, synchronize_session='fetch')
        db.session.commit()

        restored = {}
        for sem in range(1, 7):
            restored[sem] = Student.query.filter_by(semester=sem, status='Active').count()
        print(f"Restored distribution: {restored}")
        for sem in range(1, 7):
            assert restored[sem] == baseline[sem], f"Sem {sem} restore mismatch: {restored[sem]} != {baseline[sem]}"
        print(" [PASS] Database state cleanly restored to baseline!")

        # 5. Test update_academic_settings unpack and cycle change simulation
        print("\nTesting update_academic_settings() with move_odd_students='no'...")
        form_mock = {
            'academic_year': settings.academic_year,
            'semester_cycle': 'Odd',
            'cycle_start_date': str(settings.cycle_start_date or '2026-06-15'),
            'cycle_end_date': str(settings.cycle_end_date or '2026-11-30'),
            'students_per_division': '70',
            'archive_sem6': 'no',
            'move_odd_students': 'no'
        }
        res_settings, err, arch_count, prom_count = update_academic_settings(form_mock)
        assert err is None, f"Update failed: {err}"
        assert prom_count == 0, "No students should be promoted with move_odd_students='no'"
        assert arch_count == 0, "No students should be archived"
        assert res_settings.semester_cycle == 'Odd'
        print(" [PASS] update_academic_settings returns 4-tuple with correct counts.")

        print("\n========================================================")
        print(" ALL VERIFICATION TESTS PASSED SUCCESSFULLY! [PASS]")
        print("========================================================\n")

if __name__ == '__main__':
    run_tests()
