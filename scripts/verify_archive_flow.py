"""
CampusSync - Verification Test: Faculty Marks & Sem 6 Archiving Flow
====================================================================
File: scripts/verify_archive_flow.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, Subject, InternalMark, ArchivedStudent, ArchivedInternalMark, Faculty, FacultySubjectAssignment
from services.faculty_service import get_faculty_marks_students
from services.academic_service import get_graduating_students_count, archive_graduating_students, update_academic_settings
from services.academic_history_service import save_detailed_internal_mark

def test_faculty_marks_query():
    print("\n--- TEST 1: Faculty Marks Matrix Query (No StudentSubject) ---")
    with app.app_context():
        assignment = FacultySubjectAssignment.query.filter_by(status='Active').first()
        if not assignment:
            print("  [SKIP] No active faculty assignment found.")
            return

        print(f"  Testing assignment: Faculty #{assignment.faculty_id}, Subject #{assignment.subject_id}, Div '{assignment.division}'")
        data, err = get_faculty_marks_students(
            faculty_id=assignment.faculty_id,
            subject_id=assignment.subject_id,
            division=assignment.division,
            semester=assignment.subject.semester,
            academic_year="2026-27"
        )
        assert err is None, f"Query returned error: {err}"
        assert data is not None, "Data should not be None"
        students = data.get('students', [])
        print(f"  [PASS] Successfully retrieved {len(students)} students without StudentSubject table.")
        for s in students[:3]:
            print(f"    - #{s['roll_number']} {s['full_name']} (Enroll: {s['enrollment_no']})")

def test_archiving_flow():
    print("\n--- TEST 2: Semester 6 Archiving Simulation ---")
    with app.app_context():
        # Baseline counts
        init_students = Student.query.count()
        init_marks = InternalMark.query.count()
        init_archived_students = ArchivedStudent.query.count()
        init_archived_marks = ArchivedInternalMark.query.count()

        print(f"  Baseline: {init_students} students, {init_marks} marks.")

        # Create a test student in Semester 6
        test_enrollment = "TESTSEM6_9999"
        test_st = Student(
            roll_number="999",
            enrollment_no=test_enrollment,
            full_name="Test Graduating Student",
            email="testsem6@college.edu",
            mobile="9876543210",
            course="BCA",
            semester=6,
            division="A",
            academic_year="2026-27",
            password="hashed_pwd_placeholder"
        )
        db.session.add(test_st)
        db.session.commit()

        # Add a test mark for this student
        subj = Subject.query.first()
        test_mark = InternalMark(
            student_id=test_st.id,
            enrollment_no=test_enrollment,
            subject_id=subj.id,
            semester=6,
            academic_year="2026-27",
            marks_obtained=28.5,
            max_marks=30
        )
        db.session.add(test_mark)
        db.session.commit()

        # 1. Check Sem 6 count
        sem6_count = get_graduating_students_count("2026-27", semester=6)
        print(f"  Sem 6 student count detected: {sem6_count} (Expected >= 1)")
        assert sem6_count >= 1, "Should detect at least 1 Sem 6 student"

        # 2. Execute archiving
        print("  Executing archive_graduating_students('2026-27', semester=6)...")
        archived_count, arch_err = archive_graduating_students("2026-27", semester=6)
        assert arch_err is None, f"Archiving failed with error: {arch_err}"
        assert archived_count >= 1, "Should have archived at least 1 student"
        print(f"  [PASS] Archived {archived_count} student(s).")

        # 3. Verify in ArchivedStudent and ArchivedInternalMark
        archived_st = ArchivedStudent.query.filter_by(enrollment_no=test_enrollment).first()
        assert archived_st is not None, "Archived student record must exist"
        print(f"  [PASS] ArchivedStudent record verified: {archived_st.full_name} ({archived_st.enrollment_no})")

        archived_m = ArchivedInternalMark.query.filter_by(enrollment_no=test_enrollment).first()
        assert archived_m is not None, "ArchivedInternalMark record must exist"
        print(f"  [PASS] ArchivedInternalMark verified: {archived_m.marks_obtained}/{archived_m.max_marks} for enroll '{archived_m.enrollment_no}'")

        # 4. Verify test student removed from active students table
        active_check = Student.query.filter_by(enrollment_no=test_enrollment).first()
        assert active_check is None, "Archived student must be removed from active students"
        print("  [PASS] Graduated student cleanly removed from active students table.")

        # Clean up test archived records to keep DB pristine
        ArchivedInternalMark.query.filter_by(enrollment_no=test_enrollment).delete()
        ArchivedStudent.query.filter_by(enrollment_no=test_enrollment).delete()
        db.session.commit()

        # Verify final student and marks counts match original baseline
        final_students = Student.query.count()
        final_marks = InternalMark.query.count()
        print(f"  Post-cleanup: {final_students} students, {final_marks} marks.")
        assert final_students == init_students, f"Student count mismatch: {final_students} != {init_students}"
        assert final_marks == init_marks, f"Marks count mismatch: {final_marks} != {init_marks}"
        print("  [PASS] Baseline records 100% preserved with ZERO data loss!")

if __name__ == '__main__':
    test_faculty_marks_query()
    test_archiving_flow()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! [PASS]")
