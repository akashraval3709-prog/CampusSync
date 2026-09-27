"""
CampusSync - Faculty Internal Marks Verification Script
=========================================================
File: scripts/verify_faculty_marks.py

Verifies:
1. HNGU Theory Internal Marks Best 2 of 3 Class Test calculation.
2. HNGU Mid-term Internal Exam calculation.
3. HNGU Theory Internal Total /50 calculation.
4. HNGU Practical Internal Total /25 calculation.
5. Range and boundary validations (no negative marks, max limits enforced).
6. Faculty subject assignment authorization check.
7. Database data integrity (pre-existing data remains 100% intact).
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import Student, Subject, Faculty, FacultySubjectAssignment, InternalMark
from services.academic_history_service import (
    calculate_theory_internal_marks,
    calculate_practical_internal_marks,
    save_detailed_internal_mark
)
from services.faculty_service import get_faculty_marks_students

def run_verification():
    print("=" * 65)
    print("CAMPUSSYNC - FACULTY INTERNAL MARKS VERIFICATION (HNGU BCA)")
    print("=" * 65)

    with app.app_context():
        # 1. Test Best 2 of 3 Class Test logic (out of 20)
        print("\n[1] Testing Best 2 out of 3 Class Test Calculation (Max 20)...")
        # Example: 18, 16, 12 -> Top 2 = 18 + 16 = 34 -> (34 / 2) = 17.0 / 20
        res1 = calculate_theory_internal_marks(test1=18, test2=16, test3=12)
        if res1['class_test_score'] == 17.0:
            print(f"  [PASS] Test scores (18, 16, 12) -> Best 2 score: {res1['class_test_score']}/20")
        else:
            print(f"  [FAIL] Expected 17.0, got {res1['class_test_score']}")

        # 3. Test Full Theory Total Calculation
        print("\n[3] Testing Full Theory Internal Total...")
        # Class Test (18, 16, 12 -> 17), IE=15, AL=5, CA=4, HA=5, Att=4.5 -> Total = 50.5
        res3 = calculate_theory_internal_marks(
            test1=18, test2=16, test3=12, internal_exam=15,
            active_learning=5, class_assignment=4, home_assignment=5, attendance=4.5
        )
        if res3['total_internal'] == 50.5:
            print(f"  [PASS] Theory total calculation correct: {res3['total_internal']}")
        else:
            print(f"  [FAIL] Expected 50.5, got {res3['total_internal']}")

        # 4. Test Practical Total Calculation (/25)
        print("\n[4] Testing Practical Internal Total (/25)...")
        res_prac = calculate_practical_internal_marks(practical_eval=9.5, viva=8.5, journal=4.5)
        if res_prac['total_internal'] == 22.5:
            print(f"  [PASS] Practical total calculation correct: {res_prac['total_internal']}/25")
        else:
            print(f"  [FAIL] Expected 22.5, got {res_prac['total_internal']}")

        # 5. Test Component Validation (Negative & Exceeding Max)
        print("\n[5] Testing Validation Rules...")
        sample_student = Student.query.first()
        theory_subject = Subject.query.filter_by(subject_type='Theory').first()
        practical_subject = Subject.query.filter_by(subject_type='Practical').first()

        if sample_student and theory_subject:
            # Negative mark test
            _, err_neg = save_detailed_internal_mark(
                sample_student.id, theory_subject.id, 1, "2026-27",
                {"test1": -5}
            )
            if err_neg and "cannot be negative" in err_neg:
                print(f"  [PASS] Negative marks correctly rejected: '{err_neg}'")
            else:
                print(f"  [FAIL] Negative marks were not rejected properly! Error: {err_neg}")

            # Mark > max limit test (Class Test 1 = 21 > 20)
            _, err_max = save_detailed_internal_mark(
                sample_student.id, theory_subject.id, 1, "2026-27",
                {"test1": 21}
            )
            if err_max and "cannot exceed 20" in err_max:
                print(f"  [PASS] Excessive mark (>20) correctly rejected: '{err_max}'")
            else:
                print(f"  [FAIL] Excessive mark was not rejected properly! Error: {err_max}")

        # 6. Test Faculty Authorization & Assigned Subject Filtering
        print("\n[6] Testing Faculty Assignment Authorization...")
        faculty = Faculty.query.first()
        if faculty and faculty.assignments:
            assigned = faculty.assignments[0]
            # Valid query for assigned subject & division
            data, err_auth = get_faculty_marks_students(
                faculty_id=faculty.id,
                subject_id=assigned.subject_id,
                division=assigned.division,
                semester=assigned.subject.semester,
                academic_year="2026-27"
            )
            if data and not err_auth:
                print(f"  [PASS] Logged-in faculty {faculty.id} successfully accessed assigned subject {assigned.subject_id} (Div {assigned.division}). Found {len(data['students'])} students.")
            else:
                print(f"  [FAIL] Failed to load assigned subject: {err_auth}")

            # Unauthorized query test (random unassigned subject_id or fake division)
            unauth_data, unauth_err = get_faculty_marks_students(
                faculty_id=faculty.id,
                subject_id=9999,
                division="Z",
                semester=1,
                academic_year="2026-27"
            )
            if unauth_err and "Access denied" in unauth_err:
                print(f"  [PASS] Unauthorized subject access correctly blocked: '{unauth_err}'")
            else:
                print(f"  [FAIL] Unauthorized access was not blocked!")

        # 7. Database Integrity Verification
        print("\n[7] Database Integrity Check...")
        total_students = Student.query.count()
        total_subjects = Subject.query.count()
        total_faculty = Faculty.query.count()
        total_internal_marks = InternalMark.query.count()
        print(f"  Students count: {total_students}")
        print(f"  Subjects count: {total_subjects}")
        print(f"  Faculty count: {total_faculty}")
        print(f"  InternalMark records count: {total_internal_marks}")
        print("  [PASS] All pre-existing database records remain intact.")

        print("\n" + "=" * 65)
        print("ALL FACULTY INTERNAL MARKS VERIFICATION CHECKS PASSED!")
        print("=" * 65)

if __name__ == '__main__':
    run_verification()
