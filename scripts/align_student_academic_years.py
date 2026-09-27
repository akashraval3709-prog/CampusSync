"""
Script: Align Student Academic Years & Clean Database Indexes
CampusSync ERP
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from sqlalchemy import text
from models import Student, AcademicSetting

def align_database():
    with app.app_context():
        print("=" * 60)
        print("ALIGNING STUDENT ACADEMIC YEARS & CONSTRAINTS")
        print("=" * 60)

        # 1. Drop redundant old index uq_academic_course_roll if it exists
        try:
            db.session.execute(text("ALTER TABLE students DROP INDEX uq_academic_course_roll"))
            db.session.commit()
            print(" [PASS] Successfully dropped redundant constraint: uq_academic_course_roll")
        except Exception as e:
            db.session.rollback()
            print(f" [INFO] uq_academic_course_roll drop status: {e}")

        # 2. Ensure uq_academic_course_sem_roll exists
        indexes = [idx[2] for idx in db.session.execute(text("SHOW INDEX FROM students")).fetchall()]
        print(f"Current Student table indexes: {set(indexes)}")
        if 'uq_academic_course_sem_roll' not in indexes:
            try:
                db.session.execute(text(
                    "ALTER TABLE students ADD UNIQUE KEY uq_academic_course_sem_roll (academic_year, course, semester, roll_number)"
                ))
                db.session.commit()
                print(" [PASS] Created unique index: uq_academic_course_sem_roll")
            except Exception as e:
                db.session.rollback()
                print(f" [WARN] Index creation note: {e}")

        # 3. Update students according to user rules:
        # - Sem 1 & 2 -> 2026-27
        # - Sem 3 & 4 -> 2025-26
        # - Sem 5 & 6 -> 2024-25
        upd1 = db.session.execute(text("UPDATE students SET academic_year = '2026-27' WHERE semester IN (1, 2)")).rowcount
        upd2 = db.session.execute(text("UPDATE students SET academic_year = '2025-26' WHERE semester IN (3, 4)")).rowcount
        upd3 = db.session.execute(text("UPDATE students SET academic_year = '2024-25' WHERE semester IN (5, 6)")).rowcount
        db.session.commit()
        print(f" [PASS] Aligned Sem 1 & 2 students to '2026-27' ({upd1} records updated)")
        print(f" [PASS] Aligned Sem 3 & 4 students to '2025-26' ({upd2} records updated)")
        print(f" [PASS] Aligned Sem 5 & 6 students to '2024-25' ({upd3} records updated)")

        # 4. Also align central AcademicSetting.academic_year to '2026-27'
        setting = AcademicSetting.query.first()
        if setting:
            setting.academic_year = '2026-27'
            db.session.commit()
            print(f" [PASS] Central AcademicSetting updated to Year='{setting.academic_year}', Cycle='{setting.semester_cycle}'")

        # 5. Print resulting student distribution
        print("\n--- Current Students in Database ---")
        students = Student.query.order_by(Student.semester.asc(), Student.id.asc()).all()
        for s in students:
            print(f"ID: {s.id:<4} | Sem {s.semester} | Roll {s.roll_number:<3} | AY: {s.academic_year} | {s.full_name}")

        print("=" * 60)
        print("DATABASE REALIGNMENT COMPLETED SUCCESSFULLY!")
        print("=" * 60)

if __name__ == '__main__':
    align_database()
