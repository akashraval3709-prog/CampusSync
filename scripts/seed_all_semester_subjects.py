"""
CampusSync ERP - Seed & Sync All Semester BCA Subjects (NEP-2020)
===================================================================
File: scripts/seed_all_semester_subjects.py

Populates/updates all official HNGU BCA NEP-2020 syllabus subjects
for Semesters 1, 2, 3, 4, 5, and 6 into MySQL database.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models import Subject

ALL_SUBJECTS = [
    # SEMESTER 1
    {"semester": 1, "code": "BCA101", "name": "Fundamental of Programming Language - C", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 1, "code": "BCA101A", "name": "Database Management System & PC Packages", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 1, "code": "BCA102", "name": "Practical - Programming in C", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 1, "code": "BCA102A", "name": "Practical - MS Office", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 1, "code": "BCA103", "name": "Computer Organization", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 1, "code": "BCA104", "name": "Communication Skills-I", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 1, "code": "BCA105", "name": "Understanding India", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 1, "code": "BCA106", "name": "Mathematics - I", "type": "Theory", "credits": 2, "internal": 25, "external": 25},

    # SEMESTER 2
    {"semester": 2, "code": "BCA201", "name": "Advance Programming Language - C", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 2, "code": "BCA201A", "name": "Internet & Web Designing", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 2, "code": "BCA202", "name": "Practical - Advance Programming in C", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 2, "code": "BCA202A", "name": "Practical - Internet & Web Designing", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 2, "code": "BCA203", "name": "Electronic Commerce (E-Commerce)", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 2, "code": "BCA204", "name": "Communication Skills-II", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 2, "code": "BCA205", "name": "Integrated Personality Development Course - I", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 2, "code": "BCA206", "name": "Mathematics-II", "type": "Theory", "credits": 2, "internal": 25, "external": 25},

    # SEMESTER 3
    {"semester": 3, "code": "BCA301", "name": "Data Structure", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 3, "code": "BCA301A", "name": "Relational Database Management System", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 3, "code": "BCA301B", "name": "Practical - Data Structure", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 3, "code": "BCA301C", "name": "Practical - RDBMS", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 3, "code": "BCA303", "name": "Computer Network", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 3, "code": "BCA304", "name": "Environmental Science", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 3, "code": "BCA305", "name": "Health Education", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 3, "code": "BCA306", "name": "Computer Security - I", "type": "Theory", "credits": 2, "internal": 25, "external": 25},

    # SEMESTER 4
    {"semester": 4, "code": "BCA401", "name": "Python Programming", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 4, "code": "BCA401A", "name": "Web Development Using PHP", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 4, "code": "BCA401B", "name": "Practical - Python Programming", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 4, "code": "BCA401C", "name": "Practical - PHP", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 4, "code": "BCA402", "name": "System Analysis and Design", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 4, "code": "BCA404", "name": "Personality Development & Reasoning Ability", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 4, "code": "BCA405", "name": "Integrated Personality Development Course - II", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 4, "code": "BCA406", "name": "Computer Security - II", "type": "Theory", "credits": 2, "internal": 25, "external": 25},

    # SEMESTER 5
    {"semester": 5, "code": "BCA501", "name": "JAVA Programming", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 5, "code": "BCA501A", "name": "GUI Programming Using C# .net", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 5, "code": "BCA501B", "name": "Practical - JAVA Programming", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 5, "code": "BCA501C", "name": "Practical - GUI Programming", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 5, "code": "BCA502", "name": "Software Engineering", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 5, "code": "BCA502A", "name": "Operating System", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 5, "code": "BCA506", "name": "Project Development", "type": "Practical", "credits": 2, "internal": 25, "external": 25},

    # SEMESTER 6
    {"semester": 6, "code": "BCA601", "name": "Advance JAVA Programming", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 6, "code": "BCA601A", "name": "Web Development Using Asp.Net", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 6, "code": "BCA601B", "name": "Practical - Advance JAVA Programming", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 6, "code": "BCA601C", "name": "Practical - Asp.Net", "type": "Practical", "credits": 2, "internal": 25, "external": 25},
    {"semester": 6, "code": "BCA602", "name": "Unified Modeling Language (UML)", "type": "Theory", "credits": 4, "internal": 50, "external": 50},
    {"semester": 6, "code": "BCA604", "name": "Digital Communication and Marketing Skills", "type": "Theory", "credits": 2, "internal": 25, "external": 25},
    {"semester": 6, "code": "BCA607", "name": "Industrial Project", "type": "Practical", "credits": 4, "internal": 50, "external": 50}
]


def seed_subjects():
    with app.app_context():
        print("==================================================")
        print("Seeding/Syncing All Semester BCA Subjects (NEP-2020)")
        print("==================================================")

        added_count = 0
        updated_count = 0

        for data in ALL_SUBJECTS:
            code = data["code"].strip().upper()
            sem = data["semester"]
            name = data["name"].strip()
            stype = data["type"]
            credits = data["credits"]
            internal = data["internal"]
            external = data["external"]
            total = internal + external

            # Check existing subject by code or code matching existing ID
            existing = Subject.query.filter_by(course='BCA', subject_code=code).first()

            if not existing:
                # Secondary lookup by semester + matching name
                existing = Subject.query.filter(
                    Subject.course == 'BCA',
                    Subject.semester == sem,
                    Subject.subject_name.ilike(f"%{name[:10]}%")
                ).first()

            if existing:
                existing.subject_code = code
                existing.subject_name = name
                existing.semester = sem
                existing.subject_type = stype
                existing.credits = credits
                existing.internal_marks = internal
                existing.external_marks = external
                existing.total_marks = total
                existing.status = 'Active'
                updated_count += 1
                print(f"[UPDATED] Sem {sem} - {code}: {name} ({stype}, Int: {internal})")
            else:
                new_sub = Subject(
                    subject_code=code,
                    subject_name=name,
                    course='BCA',
                    semester=sem,
                    subject_type=stype,
                    credits=credits,
                    internal_marks=internal,
                    external_marks=external,
                    total_marks=total,
                    status='Active'
                )
                db.session.add(new_sub)
                added_count += 1
                print(f"[ADDED]   Sem {sem} - {code}: {name} ({stype}, Int: {internal})")

        db.session.commit()

        # Display final totals
        total_subs = Subject.query.filter_by(course='BCA', status='Active').count()
        print("==================================================")
        print(f"Sync Complete! Added: {added_count}, Updated: {updated_count}")
        print(f"Total Active BCA Subjects in Database: {total_subs}")
        print("==================================================")


if __name__ == '__main__':
    seed_subjects()
