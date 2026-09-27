"""
CampusSync - Academic History & Internal Marks Service
======================================================
File: services/academic_history_service.py

Provides backend business logic, validations, and database operations for:
1. Student Subject assignments (academic history per semester/year)
2. Internal Marks (marks scored per student/subject/semester/year)
"""

from extensions import db
from models import Student, Subject, InternalMark



def save_internal_mark(student_id, subject_id, semester, academic_year, marks_obtained):
    """
    Save or update (upsert) internal marks for a student, subject, semester, and academic year.
    
    Validation:
    - student must exist
    - subject must exist
    - semester must be valid
    - academic_year must not be empty
    - marks_obtained must be numeric (int/float)
    - marks_obtained must be >= 0
    - marks_obtained must not exceed subject.internal_marks (max_marks)
    - max_marks is dynamically fetched from subjects.internal_marks
    - updates existing record if duplicate constraint matches
    """
    try:
        if not student_id or not isinstance(student_id, int):
            return None, "Invalid student ID."

        if not subject_id or not isinstance(subject_id, int):
            return None, "Invalid subject ID."

        try:
            semester = int(semester)
            if semester <= 0 or semester > 12:
                return None, "Semester must be a valid number between 1 and 12."
        except (ValueError, TypeError):
            return None, "Semester must be a valid integer."

        if not academic_year or not str(academic_year).strip():
            return None, "Academic Year is required."

        academic_year = str(academic_year).strip()

        # Validate numeric marks_obtained
        try:
            marks_obtained = float(marks_obtained)
        except (ValueError, TypeError):
            return None, "Marks obtained must be a numeric value."

        if marks_obtained < 0:
            return None, "Marks obtained cannot be negative."

        # Verify student existence
        student = db.session.get(Student, student_id)
        if not student:
            return None, f"Student with ID {student_id} does not exist."

        # Verify subject existence and fetch default internal_marks as max_marks
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return None, f"Subject with ID {subject_id} does not exist."

        max_marks = subject.internal_marks
        if max_marks is None:
            max_marks = 30  # Default fallback if null in DB

        if marks_obtained > max_marks:
            return None, f"Marks obtained ({marks_obtained}) cannot exceed maximum internal marks ({max_marks}) for '{subject.subject_name}'."

        # Check existing record for upsert
        existing_mark = InternalMark.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            semester=semester,
            academic_year=academic_year
        ).first()

        if existing_mark:
            existing_mark.enrollment_no = student.enrollment_no
            existing_mark.marks_obtained = marks_obtained
            existing_mark.max_marks = max_marks
            db.session.commit()
            return existing_mark, None

        new_mark = InternalMark(
            student_id=student_id,
            enrollment_no=student.enrollment_no,
            subject_id=subject_id,
            semester=semester,
            academic_year=academic_year,
            marks_obtained=marks_obtained,
            max_marks=max_marks
        )
        db.session.add(new_mark)
        db.session.commit()
        return new_mark, None

    except Exception as e:
        db.session.rollback()
        return None, f"Failed to save internal mark: {str(e)}"


import json

from services.subject_service import get_subject_component_config

def calculate_theory_internal_marks(test1=0, test2=0, test3=0, internal_exam=0,
                                   active_learning=0, class_assignment=0, home_assignment=0, attendance=0):
    """
    Calculates Theory Internal Assessment marks structure.
    Best 2 out of 3 Class Tests + Internal Exam + Active Learning + Class Assignment + Home Assignment + Attendance.
    """
    t1 = float(test1 or 0)
    t2 = float(test2 or 0)
    t3 = float(test3 or 0)
    ie = float(internal_exam or 0)
    al = float(active_learning or 0)
    ca = float(class_assignment or 0)
    ha = float(home_assignment or 0)
    att = float(attendance or 0)

    sorted_tests = sorted([t1, t2, t3], reverse=True)
    best_tests_sum = sorted_tests[0] + sorted_tests[1]
    calculated_class_test = round(best_tests_sum / 2.0, 2)

    total = round(calculated_class_test + ie + al + ca + ha + att, 2)

    return {
        "class_test_score": calculated_class_test,
        "internal_exam": ie,
        "active_learning": al,
        "class_assignment": ca,
        "home_assignment": ha,
        "attendance": att,
        "total_internal": total,
        "max_internal": 50
    }


def calculate_practical_internal_marks(internal_exam=0, practical_eval=0, viva=0, journal=0):
    """
    Calculates Practical Internal marks structure.
    Internal Exam + Practical Exam / Eval + Viva + Journal.
    """
    ie = float(internal_exam or 0)
    pe = float(practical_eval or 0)
    vi = float(viva or 0)
    jo = float(journal or 0)

    total = round(ie + pe + vi + jo, 2)

    return {
        "internal_exam": ie,
        "practical_eval": pe,
        "viva": vi,
        "journal": jo,
        "total_internal": total,
        "max_internal": 25
    }


def save_detailed_internal_mark(student_id, subject_id, semester, academic_year, data_dict, save_type='draft', commit=True):
    """
    Saves or updates detailed internal marks breakdown in InternalMark.

    Validates:
    - student exists
    - subject exists
    - subject_type (Theory vs Practical)
    - Dynamic component limits sourced from Subject configuration
    - Non-negative bounds & component maximums
    - Stores save_type ('draft' vs 'final') in component_data JSON
    """
    try:
        if not student_id or not isinstance(student_id, int):
            return None, "Invalid student ID."

        if not subject_id or not isinstance(subject_id, int):
            return None, "Invalid subject ID."

        try:
            semester = int(semester)
            if semester <= 0 or semester > 12:
                return None, "Semester must be a valid number between 1 and 12."
        except (ValueError, TypeError):
            return None, "Semester must be a valid integer."

        if not academic_year or not str(academic_year).strip():
            return None, "Academic Year is required."

        academic_year = str(academic_year).strip()
        save_type = str(save_type or 'draft').strip().lower()
        if save_type not in ['draft', 'final']:
            save_type = 'draft'

        student = db.session.get(Student, student_id)
        if not student:
            return None, f"Student with ID {student_id} does not exist."

        subject = db.session.get(Subject, subject_id)
        if not subject:
            return None, f"Subject with ID {subject_id} does not exist."

        # Fetch authoritative dynamic component configuration for subject
        comp_cfg = get_subject_component_config(subject)
        subject_type = comp_cfg['type']
        configured_max = comp_cfg['max_internal']
        comp_maxes = comp_cfg['maxes']

        def parse_val(field, max_val, label):
            val_raw = data_dict.get(field, None)
            if val_raw is None or val_raw == '':
                return None
            try:
                val = float(val_raw)
            except (ValueError, TypeError):
                raise ValueError(f"{label} must be a valid number.")
            if val < 0:
                raise ValueError(f"{label} cannot be negative.")
            if val > max_val:
                raise ValueError(f"{label} cannot exceed {max_val} marks.")
            return val

        if subject_type == 'Theory':
            try:
                t1 = parse_val('test1', comp_maxes.get('test1', 20.0), 'Class Test 1')
                t2 = parse_val('test2', comp_maxes.get('test2', 20.0), 'Class Test 2')
                t3 = parse_val('test3', comp_maxes.get('test3', 20.0), 'Class Test 3')
                ie = parse_val('internal_exam', comp_maxes.get('internal_exam', 50.0), 'Internal Exam')

                al = parse_val('active_learning', comp_maxes.get('active_learning', 5.0), 'Active Learning')
                ca = parse_val('class_assignment', comp_maxes.get('class_assignment', 5.0), 'Class Assignment')
                ha = parse_val('home_assignment', comp_maxes.get('home_assignment', 5.0), 'Home Assignment')
                att = parse_val('attendance', comp_maxes.get('attendance', 5.0), 'Attendance')
            except ValueError as ve:
                return None, str(ve)

            # Best 2 of 3 Class Tests
            t1_v = t1 if t1 is not None else 0.0
            t2_v = t2 if t2 is not None else 0.0
            t3_v = t3 if t3 is not None else 0.0
            tests_sorted = sorted([t1_v, t2_v, t3_v], reverse=True)
            best2_sum = tests_sorted[0] + tests_sorted[1]
            calculated_best2 = round(best2_sum / 2.0, 2)

            ie_v = ie if ie is not None else 0.0
            al_v = al if al is not None else 0.0
            ca_v = ca if ca is not None else 0.0
            ha_v = ha if ha is not None else 0.0
            att_v = att if att is not None else 0.0

            raw_total = round(calculated_best2 + ie_v + al_v + ca_v + ha_v + att_v, 2)
            max_sum = comp_cfg['max_sum']

            parsed_config = comp_maxes
            if max_sum > 0 and configured_max != max_sum and (parsed_config and 'internal_exam' in parsed_config):
                total_obtained = round((raw_total / max_sum) * configured_max, 2)
            else:
                total_obtained = raw_total

            max_marks = configured_max
            if total_obtained > max_marks:
                total_obtained = max_marks

            existing = InternalMark.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                semester=semester,
                academic_year=academic_year
            ).first()

            if not existing:
                existing = InternalMark(
                    student_id=student_id,
                    enrollment_no=student.enrollment_no,
                    subject_id=subject_id,
                    semester=semester,
                    academic_year=academic_year,
                    marks_obtained=total_obtained,
                    max_marks=max_marks
                )
                db.session.add(existing)

            existing.enrollment_no = student.enrollment_no
            existing.marks_obtained = total_obtained
            existing.max_marks = max_marks
            existing.test1 = t1
            existing.test2 = t2
            existing.test3 = t3
            existing.internal_exam = ie
            existing.active_learning = al
            existing.class_assignment = ca
            existing.home_assignment = ha
            existing.attendance = att
            existing.practical_eval = None
            existing.viva = None
            existing.journal = None

            existing.component_data = json.dumps({
                "type": "Theory",
                "save_type": save_type,
                "status": save_type,
                "is_final": (save_type == "final"),
                "test1": t1, "test2": t2, "test3": t3,
                "best2": calculated_best2,
                "internal_exam": ie,
                "active_learning": al, "class_assignment": ca, "home_assignment": ha, "attendance": att,
                "total": total_obtained,
                "max_marks": max_marks
            })

            if commit:
                db.session.commit()
            return existing, None

        else:
            # Practical subject
            try:
                ie = parse_val('internal_exam', comp_maxes.get('internal_exam', 10.0), 'Viva / Interview Marks')
                pe = parse_val('practical_eval', comp_maxes.get('practical_eval', 10.0), 'Coding / Practical Marks')
                vi = parse_val('viva', comp_maxes.get('viva', 0.0), 'Viva')
                jo = parse_val('journal', comp_maxes.get('journal', 5.0), 'Journal')
            except ValueError as ve:
                return None, str(ve)

            ie_v = ie if ie is not None else 0.0
            pe_v = pe if pe is not None else 0.0
            vi_v = vi if vi is not None else 0.0
            jo_v = jo if jo is not None else 0.0

            raw_total = round(ie_v + pe_v + vi_v + jo_v, 2)
            max_sum = comp_cfg['max_sum']

            if max_sum > 0 and configured_max != max_sum:
                total_obtained = round((raw_total / max_sum) * configured_max, 2)
            else:
                total_obtained = raw_total

            max_marks = configured_max
            if total_obtained > max_marks:
                return None, f"Calculated practical marks ({total_obtained}) exceed subject maximum internal marks ({max_marks})."

            existing = InternalMark.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                semester=semester,
                academic_year=academic_year
            ).first()

            if not existing:
                existing = InternalMark(
                    student_id=student_id,
                    enrollment_no=student.enrollment_no,
                    subject_id=subject_id,
                    semester=semester,
                    academic_year=academic_year,
                    marks_obtained=total_obtained,
                    max_marks=max_marks
                )
                db.session.add(existing)

            existing.enrollment_no = student.enrollment_no
            existing.marks_obtained = total_obtained
            existing.max_marks = max_marks
            existing.test1 = None
            existing.test2 = None
            existing.test3 = None
            existing.active_learning = None
            existing.class_assignment = None
            existing.home_assignment = None
            existing.attendance = None
            existing.internal_exam = ie
            existing.practical_eval = pe
            existing.viva = vi
            existing.journal = jo

            existing.component_data = json.dumps({
                "type": "Practical",
                "save_type": save_type,
                "status": save_type,
                "is_final": (save_type == "final"),
                "internal_exam": ie,
                "practical_eval": pe,
                "viva": vi,
                "journal": jo,
                "total": total_obtained,
                "max_marks": max_marks
            })

            if commit:
                db.session.commit()
            return existing, None

    except Exception as e:
        if commit:
            db.session.rollback()
        return None, f"Failed to save detailed internal mark: {str(e)}"


def save_bulk_internal_marks(faculty_id, subject_id, division, semester, academic_year, marks_list, save_type='draft'):
    """
    Saves or updates a batch of internal mark records for students assigned to a subject and division.

    Validation:
    - Enforces logged-in faculty assignment check (FacultySubjectAssignment)
    - Validates each student's membership in the division and subject mapping
    - Validates component ranges (non-negative, <= component max)
    - Stores save_type ('draft' vs 'final') in component_data JSON
    - Operates atomically in a single DB transaction (rolls back on any error)

    Returns:
        tuple: (result_dict, None) or (None, error_message)
    """
    if not faculty_id:
        return None, "Unauthorized access."

    from models import FacultySubjectAssignment, Student
    assignment = FacultySubjectAssignment.query.filter_by(
        faculty_id=faculty_id,
        subject_id=subject_id,
        division=division,
        status='Active'
    ).first()

    if not assignment:
        return None, f"Access denied: Subject (ID: {subject_id}) and Division '{division}' are not assigned to you."

    if not marks_list or not isinstance(marks_list, list):
        return None, "No marks provided in bulk save payload."

    saved_records = []
    try:
        for idx, student_data in enumerate(marks_list):
            st_id = student_data.get('student_id')
            if not st_id:
                continue

            student = db.session.get(Student, int(st_id))
            st_identifier = f"Roll #{student.roll_number} ({student.full_name})" if student else f"Student ID {st_id}"

            rec, err = save_detailed_internal_mark(
                student_id=int(st_id),
                subject_id=int(subject_id),
                semester=int(semester),
                academic_year=str(academic_year).strip(),
                data_dict=student_data,
                save_type=save_type,
                commit=False
            )

            if err:
                db.session.rollback()
                return None, f"Error saving marks for {st_identifier}: {err}"

            saved_records.append(rec)

        db.session.commit()
        return {
            "saved_count": len(saved_records),
            "message": f"Successfully saved internal marks for {len(saved_records)} students."
        }, None

    except Exception as e:
        db.session.rollback()
        return None, f"Bulk save failed: {str(e)}"


