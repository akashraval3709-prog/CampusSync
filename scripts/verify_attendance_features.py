import sys
import os

# Set up project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import CollegeSetting, Student
from services.college_service import get_college_settings, update_college_settings
from services.attendance_service import (
    get_student_attendance_dashboard,
    get_semester_attendance_blacklist,
    generate_attendance_blacklist_pdf,
    generate_student_attendance_pdf_bytes
)

def run_tests():
    with app.app_context():
        print("=== TEST 1: College Settings Dynamic Attendance Thresholds ===")
        # Update settings to 70%, 70%, 50%
        class DummyForm:
            def __init__(self, data):
                self.data = data
            def get(self, k, default=None):
                return self.data.get(k, default)

        curr = get_college_settings()
        form_data = {
            'college_name': curr.college_name if curr else 'CampusSync College',
            'college_code': curr.college_code if curr else 'CS01',
            'college_short_name': curr.college_short_name if curr else 'CampusSync',
            'current_academic_year': curr.current_academic_year if curr else '2026-27',
            'affiliation': curr.affiliation if curr else 'HNGU',
            'university_name': curr.university_name if curr else 'HNGU Patan',
            'min_overall_attendance': '70.0',
            'min_subject_attendance': '70.0',
            'attendance_warning_threshold': '50.0'
        }
        res, err = update_college_settings(DummyForm(form_data), files={})
        assert res is True, f"Failed to update college settings: {err}"

        refreshed = get_college_settings()
        print(f"Refreshed settings: Overall={refreshed.min_overall_attendance}%, Subject={refreshed.min_subject_attendance}%, Warning={refreshed.attendance_warning_threshold}%")
        assert refreshed.min_overall_attendance == 70.0
        assert refreshed.min_subject_attendance == 70.0
        assert refreshed.attendance_warning_threshold == 50.0
        print("✓ TEST 1 PASSED: College settings updated and retrieved successfully.")

        print("\n=== TEST 2: Student Attendance Dashboard Dynamic Calculations ===")
        # Get student 156 (Sachin Rathod)
        st = Student.query.filter_by(semester=5).first()
        assert st is not None, "No semester 5 student found"
        print(f"Testing for student: {st.full_name} (ID {st.id}, Sem {st.semester})")

        att_data = get_student_attendance_dashboard(st.id)
        assert att_data is not None
        print(f"Overall Conducted: {att_data['overall_conducted']}, Attended: {att_data['overall_attended']}, Missed: {att_data['overall_missed']}")
        print(f"Overall %: {att_data['overall_percentage']}%, Status: {att_data['overall_status']}")
        print(f"Safe Threshold: {att_data['min_overall_attendance']}%, Needed Safe: {att_data['overall_needed_safe']}")
        print(f"Warning Threshold: {att_data['attendance_warning_threshold']}%, Needed Warning: {att_data['overall_needed_warning']}")

        assert att_data['min_overall_attendance'] == 70.0
        assert att_data['attendance_warning_threshold'] == 50.0
        # If conducted=7, attended=3: (0.7*7 - 3)/(1-0.7) = 1.9/0.3 = 6.33 -> ceil = 7
        assert att_data['overall_needed_safe'] == 7

        print("\nSubject Breakdown check:")
        for sub in att_data['subject_breakdown']:
            print(f"  - [{sub['subject_code']}] {sub['subject_name']}: Total={sub['total_lectures']}, Attended={sub['attended_lectures']}, %={sub['percentage']}%, Status={sub['status']}, NeededSafe={sub['needed_safe']}")
            if sub['total_lectures'] == 0:
                assert sub['status'] == 'Not Started'
                assert sub['needed_safe'] == 0
            if sub['subject_code'] == 'BCA501A': # GUI Programming
                # 5 total, 1 attended: (0.7*5 - 1)/(1-0.7) = 2.5/0.3 = 8.33 -> ceil = 9
                assert sub['needed_safe'] == 9

        print("✓ TEST 2 PASSED: Dynamic calculations match mathematical expectations precisely.")

        print("\n=== TEST 3: Admin Blacklist Defaulter Detection ===")
        blacklist_data = get_semester_attendance_blacklist(
            semester=5,
            academic_year='2026-27',
            overall_threshold=70.0,
            subject_threshold=70.0,
            division='All'
        )
        print(f"Total Students: {blacklist_data['total_students']}, Defaulters Count: {blacklist_data['defaulters_count']}")
        assert blacklist_data['defaulters_count'] >= 1
        defaulter = blacklist_data['defaulters'][0]
        print(f"Defaulter: {defaulter['student'].full_name}, Overall %: {defaulter['overall_percentage']}%, Reasons: {defaulter['reasons']}")
        print(f"Shortage Subjects: {[s['subject_code'] for s in defaulter['shortage_subjects']]}")
        assert len(defaulter['reasons']) > 0
        print("✓ TEST 3 PASSED: Blacklist correctly detects overall and subject-level defaulters.")

        print("\n=== TEST 4: Blacklist Official PDF Generation ===")
        pdf_buf = generate_attendance_blacklist_pdf(blacklist_data)
        assert pdf_buf is not None
        pdf_bytes = pdf_buf.getvalue()
        assert len(pdf_bytes) > 1000
        print(f"✓ TEST 4 PASSED: Defaulter PDF generated successfully ({len(pdf_bytes)} bytes).")

        print("\n=== TEST 5: Student Attendance PDF Generation ===")
        st_pdf_buf = generate_student_attendance_pdf_bytes(st.id)
        assert st_pdf_buf is not None
        st_pdf_bytes = st_pdf_buf.getvalue()
        assert len(st_pdf_bytes) > 1000
        print(f"✓ TEST 5 PASSED: Student Attendance PDF generated successfully ({len(st_pdf_bytes)} bytes).")

        print("\nALL 5 TESTS PASSED SUCCESSFULLY! 🎯")

if __name__ == '__main__':
    run_tests()
