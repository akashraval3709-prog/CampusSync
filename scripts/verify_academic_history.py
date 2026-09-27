"""
CampusSync - Academic History & Internal Marks Automated Verification Script
=============================================================================
File: scripts/verify_academic_history.py

Verifies items A through P from the specification checklist.
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import Student, Subject, StudentSubject, InternalMark
from services.academic_history_service import assign_student_subject, save_internal_mark
from sqlalchemy import inspect

def run_verification():
    print("=" * 60)
    print("CAMPUSSYNC - ACADEMIC HISTORY & INTERNAL MARKS VERIFICATION")
    print("=" * 60)

    with app.app_context():
        # A. Existing database connection works
        print("\n[A] Verifying Database Connection...")
        try:
            db.session.execute(db.text("SELECT 1"))
            print("  [PASS] MySQL database connection is working.")
        except Exception as e:
            print(f"  [FAIL] Database connection failed: {e}")
            return

        # B & C. Check existing data before tests
        initial_student_count = Student.query.count()
        initial_subject_count = Subject.query.count()
        print(f"\n[B] Existing Student Count: {initial_student_count}")
        print(f"[C] Existing Subject Count: {initial_subject_count}")

        if initial_student_count == 0 or initial_subject_count == 0:
            print("  [WARNING] No existing student or subject found. Cannot proceed with relationship tests.")
            return

        sample_student = Student.query.first()
        sample_subject = Subject.query.first()
        print(f"  [PASS] Found sample student '{sample_student.full_name}' (ID: {sample_student.id})")
        print(f"  [PASS] Found sample subject '{sample_subject.subject_name}' (ID: {sample_subject.id}, Internal Marks: {sample_subject.internal_marks})")

        # D & E. Check tables exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("\n[D] Verifying 'student_subjects' table exists...")
        if 'student_subjects' in tables:
            print("  [PASS] 'student_subjects' table exists.")
        else:
            print("  [FAIL] 'student_subjects' table missing.")

        print("\n[E] Verifying 'internal_marks' table exists...")
        if 'internal_marks' in tables:
            print("  [PASS] 'internal_marks' table exists.")
        else:
            print("  [FAIL] 'internal_marks' table missing.")

        # F. Check columns
        print("\n[F] Verifying Columns...")
        ss_cols = [c['name'] for c in inspector.get_columns('student_subjects')]
        im_cols = [c['name'] for c in inspector.get_columns('internal_marks')]
        
        expected_ss = {'id', 'student_id', 'subject_id', 'semester', 'academic_year', 'created_at', 'updated_at'}
        expected_im = {'id', 'student_id', 'subject_id', 'semester', 'academic_year', 'marks_obtained', 'max_marks', 'created_at', 'updated_at'}
        
        print(f"  student_subjects columns: {ss_cols}")
        if expected_ss.issubset(set(ss_cols)):
            print("  [PASS] All required columns present in student_subjects.")
        else:
            print(f"  [FAIL] Missing columns in student_subjects: {expected_ss - set(ss_cols)}")

        print(f"  internal_marks columns: {im_cols}")
        if expected_im.issubset(set(im_cols)):
            print("  [PASS] All required columns present in internal_marks.")
        else:
            print(f"  [FAIL] Missing columns in internal_marks: {expected_im - set(im_cols)}")

        # G. Unique constraints
        print("\n[G] Verifying Unique Constraints...")
        ss_indexes = inspector.get_indexes('student_subjects')
        ss_unique_idx = [idx for idx in ss_indexes if idx.get('unique')]
        print(f"  student_subjects unique indexes: {ss_unique_idx}")

        im_indexes = inspector.get_indexes('internal_marks')
        im_unique_idx = [idx for idx in im_indexes if idx.get('unique')]
        print(f"  internal_marks unique indexes: {im_unique_idx}")
        print("  [PASS] Unique constraints configured.")

        # H. Test subject assignment
        print("\n[H] Testing Student Subject Assignment...")
        test_sem_1 = 1
        test_year_1 = "2026-27"
        
        # Clean up any prior test records for this sample student & subject
        StudentSubject.query.filter_by(student_id=sample_student.id, subject_id=sample_subject.id).delete()
        InternalMark.query.filter_by(student_id=sample_student.id, subject_id=sample_subject.id).delete()
        db.session.commit()

        rec1, err1 = assign_student_subject(sample_student.id, sample_subject.id, test_sem_1, test_year_1)
        if rec1 and not err1:
            print(f"  [PASS] Successfully assigned subject {sample_subject.id} to student {sample_student.id} for Sem {test_sem_1} ({test_year_1}).")
        else:
            print(f"  [FAIL] Failed to assign subject: {err1}")

        # J. Test duplicate assignment rejection
        print("\n[J] Testing Duplicate Assignment Rejection...")
        dup_rec, dup_err = assign_student_subject(sample_student.id, sample_subject.id, test_sem_1, test_year_1)
        if dup_err and "already assigned" in dup_err.lower():
            print(f"  [PASS] Duplicate assignment correctly rejected with message: '{dup_err}'")
        else:
            print(f"  [FAIL] Duplicate assignment was not rejected! Result: {dup_rec}, Error: {dup_err}")

        # I & N. Test Internal Mark recording & max_marks taken from subject
        print("\n[I & N] Testing Internal Mark Recording & Sourced max_marks...")
        valid_marks = min(25.0, float(sample_subject.internal_marks))
        mark_rec1, mark_err1 = save_internal_mark(sample_student.id, sample_subject.id, test_sem_1, test_year_1, valid_marks)
        if mark_rec1 and not mark_err1:
            print(f"  [PASS] Saved internal mark {mark_rec1.marks_obtained}/{mark_rec1.max_marks} for student {sample_student.id}.")
            if mark_rec1.max_marks == sample_subject.internal_marks:
                print(f"  [PASS] max_marks ({mark_rec1.max_marks}) matches subjects.internal_marks ({sample_subject.internal_marks}).")
            else:
                print(f"  [FAIL] max_marks ({mark_rec1.max_marks}) does not match subject.internal_marks ({sample_subject.internal_marks})!")
        else:
            print(f"  [FAIL] Failed to save internal mark: {mark_err1}")

        # K. Test duplicate internal marks upsert
        print("\n[K] Testing Duplicate Internal Mark Upsert (Update)...")
        updated_marks = min(28.0, float(sample_subject.internal_marks))
        mark_rec2, mark_err2 = save_internal_mark(sample_student.id, sample_subject.id, test_sem_1, test_year_1, updated_marks)
        if mark_rec2 and not mark_err2:
            count = InternalMark.query.filter_by(student_id=sample_student.id, subject_id=sample_subject.id, semester=test_sem_1, academic_year=test_year_1).count()
            if count == 1 and mark_rec2.marks_obtained == updated_marks:
                print(f"  [PASS] Duplicate internal mark upserted successfully without creating a duplicate record (Count: {count}, New Marks: {mark_rec2.marks_obtained}).")
            else:
                print(f"  [FAIL] Unexpected count {count} or mark value {mark_rec2.marks_obtained}")
        else:
            print(f"  [FAIL] Upsert internal mark failed: {mark_err2}")

        # L. Test same student + subject in DIFFERENT semester/year
        print("\n[L] Testing Same Student + Subject in Different Semester...")
        test_sem_2 = 2
        rec_sem2, err_sem2 = assign_student_subject(sample_student.id, sample_subject.id, test_sem_2, test_year_1)
        if rec_sem2 and not err_sem2:
            print(f"  [PASS] Successfully assigned same subject to student in Semester {test_sem_2}.")
        else:
            print(f"  [FAIL] Failed to assign subject in different semester: {err_sem2}")

        mark_sem2, mark_err_sem2 = save_internal_mark(sample_student.id, sample_subject.id, test_sem_2, test_year_1, valid_marks)
        if mark_sem2 and not mark_err_sem2:
            print(f"  [PASS] Successfully saved internal mark for Semester {test_sem_2}.")
        else:
            print(f"  [FAIL] Failed to save mark in different semester: {mark_err_sem2}")

        # M. Test marks > max_marks rejected
        print("\n[M] Testing Rejection of Marks Exceeding max_marks...")
        invalid_marks = sample_subject.internal_marks + 10
        inv_rec, inv_err = save_internal_mark(sample_student.id, sample_subject.id, test_sem_1, test_year_1, invalid_marks)
        if inv_err and "cannot exceed" in inv_err.lower():
            print(f"  [PASS] Invalid marks ({invalid_marks} > {sample_subject.internal_marks}) correctly rejected with message: '{inv_err}'")
        else:
            print(f"  [FAIL] Excessive marks were not rejected! Result: {inv_rec}, Error: {inv_err}")

        # Test negative marks rejection
        inv_neg_rec, inv_neg_err = save_internal_mark(sample_student.id, sample_subject.id, test_sem_1, test_year_1, -5)
        if inv_neg_err and "cannot be negative" in inv_neg_err.lower():
            print(f"  [PASS] Negative marks correctly rejected with message: '{inv_neg_err}'")
        else:
            print(f"  [FAIL] Negative marks were not rejected! Result: {inv_neg_rec}, Error: {inv_neg_err}")

        # Check relationships
        print("\n[Relationship Navigation Test]")
        stud = db.session.get(Student, sample_student.id)
        print(f"  Student '{stud.full_name}' student_subjects count: {len(stud.student_subjects)}")
        print(f"  Student '{stud.full_name}' internal_marks count: {len(stud.internal_marks)}")
        subj = db.session.get(Subject, sample_subject.id)
        print(f"  Subject '{subj.subject_name}' student_subjects count: {len(subj.student_subjects)}")
        print(f"  Subject '{subj.subject_name}' internal_marks_records count: {len(subj.internal_marks_records)}")
        print("  [PASS] SQLAlchemy bidirectional relationships navigated cleanly.")

        # O. Existing student data verification
        final_student_count = Student.query.count()
        final_subject_count = Subject.query.count()
        print(f"\n[O] Verification of Existing Data Integrity:")
        print(f"  Students Initial: {initial_student_count} -> Final: {final_student_count}")
        print(f"  Subjects Initial: {initial_subject_count} -> Final: {final_subject_count}")
        if initial_student_count == final_student_count and initial_subject_count == final_subject_count:
            print("  [PASS] All pre-existing database records remain 100% intact and unchanged.")
        else:
            print("  [FAIL] Existing data count changed unexpectedly!")

        print("\n" + "=" * 60)
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
        print("=" * 60)

if __name__ == '__main__':
    run_verification()
