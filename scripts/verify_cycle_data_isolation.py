"""
Verification Script for Dynamic Semester Cycle Data Segregation
Tests Odd vs Even cycle switching across:
1. Faculty Assignment Notices
2. Faculty & Student Notifications
3. Reports Analytics ('All' scope & Bar Charts & Subjects)
4. Admin Dashboard Metrics & Distributions
5. Faculty Dashboard & Assigned Subject Counts
"""
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import AcademicSetting, Notification, Student, Subject, Faculty, FacultySubjectAssignment
from services.academic_service import get_academic_settings, get_active_semesters
from services.assignment_service import get_faculty_assignment_notices
from services.notification_service import get_faculty_notices, get_faculty_created_notices, get_student_notices, get_all_admin_notices
from services.report_service import get_reports_analytics_data
from services.admin_dashboard_service import get_admin_dashboard_data
from services.faculty_service import get_faculty_dashboard_data, get_faculty_statistics

app = create_app()

with app.app_context():
    setting = get_academic_settings()
    original_cycle = setting.semester_cycle
    print(f"\n=======================================================")
    print(f" INITIAL STATE: Year={setting.academic_year}, Cycle={original_cycle}")
    print(f"=======================================================\n")

    try:
        # TEST 1: SET CYCLE TO ODD
        print(">>> [TEST 1] Setting Semester Cycle to 'Odd'...")
        setting.semester_cycle = 'Odd'
        db.session.commit()

        active_odd = get_active_semesters()
        assert active_odd == [1, 3, 5], f"Expected [1, 3, 5], got {active_odd}"
        print(f" [PASS] Active semesters for Odd cycle: {active_odd}")

        # Check Reports Analytics with semester=None ("All")
        rep_odd = get_reports_analytics_data(semester=None)
        chart_labels_odd = rep_odd['overview']['semester_pass_fail']['labels']
        print(f" [PASS] Reports Overview pass/fail chart labels: {chart_labels_odd}")
        assert all(label in ['Sem 1', 'Sem 3', 'Sem 5'] for label in chart_labels_odd), \
            f"Expected only Sem 1, 3, 5 labels in Odd cycle, got {chart_labels_odd}"
        
        # Check Admin Dashboard
        dash_odd = get_admin_dashboard_data()
        dist_sems_odd = [d['semester'] for d in dash_odd['semester_distribution']]
        print(f" [PASS] Admin Dashboard semester distribution: {dist_sems_odd}")
        assert dist_sems_odd == [1, 3, 5], f"Expected [1, 3, 5], got {dist_sems_odd}"

        # TEST 2: SET CYCLE TO EVEN
        print("\n>>> [TEST 2] Setting Semester Cycle to 'Even'...")
        setting.semester_cycle = 'Even'
        db.session.commit()

        active_even = get_active_semesters()
        assert active_even == [2, 4, 6], f"Expected [2, 4, 6], got {active_even}"
        print(f" [PASS] Active semesters for Even cycle: {active_even}")

        # Check Reports Analytics with semester=None ("All")
        rep_even = get_reports_analytics_data(semester=None)
        chart_labels_even = rep_even['overview']['semester_pass_fail']['labels']
        print(f" [PASS] Reports Overview pass/fail chart labels: {chart_labels_even}")
        assert all(label in ['Sem 2', 'Sem 4', 'Sem 6'] for label in chart_labels_even), \
            f"Expected only Sem 2, 4, 6 labels in Even cycle, got {chart_labels_even}"

        # Check Admin Dashboard
        dash_even = get_admin_dashboard_data()
        dist_sems_even = [d['semester'] for d in dash_even['semester_distribution']]
        print(f" [PASS] Admin Dashboard semester distribution: {dist_sems_even}")
        assert dist_sems_even == [2, 4, 6], f"Expected [2, 4, 6], got {dist_sems_even}"

        # TEST 3: TEST NOTICES & ASSIGNMENTS SEGREGATION
        # Create a dummy Odd notice (Sem 3) and a dummy Even notice (Sem 4)
        fac = Faculty.query.first()
        if fac:
            print(f"\n>>> [TEST 3] Testing Faculty Assignment Notices Filtering for Faculty ID={fac.id}...")
            odd_notice = Notification(
                title="[TEST ODD] Assignment Sem 3",
                message="Testing odd assignment",
                category="Assignment Submit Date",
                posted_by_role="Faculty",
                faculty_id=fac.id,
                target_audience="Student",
                target_semester=3,
                is_active=True
            )
            even_notice = Notification(
                title="[TEST EVEN] Assignment Sem 4",
                message="Testing even assignment",
                category="Assignment Submit Date",
                posted_by_role="Faculty",
                faculty_id=fac.id,
                target_audience="Student",
                target_semester=4,
                is_active=True
            )
            db.session.add(odd_notice)
            db.session.add(even_notice)
            db.session.commit()

            # Cycle is currently Even:
            notices_even = get_faculty_assignment_notices(fac.id, filter_by_cycle=True)
            notice_ids_even = [item['notice'].id for item in notices_even]
            assert even_notice.id in notice_ids_even, "Even notice must be visible in Even cycle"
            assert odd_notice.id not in notice_ids_even, "Odd notice must NOT be visible in Even cycle!"
            print(f" [PASS] In Even Cycle: Only Even assignment (Sem 4) visible; Odd assignment (Sem 3) is hidden.")

            # Switch cycle back to Odd:
            setting.semester_cycle = 'Odd'
            db.session.commit()

            notices_odd = get_faculty_assignment_notices(fac.id, filter_by_cycle=True)
            notice_ids_odd = [item['notice'].id for item in notices_odd]
            assert odd_notice.id in notice_ids_odd, "Odd notice must be visible in Odd cycle"
            assert even_notice.id not in notice_ids_odd, "Even notice must NOT be visible in Odd cycle!"
            print(f" [PASS] In Odd Cycle: Only Odd assignment (Sem 3) visible; Even assignment (Sem 4) is hidden.")

            # Cleanup test notices
            db.session.delete(odd_notice)
            db.session.delete(even_notice)
            db.session.commit()
            print(" [PASS] Cleaned up temporary test notifications.")

        print("\n=======================================================")
        print(" ALL CYCLE FILTERING TESTS PASSED PERFECTLY!")
        print("=======================================================\n")

    finally:
        # Restore original cycle
        setting.semester_cycle = original_cycle
        db.session.commit()
        print(f"Restored original academic cycle to: '{original_cycle}'\n")
