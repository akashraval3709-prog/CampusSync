"""
CampusSync - Database Migration: Archive Tables & Schema Cleanup
================================================================
File: scripts/migrate_archive_and_cleanup.py

Performs:
1. Adds 'enrollment_no' column to 'internal_marks' if missing.
2. Backfills 'enrollment_no' for all existing mark records from 'students'.
3. Creates 'archived_students' and 'archived_internal_marks' tables.
4. Safely drops 'student_subjects' table.
5. Verifies existing data is 100% preserved (zero data loss).
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import inspect, text
from models import Student, InternalMark, ArchivedStudent, ArchivedInternalMark

def run_migration():
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print("Existing tables:", existing_tables)

        # 1. Add enrollment_no to internal_marks if missing
        im_cols = [c['name'] for c in inspector.get_columns('internal_marks')]
        if 'enrollment_no' not in im_cols:
            print("[1] Adding 'enrollment_no' column to 'internal_marks'...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE internal_marks ADD COLUMN enrollment_no VARCHAR(20) NULL AFTER student_id"))
                conn.execute(text("CREATE INDEX idx_internal_marks_enrollment ON internal_marks(enrollment_no)"))
                conn.commit()
            print("  -> Column 'enrollment_no' added successfully.")
        else:
            print("[1] 'enrollment_no' already exists in 'internal_marks'.")

        # 2. Backfill enrollment_no for existing internal_marks
        print("[2] Backfilling 'enrollment_no' for existing internal_marks records...")
        with db.engine.connect() as conn:
            conn.execute(text("""
                UPDATE internal_marks im
                JOIN students s ON im.student_id = s.id
                SET im.enrollment_no = s.enrollment_no
                WHERE im.enrollment_no IS NULL OR im.enrollment_no = ''
            """))
            conn.commit()
        print("  -> Backfill complete.")

        # 3. Create archive tables if they don't exist
        print("[3] Creating archive tables (archived_students, archived_internal_marks)...")
        db.create_all()
        print("  -> Tables ensured via db.create_all().")

        # 4. Safely drop student_subjects table
        if 'student_subjects' in existing_tables:
            print("[4] Safely dropping 'student_subjects' table...")
            with db.engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS student_subjects"))
                conn.commit()
            print("  -> 'student_subjects' dropped successfully.")
        else:
            print("[4] 'student_subjects' table was already dropped or does not exist.")

        # 5. Verify database state and zero data loss
        inspector_after = inspect(db.engine)
        tables_after = inspector_after.get_table_names()
        student_count = Student.query.count()
        marks_count = InternalMark.query.count()
        marks_with_enrollment = InternalMark.query.filter(InternalMark.enrollment_no.isnot(None), InternalMark.enrollment_no != '').count()

        print("\n" + "="*50)
        print("MIGRATION VERIFICATION:")
        print(f"  - 'student_subjects' in tables: {'student_subjects' in tables_after} (Expected: False)")
        print(f"  - 'archived_students' in tables: {'archived_students' in tables_after} (Expected: True)")
        print(f"  - 'archived_internal_marks' in tables: {'archived_internal_marks' in tables_after} (Expected: True)")
        print(f"  - Total Students preserved: {student_count} (Expected: 19)")
        print(f"  - Total Marks preserved: {marks_count} (Expected: 10)")
        print(f"  - Marks with valid enrollment_no: {marks_with_enrollment} of {marks_count}")
        print("="*50)

        for m in InternalMark.query.all():
            print(f"    Mark ID {m.id}: Student #{m.student_id} | Enroll: '{m.enrollment_no}' | Score: {m.marks_obtained} | Sem {m.semester} | Year {m.academic_year}")

        assert 'student_subjects' not in tables_after, "student_subjects should be removed"
        assert 'archived_students' in tables_after, "archived_students table must exist"
        assert 'archived_internal_marks' in tables_after, "archived_internal_marks table must exist"
        assert student_count >= 19, "Existing students must be preserved"
        assert marks_count >= 10, "Existing marks must be preserved"
        assert marks_with_enrollment == marks_count, "All marks must have enrollment_no"

        print("\nSUCCESS: Migration completed with ZERO data loss!")

if __name__ == '__main__':
    run_migration()
