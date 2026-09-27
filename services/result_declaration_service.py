"""
CampusSync ERP - Result Declaration Service
===========================================
File: services/result_declaration_service.py

Manages official publication and declaration of internal assessment results.
Enforces that students can only download official marksheets after Admin publishes results.
"""

from datetime import datetime
from extensions import db
from models import ResultDeclaration, Subject, Student, InternalMark
from services.admin_results_service import is_mark_final


def is_result_declared(academic_year, semester, division='All'):
    """
    Checks if internal assessment results are declared/published for the given
    academic year, semester, and division.
    
    Checks specific division record first, then falls back to 'All' division record.
    """
    try:
        sem_num = int(semester) if semester is not None else None
    except (ValueError, TypeError):
        return False

    if not academic_year or sem_num is None:
        return False

    # Check division-specific declaration
    if division and division != 'All':
        specific_decl = ResultDeclaration.query.filter_by(
            academic_year=str(academic_year).strip(),
            semester=sem_num,
            division=str(division).strip()
        ).first()
        if specific_decl and specific_decl.is_declared:
            return True

    # Check global/all-division declaration
    all_decl = ResultDeclaration.query.filter_by(
        academic_year=str(academic_year).strip(),
        semester=sem_num,
        division='All'
    ).first()

    return bool(all_decl and all_decl.is_declared)


def get_declaration_status(academic_year, semester, division='All'):
    """
    Gets the declaration status record and details for given parameters.
    """
    try:
        sem_num = int(semester) if semester is not None else None
    except (ValueError, TypeError):
        return {'is_declared': False, 'declared_at': None, 'declared_by': None, 'record': None}

    # First check specific division, then fallback to 'All'
    decl = None
    if division and division != 'All':
        decl = ResultDeclaration.query.filter_by(
            academic_year=str(academic_year).strip(),
            semester=sem_num,
            division=str(division).strip()
        ).first()

    if not decl:
        decl = ResultDeclaration.query.filter_by(
            academic_year=str(academic_year).strip(),
            semester=sem_num,
            division='All'
        ).first()

    if decl:
        return {
            'is_declared': bool(decl.is_declared),
            'declared_at': decl.declared_at,
            'declared_by': decl.declared_by,
            'record': decl
        }

    return {'is_declared': False, 'declared_at': None, 'declared_by': None, 'record': None}


def toggle_result_declaration(academic_year, semester, division='All', admin_id=None):
    """
    Toggles the declaration status (Declare <-> Revoke/Unpublish) for a semester/division.
    Returns (record, is_declared, message).
    """
    try:
        sem_num = int(semester) if semester is not None else None
    except (ValueError, TypeError):
        return None, False, "Invalid semester provided."

    if not academic_year or sem_num is None:
        return None, False, "Academic year and semester are required."

    target_div = str(division).strip() if division else 'All'
    ay_str = str(academic_year).strip()

    decl = ResultDeclaration.query.filter_by(
        academic_year=ay_str,
        semester=sem_num,
        division=target_div
    ).first()

    will_be_declared = not decl.is_declared if decl else True

    # STRICT SAFEGUARD: Only allow publication if ALL subjects' internal marks are final-saved!
    if will_be_declared:
        sub_status = get_semester_faculty_submission_status(ay_str, sem_num, target_div)
        if not sub_status['is_all_finalized']:
            pending = sub_status['pending_subjects']
            pending_names = [f"{s['code']} ({s['name']})" for s in pending]
            pending_summary = ", ".join(pending_names[:5])
            if len(pending_names) > 5:
                pending_summary += f" and {len(pending_names) - 5} more"
            return None, False, f"Cannot declare results: All subjects must be final-saved by faculty first. Pending {len(pending)} of {sub_status['total_subjects']} subjects: {pending_summary}"

    if decl:
        # Toggle existing status
        decl.is_declared = will_be_declared
        decl.declared_at = datetime.utcnow()
        if admin_id:
            decl.declared_by = admin_id
    else:
        # Create new declared record
        decl = ResultDeclaration(
            academic_year=ay_str,
            semester=sem_num,
            division=target_div,
            is_declared=will_be_declared,
            declared_at=datetime.utcnow(),
            declared_by=admin_id
        )
        db.session.add(decl)

    try:
        db.session.commit()
        status_text = "declared & published" if decl.is_declared else "un-published / revoked"
        msg = f"Results for Semester {sem_num} ({ay_str}, Division: {target_div}) have been {status_text} successfully."
        return decl, decl.is_declared, msg
    except Exception as e:
        db.session.rollback()
        return None, False, f"Database error toggling result declaration: {str(e)}"


def get_semester_faculty_submission_status(academic_year, semester, division='A'):
    """
    Analyzes whether faculty have finalized internal marks for all subjects of this semester.
    Returns dictionary with counts, list of pending subjects, and readiness flag.
    """
    try:
        sem_num = int(semester) if semester is not None else None
    except (ValueError, TypeError):
        return {'total_subjects': 0, 'finalized_subjects': 0, 'pending_subjects': [], 'is_all_finalized': False, 'total_students': 0}

    if not academic_year or sem_num is None:
        return {'total_subjects': 0, 'finalized_subjects': 0, 'pending_subjects': [], 'is_all_finalized': False, 'total_students': 0}

    # Fetch active subjects for this semester
    subjects = Subject.query.filter_by(semester=sem_num, status='Active').order_by(Subject.subject_code).all()
    if not subjects:
        subjects = Subject.query.filter_by(semester=sem_num).order_by(Subject.subject_code).all()
    if not subjects:
        return {'total_subjects': 0, 'finalized_subjects': 0, 'pending_subjects': [], 'is_all_finalized': False, 'total_students': 0}

    # Active students in this semester (and division if specified)
    students_query = Student.query.filter_by(
        semester=sem_num,
        status='Active'
    )
    if division and division != 'All':
        students_query = students_query.filter_by(division=division)

    students = students_query.all()
    if not students:
        pending_list = [{'code': s.subject_code, 'name': s.subject_name} for s in subjects]
        return {
            'total_subjects': len(subjects),
            'finalized_subjects': 0,
            'pending_subjects': pending_list,
            'is_all_finalized': False,
            'total_students': 0
        }

    finalized_subject_count = 0
    student_ids = [s.id for s in students]
    pending_subjects = []
    finalized_subjects = []

    for subj in subjects:
        # Check marks for these students in this subject
        marks = InternalMark.query.filter(
            InternalMark.subject_id == subj.id,
            InternalMark.semester == sem_num,
            InternalMark.academic_year == academic_year,
            InternalMark.student_id.in_(student_ids)
        ).all()

        marks_by_st = {m.student_id: m for m in marks}
        has_all_students = len(marks) >= len(students) and all(s_id in marks_by_st for s_id in student_ids)
        all_final = has_all_students and all(is_mark_final(marks_by_st[s_id]) for s_id in student_ids)

        if all_final:
            finalized_subject_count += 1
            finalized_subjects.append({
                'id': subj.id,
                'code': subj.subject_code,
                'name': subj.subject_name
            })
        else:
            final_entered_count = sum(1 for s_id in student_ids if s_id in marks_by_st and is_mark_final(marks_by_st[s_id]))
            pending_subjects.append({
                'id': subj.id,
                'code': subj.subject_code,
                'name': subj.subject_name,
                'final_entered_count': final_entered_count,
                'total_students': len(students)
            })

    is_all_finalized = (finalized_subject_count == len(subjects) and len(subjects) > 0 and len(students) > 0)

    return {
        'total_subjects': len(subjects),
        'finalized_subjects': finalized_subject_count,
        'pending_subjects': pending_subjects,
        'finalized_subjects_list': finalized_subjects,
        'is_all_finalized': is_all_finalized,
        'total_students': len(students)
    }
