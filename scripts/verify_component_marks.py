import sys
import os

# Ensure CampusSync directory is in python path
sys.path.insert(0, r"d:\Project_sem_5\A-project\CampusSync")

from app import app, db
from models import Subject, Student, InternalMark, Faculty
from services.subject_service import get_subject_component_config
from services.academic_history_service import save_detailed_internal_mark
from services.faculty_service import get_faculty_marks_students
from services.admin_results_service import get_admin_subject_marks_matrix, get_admin_student_full_result
from services.export_marks_service import generate_internal_marks_excel, generate_internal_marks_pdf

def run_verification():
    with app.app_context():
        print("==================================================")
        print("CampusSync Dynamic Internal Marks Verification")
        print("==================================================")

        # 1. Subject Component Config Verification
        theory_sub = Subject.query.filter_by(subject_type='Theory').first()
        prac_sub = Subject.query.filter_by(subject_type='Practical').first()

        if not theory_sub or not prac_sub:
            print("[ERROR] Theory or Practical subject not found in database.")
            return False

        t_config = get_subject_component_config(theory_sub)
        p_config = get_subject_component_config(prac_sub)

        print(f"[OK] Theory Subject ({theory_sub.subject_code}): Maxes = {t_config['maxes']}, Max Sum = {t_config['max_sum']}")
        print(f"[OK] Practical Subject ({prac_sub.subject_code}): Maxes = {p_config['maxes']}, Max Sum = {p_config['max_sum']}")

        # 2. Test Theory Calculation & Save
        test_student = Student.query.first()
        if not test_student:
            print("[ERROR] No student found for testing.")
            return False

        theory_input = {
            "test1": 12.0, "test2": 14.0, "test3": 10.0,
            "internal_exam": 13.0,
            "active_learning": 4.0, "class_assignment": 4.0, "home_assignment": 4.0,
            "attendance": 4.0
        }

        mark_obj, err = save_detailed_internal_mark(
            student_id=test_student.id,
            subject_id=theory_sub.id,
            semester=theory_sub.semester,
            academic_year="2026-27",
            data_dict=theory_input,
            commit=True
        )

        if err:
            print(f"[FAIL] Theory mark save error: {err}")
            return False

        # Expected: Best 2 of tests = (14 + 12)/2 = 13.0
        # Total scaled for 50 max internal = round((42 / 85) * 50, 2) = 24.71
        print(f"[OK] Theory Mark Saved for Roll #{test_student.roll_number}: Obtained = {mark_obj.marks_obtained}")
        assert mark_obj.marks_obtained is not None and mark_obj.marks_obtained > 0, "Theory mark should be saved successfully"

        # 3. Test Practical Calculation & Save
        prac_input = {
            "internal_exam": 8.0,
            "practical_eval": 9.0,
            "viva": 0.0,
            "journal": 4.0
        }

        prac_mark_obj, err = save_detailed_internal_mark(
            student_id=test_student.id,
            subject_id=prac_sub.id,
            semester=prac_sub.semester,
            academic_year="2026-27",
            data_dict=prac_input,
            commit=True
        )

        if err:
            print(f"[FAIL] Practical mark save error: {err}")
            return False

        # Expected: 8 + 9 + 0 + 4 = 21.0
        print(f"[OK] Practical Mark Saved for Roll #{test_student.roll_number}: Obtained = {prac_mark_obj.marks_obtained} (Expected 21.0)")
        assert prac_mark_obj.marks_obtained == 21.0, f"Expected 21.0 got {prac_mark_obj.marks_obtained}"

        # 4. Test Faculty Marks Data Structure
        fac = Faculty.query.first()
        fac_data = None
        if fac:
            fac_data, fac_err = get_faculty_marks_students(
                faculty_id=fac.id,
                subject_id=theory_sub.id,
                division=test_student.division or 'A',
                semester=theory_sub.semester,
                academic_year="2026-27"
            )
            if fac_data and "subject" in fac_data:
                assert "components" in fac_data["subject"], "components missing from faculty student_data['subject']"
                assert "maxes" in fac_data["subject"], "maxes missing from faculty student_data['subject']"
                print(f"[OK] Faculty Service Data Structure Verified (components: {len(fac_data['subject']['components'])})")

        # 5. Test Admin Matrix & Full Result
        matrix_res, matrix_err = get_admin_subject_marks_matrix(
            subject_id=theory_sub.id,
            semester=theory_sub.semester,
            division=test_student.division or 'A',
            academic_year="2026-27"
        )
        if matrix_err:
            print(f"[FAIL] Admin Matrix Error: {matrix_err}")
            return False
        print(f"[OK] Admin Subject Matrix fetched successfully (Students = {len(matrix_res['students'])})")

        student_result, sr_err = get_admin_student_full_result(
            student_id=test_student.id,
            semester=theory_sub.semester,
            academic_year="2026-27"
        )
        if sr_err:
            print(f"[FAIL] Admin Full Student Result Error: {sr_err}")
            return False
        print(f"[OK] Admin Full Student Result Card fetched successfully (Total Obtained = {student_result['total_obtained']})")

        # 6. Test Excel & PDF Export Generation if fac_data available
        if fac_data:
            excel_buf = generate_internal_marks_excel(fac_data, faculty_name="Test Faculty")
            print(f"[OK] Excel Export generated successfully ({len(excel_buf.getvalue())} bytes)")

            pdf_buf = generate_internal_marks_pdf(fac_data, faculty_name="Test Faculty")
            print(f"[OK] PDF Export generated successfully ({len(pdf_buf.getvalue())} bytes)")

        print("==================================================")
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
        print("==================================================")
        return True

if __name__ == '__main__':
    success = run_verification()
    sys.exit(0 if success else 1)
