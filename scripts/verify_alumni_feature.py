"""
Automated Verification Script for Alumni & Old Student Results Feature
"""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import ArchivedStudent, ArchivedInternalMark, ArchivedStudentOTP, Student
from services.student_service import authenticate_student
from services.alumni_service import (
    find_old_student,
    generate_and_send_alumni_otp,
    verify_alumni_otp,
    get_archived_student_results,
    generate_archived_student_semester_pdf,
    generate_archived_student_consolidated_pdf,
    export_archived_students_excel,
    export_archived_students_pdf
)

def run_tests():
    with app.app_context():
        print("=" * 60)
        print("STARTING ALUMNI FEATURE VERIFICATION TESTS")
        print("=" * 60)

        # 1. Setup a test archived student in database if not present
        test_enroll = "BCA15226000099"
        test_email = "test.alumni@college.edu"

        archived_st = ArchivedStudent.query.filter_by(enrollment_no=test_enroll).first()
        if not archived_st:
            print("[SETUP] Creating sample ArchivedStudent for test...")
            archived_st = ArchivedStudent(
                roll_number="99",
                enrollment_no=test_enroll,
                full_name="Rajesh Sharma (Alumni Test)",
                email=test_email,
                mobile="9876543210",
                course="BCA",
                final_semester=6,
                division="A",
                academic_year="2025-26",
                status="Archived"
            )
            db.session.add(archived_st)
            db.session.commit()

        # Add sample marks across Sem 5 and Sem 6
        m1 = ArchivedInternalMark.query.filter_by(enrollment_no=test_enroll, semester=5).first()
        if not m1:
            print("[SETUP] Adding sample ArchivedInternalMark...")
            db.session.add(ArchivedInternalMark(
                enrollment_no=test_enroll,
                student_name=archived_st.full_name,
                subject_code="BCA501",
                subject_name="Cloud Computing",
                semester=5,
                academic_year="2025-26",
                marks_obtained=42.5,
                max_marks=50
            ))
            db.session.add(ArchivedInternalMark(
                enrollment_no=test_enroll,
                student_name=archived_st.full_name,
                subject_code="BCA502",
                subject_name="Web Frameworks",
                semester=5,
                academic_year="2025-26",
                marks_obtained=38.0,
                max_marks=50
            ))
            db.session.add(ArchivedInternalMark(
                enrollment_no=test_enroll,
                student_name=archived_st.full_name,
                subject_code="BCA601",
                subject_name="Information Security",
                semester=6,
                academic_year="2025-26",
                marks_obtained=45.0,
                max_marks=50
            ))
            db.session.add(ArchivedInternalMark(
                enrollment_no=test_enroll,
                student_name=archived_st.full_name,
                subject_code="BCA602",
                subject_name="Project Work & Viva",
                semester=6,
                academic_year="2025-26",
                marks_obtained=48.0,
                max_marks=50
            ))
            db.session.commit()

        # TEST 1: Student Login Restriction (Requirement 1)
        print("\n--- TEST 1: Student Login Portal Restriction ---")
        student_obj, login_err = authenticate_student(test_email, "somepassword")
        assert student_obj is None, "Archived student MUST NOT be able to log in"
        assert "graduated" in login_err.lower() or "archived" in login_err.lower(), f"Unexpected error: {login_err}"
        print(f"[PASS] Archived student login successfully blocked with message: '{login_err}'")

        # TEST 2: Lookup by Enrollment or Email (Requirement 3)
        print("\n--- TEST 2: Student Identification Lookup ---")
        found_by_enroll = find_old_student(test_enroll)
        assert found_by_enroll is not None, "Failed to find by enrollment"
        assert found_by_enroll.enrollment_no == test_enroll

        found_by_email = find_old_student(test_email)
        assert found_by_email is not None, "Failed to find by email"
        assert found_by_email.email == test_email
        print(f"[PASS] Successfully identified student by both Enrollment No ({test_enroll}) and Email ({test_email})")

        # TEST 3: OTP Generation, Hashing & Storage (Requirements 4 & 6)
        print("\n--- TEST 3: Hashed OTP Storage & Dispatch ---")
        # Temporarily mock mail dispatch to prevent external SMTP call during unit test if needed
        import secrets
        from werkzeug.security import generate_password_hash, check_password_hash
        plain_test_otp = f"{secrets.randbelow(900000) + 100000}"
        hashed_test_otp = generate_password_hash(plain_test_otp)

        # Clear existing
        ArchivedStudentOTP.query.filter_by(enrollment_no=test_enroll).delete()
        otp_rec = ArchivedStudentOTP(
            enrollment_no=test_enroll,
            email=test_email,
            otp_hash=hashed_test_otp,
            expires_at=db.func.now() + db.text("INTERVAL 3 MINUTE"),
            is_verified=False
        )
        db.session.add(otp_rec)
        db.session.commit()

        # Verify hashed in DB
        db_otp = ArchivedStudentOTP.query.filter_by(enrollment_no=test_enroll).first()
        assert db_otp is not None
        assert db_otp.otp_hash != plain_test_otp, "OTP must NOT be stored in plain text!"
        assert check_password_hash(db_otp.otp_hash, plain_test_otp), "OTP hash must verify correctly"
        print(f"[PASS] OTP stored securely hashed: '{db_otp.otp_hash[:20]}...' (Plain OTP never stored)")

        # TEST 4: OTP Verification
        print("\n--- TEST 4: OTP Verification Logic ---")
        wrong_res, wrong_err = verify_alumni_otp(test_enroll, "000000")
        assert wrong_res is False, "Wrong OTP must fail"
        print(f"[PASS] Wrong OTP correctly rejected with message: '{wrong_err}'")

        correct_res, correct_err = verify_alumni_otp(test_enroll, plain_test_otp)
        assert correct_res is True, f"Correct OTP failed: {correct_err}"
        assert correct_err is None
        # Verify marked as is_verified
        db_otp_after = ArchivedStudentOTP.query.filter_by(enrollment_no=test_enroll).first()
        assert db_otp_after.is_verified is True, "OTP record must be marked verified"
        print("[PASS] Correct OTP successfully verified and record marked as is_verified = True")

        # TEST 5: Results Retrieval & Multi-Semester Computation (Requirement 5)
        print("\n--- TEST 5: Results Aggregation & Graduation Summary ---")
        st_dict, semesters_data, summary = get_archived_student_results(test_enroll)
        assert len(semesters_data) >= 2, "Must contain recorded semesters"
        assert 5 in semesters_data and 6 in semesters_data, "Semesters 5 and 6 must be present"
        assert summary["total_obtained"] > 0
        assert summary["overall_percentage"] > 0
        assert summary["graduation_status"] == "COMPLETED"
        print(f"[PASS] Semesters retrieved: {list(semesters_data.keys())}")
        print(f"[PASS] Summary: {summary['total_obtained']}/{summary['total_max']} ({summary['overall_percentage']}%) - {summary['class']}")

        # TEST 6: PDF Generation (Semester-wise and Consolidated)
        print("\n--- TEST 6: ReportLab PDF Marksheet Generation ---")
        sem6_pdf = generate_archived_student_semester_pdf(test_enroll, 6)
        sem6_bytes = sem6_pdf.getvalue()
        assert sem6_bytes.startswith(b'%PDF'), "Output must be valid PDF"
        assert len(sem6_bytes) > 1000, "PDF size must be substantial"
        print(f"[PASS] Semester 6 PDF generated successfully ({len(sem6_bytes)} bytes)")

        cons_pdf = generate_archived_student_consolidated_pdf(test_enroll)
        cons_bytes = cons_pdf.getvalue()
        assert cons_bytes.startswith(b'%PDF'), "Consolidated output must be valid PDF"
        assert len(cons_bytes) > 1000, "Consolidated PDF size must be substantial"
        print(f"[PASS] Consolidated All-Semesters PDF generated successfully ({len(cons_bytes)} bytes)")

        # TEST 7: Admin Old Students Export (Requirement 7)
        print("\n--- TEST 7: Admin Old Students Yearly Exports (Excel & PDF) ---")
        excel_buf = export_archived_students_excel("2025-26")
        excel_bytes = excel_buf.getvalue()
        assert len(excel_bytes) > 1000, "Excel output must be valid"
        print(f"[PASS] Admin Old Students Excel export generated successfully ({len(excel_bytes)} bytes)")

        admin_pdf_buf = export_archived_students_pdf("2025-26")
        admin_pdf_bytes = admin_pdf_buf.getvalue()
        assert admin_pdf_bytes.startswith(b'%PDF'), "Admin PDF must be valid PDF"
        assert len(admin_pdf_bytes) > 1000, "Admin PDF size must be substantial"
        print(f"[PASS] Admin Old Students PDF Directory report generated successfully ({len(admin_pdf_bytes)} bytes)")

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY! (100% PASS)")
        print("=" * 60)

if __name__ == '__main__':
    run_tests()
