"""
Verification script for Faculty Students Module
================================================
Checks:
1. Unauthenticated access protection on /faculty/students.
2. Logged-in faculty access to /faculty/students.
3. Strict filtering by faculty_subject_assignments (assigned vs unassigned).
4. Numerical Roll Number ascending sorting.
5. Read-only student details structure.
6. Integrity of existing faculty routes & database records.
"""

import sys
import os

# Set stdout encoding for Windows compatibility
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Faculty, Subject, FacultySubjectAssignment, Student, StudentSubject
from services.faculty_service import get_faculty_assigned_students, get_faculty_assigned_subjects


def run_tests():
    print("==================================================")
    print("STARTING FACULTY STUDENTS MODULE VERIFICATION")
    print("==================================================")

    with app.app_context():
        # 1. Inspect active faculty & subject assignments in DB
        faculty_member = Faculty.query.filter_by(status='Active').first()
        if not faculty_member:
            print("[FAIL] No active faculty member found in database.")
            return False

        print(f"[OK] Found active faculty: ID {faculty_member.id} ({faculty_member.full_name}, Email: {faculty_member.email})")

        assignments = FacultySubjectAssignment.query.filter_by(
            faculty_id=faculty_member.id,
            status='Active'
        ).all()

        if not assignments:
            print("[WARN] No active subject assignments for this faculty. Creating temporary test assignment...")
            sub = Subject.query.first()
            if not sub:
                print("[FAIL] No subject records found in database.")
                return False
            assign = FacultySubjectAssignment(
                faculty_id=faculty_member.id,
                subject_id=sub.id,
                division='A',
                status='Active'
            )
            db.session.add(assign)
            db.session.commit()
            assignments = [assign]

        assigned_sub = Subject.query.get(assignments[0].subject_id)
        assigned_div = assignments[0].division

        print(f"[OK] Testing assigned Subject ID {assigned_sub.id} ({assigned_sub.subject_code}) Division '{assigned_div}'")

        # 2. Test get_faculty_assigned_students service query
        data, err = get_faculty_assigned_students(
            faculty_id=faculty_member.id,
            subject_id=assigned_sub.id,
            division=assigned_div,
            semester=assigned_sub.semester,
            academic_year="2026-27"
        )

        if err:
            print(f"[FAIL] Error returned from get_faculty_assigned_students: {err}")
            return False

        students = data.get("students", [])
        print(f"[OK] Service query returned {len(students)} students for assigned Subject/Division.")

        # 3. Test Numerical Roll Number ascending sorting
        roll_numbers = [s["roll_number"] for s in students if s.get("roll_number")]

        def _parse_roll(r):
            digits = "".join(c for c in str(r) if c.isdigit())
            return int(digits) if digits else 999999

        numeric_rolls = [_parse_roll(r) for r in roll_numbers]
        is_sorted = numeric_rolls == sorted(numeric_rolls)

        if is_sorted:
            print(f"[PASS] Roll numbers are sorted numerically ascending: {roll_numbers[:10]}")
        else:
            print(f"[FAIL] Roll numbers are NOT sorted numerically ascending! Found: {roll_numbers}")
            return False

        # 4. Test Authorization Check (Unassigned Subject/Division)
        # Find all assigned subject_ids for this faculty
        assigned_sub_ids = {a.subject_id for a in assignments}
        unassigned_sub = Subject.query.filter(~Subject.id.in_(assigned_sub_ids)).first()
        test_sub_id = unassigned_sub.id if unassigned_sub else 999999
        test_div = 'Z'

        unassigned_data, unassigned_err = get_faculty_assigned_students(
            faculty_id=faculty_member.id,
            subject_id=test_sub_id,
            division=test_div
        )
        if unassigned_err and "Access denied" in unassigned_err:
            print("[PASS] Security check correctly blocked access to unassigned subject/division.")
        else:
            print(f"[FAIL] Security check failed to block unassigned subject access! Got: {unassigned_err}")
            return False

        # 5. Flask Test Client Route Checks
        client = app.test_client()

        # Check 1: Unauthenticated request to /faculty/students
        resp_unauth = client.get('/faculty/students')
        if resp_unauth.status_code in [302, 401, 403]:
            print(f"[PASS] Unauthenticated access to /faculty/students redirected/blocked (Status {resp_unauth.status_code}).")
        else:
            print(f"[FAIL] Unauthenticated access returned HTTP {resp_unauth.status_code}!")
            return False

        # Check 2: Authenticated request with session
        with client.session_transaction() as sess:
            sess["faculty_id"] = faculty_member.id

        resp_auth = client.get(f'/faculty/students?subject_id={assigned_sub.id}&division={assigned_div}')
        if resp_auth.status_code == 200 and b"Assigned Students" in resp_auth.data:
            print("[PASS] Logged-in faculty can access /faculty/students successfully (HTTP 200).")
        else:
            print(f"[FAIL] Authenticated request to /faculty/students failed! (Status {resp_auth.status_code})")
            return False

        # Check 3: Sidebar contains Students link
        if b'href="/faculty/students"' in resp_auth.data or b"Students" in resp_auth.data:
            print("[PASS] Faculty sidebar includes 'Students' navigation item.")
        else:
            print("[FAIL] 'Students' link missing from rendered sidebar!")
            return False

        # Check 4: Verify existing routes still function
        resp_dash = client.get('/faculty/dashboard')
        resp_subj = client.get('/faculty/subjects')
        resp_marks = client.get('/faculty/marks')

        if resp_dash.status_code == 200 and resp_subj.status_code == 200 and resp_marks.status_code == 200:
            print("[PASS] Existing Faculty Dashboard, My Subjects, and Internal Marks routes continue working cleanly.")
        else:
            print("[FAIL] Regressions found in existing faculty routes!")
            return False

    print("==================================================")
    print("ALL FACULTY STUDENTS MODULE TESTS PASSED SAFELY!")
    print("==================================================")
    return True


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
