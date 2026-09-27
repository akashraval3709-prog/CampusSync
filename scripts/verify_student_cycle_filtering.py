"""
Verification Script: Admin Student Directory Cycle Filtering
CampusSync ERP
"""
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Student, AcademicSetting
from services.academic_service import get_academic_settings, get_active_semesters
from services.student_service import get_all_students_sorted
from extensions import db

def test_cycle_filtering():
    with app.app_context():
        print("=" * 60)
        print("TEST: STUDENT DIRECTORY SEMESTER CYCLE FILTERING")
        print("=" * 60)

        setting = get_academic_settings()
        assert setting is not None, "Academic setting must exist"
        orig_cycle = setting.semester_cycle
        print(f"Original DB Academic Cycle: {orig_cycle}")

        # -----------------------------------------------------------------
        # TEST 1: ODD CYCLE
        # -----------------------------------------------------------------
        setting.semester_cycle = 'Odd'
        db.session.commit()

        active_odd = get_active_semesters(setting.semester_cycle)
        print(f"\n[Test 1: Odd Cycle] Active Semesters: {active_odd}")
        assert active_odd == [1, 3, 5], f"Expected [1, 3, 5], got {active_odd}"

        # 1.a: All Semesters query (semester=None)
        odd_students = get_all_students_sorted()
        odd_semesters_present = set(s['semester'] for s in odd_students)
        print(f"  All Sem (Odd): Found {len(odd_students)} students. Semesters present: {odd_semesters_present}")
        for sem in odd_semesters_present:
            assert sem in [1, 3, 5], f"Student semester {sem} should not appear in Odd cycle!"

        # 1.b: Query active semester (e.g. semester=1)
        sem1_students = get_all_students_sorted(semester=1)
        print(f"  Filter Sem 1: Found {len(sem1_students)} students.")
        for s in sem1_students:
            assert s['semester'] == 1, f"Expected semester 1, got {s['semester']}"

        # 1.c: Query inactive semester (e.g. semester=2 in Odd cycle)
        sem2_in_odd = get_all_students_sorted(semester=2)
        print(f"  Filter Sem 2 (Inactive in Odd cycle): Found {len(sem2_in_odd)} students.")
        assert len(sem2_in_odd) == 0, f"Expected 0 students for inactive semester 2 in Odd cycle, got {len(sem2_in_odd)}"

        # -----------------------------------------------------------------
        # TEST 2: EVEN CYCLE
        # -----------------------------------------------------------------
        setting.semester_cycle = 'Even'
        db.session.commit()

        active_even = get_active_semesters(setting.semester_cycle)
        print(f"\n[Test 2: Even Cycle] Active Semesters: {active_even}")
        assert active_even == [2, 4, 6], f"Expected [2, 4, 6], got {active_even}"

        # 2.a: All Semesters query (semester=None)
        even_students = get_all_students_sorted()
        even_semesters_present = set(s['semester'] for s in even_students)
        print(f"  All Sem (Even): Found {len(even_students)} students. Semesters present: {even_semesters_present}")
        for sem in even_semesters_present:
            assert sem in [2, 4, 6], f"Student semester {sem} should not appear in Even cycle!"

        # 2.b: Query active semester (e.g. semester=2)
        sem2_students = get_all_students_sorted(semester=2)
        print(f"  Filter Sem 2: Found {len(sem2_students)} students.")
        for s in sem2_students:
            assert s['semester'] == 2, f"Expected semester 2, got {s['semester']}"

        # 2.c: Query inactive semester (e.g. semester=1 in Even cycle)
        sem1_in_even = get_all_students_sorted(semester=1)
        print(f"  Filter Sem 1 (Inactive in Even cycle): Found {len(sem1_in_even)} students.")
        assert len(sem1_in_even) == 0, f"Expected 0 students for inactive semester 1 in Even cycle, got {len(sem1_in_even)}"

        # -----------------------------------------------------------------
        # RESTORE ORIGINAL STATE
        # -----------------------------------------------------------------
        setting.semester_cycle = orig_cycle
        db.session.commit()
        print(f"\n[Restored] Academic Cycle restored to: {orig_cycle}")
        print("=" * 60)
        print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 60)

if __name__ == '__main__':
    test_cycle_filtering()
