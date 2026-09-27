"""
Verification Script: Result Declaration and Student Marksheet Download
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Student, CollegeSetting, ResultDeclaration
from services.result_declaration_service import is_result_declared, toggle_result_declaration, get_declaration_status
from services.admin_results_service import get_admin_student_full_result
from services.export_marks_service import generate_student_result_pdf

def test_flow():
    with app.app_context():
        print("==================================================")
        print("1. Verifying College Settings (Seal & Signature)")
        print("==================================================")
        cs = CollegeSetting.query.first()
        assert cs is not None, "CollegeSetting must exist"
        print(f"College: {cs.college_name}")
        print(f"Stamp file: {cs.college_stamp}")
        print(f"Signature file: {cs.principal_signature}")
        assert cs.college_stamp is not None, "Stamp file must not be None"
        assert cs.principal_signature is not None, "Signature file must not be None"
        print("[PASS] College Settings verified.\n")

        print("==================================================")
        print("2. Verifying Result Declaration Safeguard & Pending Check")
        print("==================================================")
        ay = '2026-27'
        sem = 5
        div = 'A'

        # Ensure starting in undeclared state
        decl = ResultDeclaration.query.filter_by(academic_year=ay, semester=sem, division='All').first()
        if decl:
            decl.is_declared = False
            db.session.commit()

        # Step A: Check is_result_declared is False
        assert not is_result_declared(ay, sem, div), "Should be False initially"
        print(f"[OK] Semester {sem} ({ay}) declared status initially: False")

        # Step B: Check faculty submission status for Semester 5 (has 1 finalized, 6 pending)
        from services.result_declaration_service import get_semester_faculty_submission_status
        sub_status = get_semester_faculty_submission_status(ay, sem, 'All')
        print(f"[OK] Total subjects: {sub_status['total_subjects']}, Finalized: {sub_status['finalized_subjects']}, Pending: {len(sub_status['pending_subjects'])}")
        assert sub_status['is_all_finalized'] is False, "Sem 5 should not be all finalized"

        # Step C: Admin attempts to declare result (MUST FAIL because subjects are pending)
        d_rec, is_decl, msg = toggle_result_declaration(ay, sem, 'All', admin_id=1)
        assert d_rec is None and is_decl is False, "Publishing incomplete results must be blocked"
        assert "All subjects must be final-saved" in msg, f"Unexpected message: {msg}"
        print(f"[OK] Safeguard successfully blocked premature publication: {msg}")
        print("[PASS] Incomplete result publication safeguard verified.\n")

        print("==================================================")
        print("3. Verifying Student Marksheet PDF Generation")
        print("==================================================")
        # Find an active student
        st = Student.query.filter_by(status='Active').first()
        assert st is not None, "At least one active student must exist"
        print(f"Testing with Student: {st.full_name} (ID: {st.id}, Sem: {st.semester})")

        res_data, err = get_admin_student_full_result(st.id, semester=st.semester, academic_year=ay)
        assert err is None, f"Full result error: {err}"
        assert res_data is not None, "res_data must not be None"

        pdf_buf = generate_student_result_pdf(res_data)
        pdf_bytes = pdf_buf.getvalue()
        assert len(pdf_bytes) > 1000, "PDF bytes must be generated"
        print(f"[OK] PDF successfully generated! Size: {len(pdf_bytes)} bytes")

        # Save to scratch for verification
        scratch_dir = os.path.join(os.path.dirname(__file__), '..', 'scratch')
        os.makedirs(scratch_dir, exist_ok=True)
        pdf_path = os.path.join(scratch_dir, 'verified_student_marksheet.pdf')
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"[OK] PDF saved to {pdf_path}")
        print("[PASS] PDF generation verified.\n")

        print("==================================================")
        print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
        print("==================================================")

if __name__ == '__main__':
    test_flow()
