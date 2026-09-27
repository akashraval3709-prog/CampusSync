"""
Migration Script: Add Attendance Threshold Columns to college_settings table
=============================================================================
Adds:
- min_overall_attendance (FLOAT DEFAULT 75.0 NOT NULL)
- min_subject_attendance (FLOAT DEFAULT 75.0 NOT NULL)
- attendance_warning_threshold (FLOAT DEFAULT 60.0 NOT NULL)
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        print("Starting college_settings migration for attendance thresholds...")
        
        inspector = db.inspect(db.engine)
        existing_cols = [col['name'] for col in inspector.get_columns('college_settings')]
        print(f"Existing columns in 'college_settings': {existing_cols}")

        with db.engine.connect() as conn:
            if 'min_overall_attendance' not in existing_cols:
                conn.execute(text("ALTER TABLE college_settings ADD COLUMN min_overall_attendance FLOAT NOT NULL DEFAULT 75.0"))
                print("Added column: min_overall_attendance")
            else:
                print("Column min_overall_attendance already exists.")

            if 'min_subject_attendance' not in existing_cols:
                conn.execute(text("ALTER TABLE college_settings ADD COLUMN min_subject_attendance FLOAT NOT NULL DEFAULT 75.0"))
                print("Added column: min_subject_attendance")
            else:
                print("Column min_subject_attendance already exists.")

            if 'attendance_warning_threshold' not in existing_cols:
                conn.execute(text("ALTER TABLE college_settings ADD COLUMN attendance_warning_threshold FLOAT NOT NULL DEFAULT 60.0"))
                print("Added column: attendance_warning_threshold")
            else:
                print("Column attendance_warning_threshold already exists.")

            conn.commit()

        print("[SUCCESS] college_settings migration completed successfully!")

if __name__ == '__main__':
    run_migration()
