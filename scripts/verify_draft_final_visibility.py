"""
CampusSync ERP - Draft vs Final Save Visibility Test Script
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import InternalMark, Student, Subject
from services.academic_history_service import save_detailed_internal_mark
from services.admin_results_service import get_admin_subject_marks_matrix, get_admin_student_full_result, is_mark_final

def run_test():
    with app.app_context():
        st_id = 127
        sub_id = 1
        sem = 1
        ay = '2026-27'
        
        print("==================================================")
        print("Testing Draft Save vs Final Save Visibility Rules")
        print("==================================================")
        
        # 1. Draft Save
        mark, err = save_detailed_internal_mark(
            student_id=st_id,
            subject_id=sub_id,
            semester=sem,
            academic_year=ay,
            data_dict={
                'test1': 10, 'test2': 12, 'test3': 14,
                'internal_exam': 14, 'active_learning': 4,
                'class_assignment': 4, 'home_assignment': 4, 'attendance': 4
            },
            save_type='draft',
            commit=True
        )
        assert err is None, f"Draft save failed: {err}"
        print(f"[OK] Draft Mark Saved (is_mark_final = {is_mark_final(mark)})")

        # Check Student visibility
        m_student = InternalMark.query.filter_by(student_id=st_id, subject_id=sub_id, semester=sem, academic_year=ay).first()
        print(f"[OK] Student Results View: Obtained = {m_student.marks_obtained}")
        assert m_student.marks_obtained is not None, "Student MUST see Draft marks!"

        # Check Admin visibility (Matrix)
        matrix_data, _ = get_admin_subject_marks_matrix(subject_id=sub_id, division='A', semester=sem, academic_year=ay)
        st_admin_entry = [s for s in matrix_data['students'] if s['id'] == st_id][0]
        print(f"[OK] Admin Matrix View: Obtained = {st_admin_entry['marks_obtained']}, Status = {st_admin_entry['marks_status']}")
        assert st_admin_entry['marks_obtained'] is None, "Admin matrix MUST NOT show Draft marks!"

        # Check Admin visibility (Student Card)
        card_data, _ = get_admin_student_full_result(student_id=st_id, semester=sem, academic_year=ay)
        sub_card_entry = [s for s in card_data['results'] if s['subject_id'] == sub_id][0]
        print(f"[OK] Admin Full Student Card View: Obtained = {sub_card_entry['marks_obtained']}")
        assert sub_card_entry['marks_obtained'] is None, "Admin student card MUST NOT show Draft marks!"

        # 2. Final Save
        mark_final, err2 = save_detailed_internal_mark(
            student_id=st_id,
            subject_id=sub_id,
            semester=sem,
            academic_year=ay,
            data_dict={
                'test1': 10, 'test2': 12, 'test3': 14,
                'internal_exam': 14, 'active_learning': 4,
                'class_assignment': 4, 'home_assignment': 4, 'attendance': 4
            },
            save_type='final',
            commit=True
        )
        assert err2 is None, f"Final save failed: {err2}"
        print(f"[OK] Final Mark Saved (is_mark_final = {is_mark_final(mark_final)})")

        # Check Student visibility
        m_student_final = InternalMark.query.filter_by(student_id=st_id, subject_id=sub_id, semester=sem, academic_year=ay).first()
        print(f"[OK] Student Results View: Obtained = {m_student_final.marks_obtained}")
        assert m_student_final.marks_obtained is not None, "Student MUST see Final marks!"

        # Check Admin visibility (Matrix)
        matrix_final_data, _ = get_admin_subject_marks_matrix(subject_id=sub_id, division='A', semester=sem, academic_year=ay)
        st_admin_final_entry = [s for s in matrix_final_data['students'] if s['id'] == st_id][0]
        print(f"[OK] Admin Matrix View: Obtained = {st_admin_final_entry['marks_obtained']}, Status = {st_admin_final_entry['marks_status']}")
        assert st_admin_final_entry['marks_obtained'] == m_student_final.marks_obtained, "Admin matrix MUST show Final marks!"

        # Check Admin visibility (Student Card)
        card_final_data, _ = get_admin_student_full_result(student_id=st_id, semester=sem, academic_year=ay)
        sub_card_final_entry = [s for s in card_final_data['results'] if s['subject_id'] == sub_id][0]
        print(f"[OK] Admin Full Student Card View: Obtained = {sub_card_final_entry['marks_obtained']}")
        assert sub_card_final_entry['marks_obtained'] == m_student_final.marks_obtained, "Admin student card MUST show Final marks!"

        print("==================================================")
        print("ALL DRAFT VS FINAL VISIBILITY TESTS PASSED!")
        print("==================================================")

if __name__ == '__main__':
    run_test()
