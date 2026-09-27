"""
CampusSync - Faculty Subject Assignment De-duplication Verification Script
===========================================================================
File: scripts/verify_faculty_assignment_dedup.py

Verifies:
1. Different faculty members CAN teach the SAME subject in DIFFERENT divisions.
2. Two faculty members CANNOT teach the SAME subject in the SAME division.
3. Updating faculty allows keeping their own assigned divisions without false conflict.
4. get_available_subjects() accurately reports assigned_divisions.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Faculty, Subject, FacultySubjectAssignment
from services.faculty_service import create_faculty, update_faculty, get_available_subjects
import json

def run_verification():
    print("=" * 70)
    print("CAMPUSSYNC - FACULTY ASSIGNMENT DEDUPLICATION VERIFICATION")
    print("=" * 70)

    with app.app_context():
        faculty_members = Faculty.query.filter_by(status='Active').all()
        if len(faculty_members) < 2:
            print("[SKIP] Need at least 2 active faculty members in database.")
            return True

        f1 = faculty_members[0]
        f2 = faculty_members[1]
        test_sub = Subject.query.filter_by(status='Active').first()

        if not test_sub:
            print("[FAIL] No active subject found.")
            return False

        print(f"Testing with Faculty 1: '{f1.full_name}' (ID: {f1.id}, Code: {f1.faculty_code})")
        print(f"Testing with Faculty 2: '{f2.full_name}' (ID: {f2.id}, Code: {f2.faculty_code})")
        print(f"Testing with Subject: '{test_sub.subject_name}' ({test_sub.subject_code}, ID: {test_sub.id})\n")

        # 1. Clean test subject assignments first
        FacultySubjectAssignment.query.filter_by(subject_id=test_sub.id).delete()
        db.session.commit()

        # 2. Test Case 1: Assign Subject to Faculty 1 for Division A
        print("[1] Testing Assignment: Faculty 1 -> Division A...")
        f1_form = {
            "full_name": f1.full_name,
            "faculty_code": f1.faculty_code,
            "email": f1.email,
            "mobile": f1.mobile,
            "gender": f1.gender or "Male",
            "qualification": f1.qualification or "MCA",
            "designation": f1.designation or "Assistant Professor",
            "department": f1.department or "BCA",
            "status": f1.status or "Active",
            "assigned_subjects": json.dumps([{"code": test_sub.subject_code, "divisions": ["A"]}])
        }
        res_f1, err1 = update_faculty(f1.id, f1_form)
        if err1:
            print(f"  [FAIL] Faculty 1 initial assignment failed: {err1}")
            return False
        print(f"  [PASS] Faculty 1 successfully assigned Division A.")

        # 3. Test Case 2: Assign SAME Subject to Faculty 2 for DIFFERENT Division (Division B)
        print("\n[2] Testing Assignment: Faculty 2 -> Division B (Different Division)...")
        f2_form_b = {
            "full_name": f2.full_name,
            "faculty_code": f2.faculty_code,
            "email": f2.email,
            "mobile": f2.mobile,
            "gender": f2.gender or "Male",
            "qualification": f2.qualification or "MCA",
            "designation": f2.designation or "Assistant Professor",
            "department": f2.department or "BCA",
            "status": f2.status or "Active",
            "assigned_subjects": json.dumps([{"code": test_sub.subject_code, "divisions": ["B"]}])
        }
        res_f2, err2 = update_faculty(f2.id, f2_form_b)
        if err2:
            print(f"  [FAIL] Faculty 2 assignment to Division B should be allowed! Error: {err2}")
            return False
        print(f"  [PASS] Different divisions for same subject allowed (Faculty 1 in Div A, Faculty 2 in Div B).")

        # 4. Test Case 3: Try to assign SAME Subject to Faculty 2 for SAME Division (Division A) -> MUST BE BLOCKED!
        print("\n[3] Testing Conflict: Faculty 2 -> Division A (Same Division as Faculty 1)...")
        f2_form_conflict = {
            "full_name": f2.full_name,
            "faculty_code": f2.faculty_code,
            "email": f2.email,
            "mobile": f2.mobile,
            "gender": f2.gender or "Male",
            "qualification": f2.qualification or "MCA",
            "designation": f2.designation or "Assistant Professor",
            "department": f2.department or "BCA",
            "status": f2.status or "Active",
            "assigned_subjects": json.dumps([{"code": test_sub.subject_code, "divisions": ["A"]}])
        }
        res_conflict, err_conflict = update_faculty(f2.id, f2_form_conflict)
        if res_conflict is None and err_conflict and "already assigned" in err_conflict:
            print(f"  [PASS] Duplicate assignment strictly blocked: '{err_conflict}'")
        else:
            print(f"  [FAIL] Duplicate assignment was NOT blocked! res={res_conflict}, err={err_conflict}")
            return False

        # 5. Test Case 4: Verify get_available_subjects() exposes assigned_divisions
        print("\n[4] Testing get_available_subjects() assigned_divisions metadata...")
        subjects_meta = get_available_subjects()
        match_sub = next((s for s in subjects_meta if s["code"] == test_sub.subject_code), None)
        if not match_sub or "assigned_divisions" not in match_sub:
            print("  [FAIL] assigned_divisions missing in get_available_subjects()")
            return False

        assigned_divs = match_sub["assigned_divisions"]
        print(f"  Assigned divisions for {test_sub.subject_code}: {list(assigned_divs.keys())}")
        if "A" in assigned_divs and assigned_divs["A"]["faculty_id"] == f1.id:
            print(f"  [PASS] Division A correctly mapped to Faculty 1 ({assigned_divs['A']['faculty_name']})")
        else:
            print(f"  [FAIL] Division A mapping incorrect: {assigned_divs}")
            return False

        # 6. Test Case 5: Faculty 1 updating profile retains own Division A without conflict
        print("\n[5] Testing Self-Update: Faculty 1 updates profile keeping Division A...")
        res_self, err_self = update_faculty(f1.id, f1_form)
        if err_self:
            print(f"  [FAIL] Self-update should not trigger conflict with itself! Error: {err_self}")
            return False
        print(f"  [PASS] Faculty 1 can update profile keeping own assigned division without conflict.")

        print("\n" + "=" * 70)
        print("ALL FACULTY ASSIGNMENT DEDUPLICATION CHECKS PASSED!")
        print("=" * 70)
        return True

if __name__ == '__main__':
    success = run_verification()
    sys.exit(0 if success else 1)
