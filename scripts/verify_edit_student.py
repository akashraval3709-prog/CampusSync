"""
CampusSync - Verification Test: Edit Student Functionality & API
================================================================
File: scripts/verify_edit_student.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, AcademicSetting
from services.student_service import get_student_dict, update_student, create_student

def test_edit_student():
    print("=" * 60)
    print("TEST: STUDENT EDIT FUNCTIONALITY & API")
    print("=" * 60)

    with app.app_context():
        # Create a test student
        test_email = "edit_test_student@college.edu"
        test_mobile = "9900112233"
        st, err = create_student(
            full_name="Original Name",
            email=test_email,
            mobile=test_mobile,
            parsed_dob=None,
            course="BCA",
            parsed_semester=1,
            division="A",
            academic_year="2026-27"
        )
        assert err is None, f"Failed to create test student: {err}"
        test_id = st.id
        print(f"[1] Test student created: ID {test_id}, Name '{st.full_name}', Roll {st.roll_number}")

        try:
            # 1. Test get_student_dict
            s_dict = get_student_dict(test_id)
            assert s_dict is not None
            assert s_dict['full_name'] == "Original Name"
            assert s_dict['email'] == test_email
            assert s_dict['semester'] == 1
            print("  [PASS] get_student_dict returned complete student profile.")

            # 2. Test updating student details
            update_data = {
                "full_name": "Updated Full Name",
                "email": "updated_test_email@college.edu",
                "mobile": "9900112244",
                "dob": "2005-06-15",
                "course": "BCA",
                "semester": "1",
                "division": "B",
                "academic_year": "2026-27",
                "status": "Active"
            }
            updated_st, err_msg, code = update_student(test_id, update_data)
            assert err_msg is None, f"Update failed: {err_msg}"
            assert updated_st.full_name == "Updated Full Name"
            assert updated_st.email == "updated_test_email@college.edu"
            assert updated_st.division == "B"
            assert str(updated_st.dob) == "2005-06-15"
            print(f"  [PASS] Successfully updated student fields (Name: '{updated_st.full_name}', Div: '{updated_st.division}').")

            # 3. Test changing status to Inactive
            update_data["status"] = "Inactive"
            updated_st, err_msg, code = update_student(test_id, update_data)
            assert err_msg is None
            assert updated_st.status == "Inactive"
            print("  [PASS] Successfully updated student status to 'Inactive'.")

            # 4. Test validation: duplicate email rejection
            # Create a second student to trigger collision
            st2, _ = create_student(
                full_name="Second Student",
                email="second_student_unique@college.edu",
                mobile="9900112255",
                parsed_dob=None,
                course="BCA",
                parsed_semester=1,
                division="A",
                academic_year="2026-27"
            )
            try:
                update_data["email"] = "second_student_unique@college.edu"
                _, err_msg, code = update_student(test_id, update_data)
                assert code == 409
                assert "already registered" in err_msg
                print(f"  [PASS] Duplicate email update correctly rejected: '{err_msg}'.")
            finally:
                db.session.delete(st2)
                db.session.commit()

            # 5. Test Flask Test Client (API routes)
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['admin_id'] = 1  # simulate logged-in admin

                # Test GET /admin/api/students/<id>
                resp = client.get(f"/admin/api/students/{test_id}")
                assert resp.status_code == 200
                data = resp.get_json()
                assert data['success'] is True
                assert data['student']['full_name'] == "Updated Full Name"
                print("  [PASS] GET /admin/api/students/<id> returned 200 with student details.")

                # Test POST /admin/api/students/<id>/update
                api_payload = {
                    "full_name": "API Final Name",
                    "email": "api_final@college.edu",
                    "mobile": "9988776655",
                    "dob": "2005-08-20",
                    "course": "BCA",
                    "semester": "1",
                    "division": "A",
                    "academic_year": "2026-27",
                    "status": "Active"
                }
                post_resp = client.post(
                    f"/admin/api/students/{test_id}/update",
                    json=api_payload
                )
                assert post_resp.status_code == 200
                post_data = post_resp.get_json()
                assert post_data['success'] is True
                print(f"  [PASS] POST /admin/api/students/<id>/update succeeded: '{post_data['message']}'.")

        finally:
            # Clean up test student
            test_st = Student.query.get(test_id)
            if test_st:
                db.session.delete(test_st)
                db.session.commit()
            print("[Cleaned up] Test student record removed.")

    print("=" * 60)
    print("ALL STUDENT EDIT VERIFICATION TESTS PASSED! (100% PASS)")
    print("=" * 60)

if __name__ == '__main__':
    test_edit_student()
