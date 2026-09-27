import json
from extensions import db
from models import Subject

def get_subject_component_config(subject):
    """
    Returns the single source of truth assessment component configuration for a subject.
    Sources from subject.component_config (JSON string) if configured, else generates standard
    type-specific defaults matching subject.internal_marks.
    """
    if not subject:
        return None

    if isinstance(subject, dict):
        subj_type = subject.get('subject_type') or 'Theory'
        internal_max = float(subject.get('internal_marks') or (50 if subj_type == 'Theory' else 25))
        cfg_raw = subject.get('component_config')
    else:
        subj_type = getattr(subject, 'subject_type', 'Theory') or 'Theory'
        internal_max = float(getattr(subject, 'internal_marks', 50 if subj_type == 'Theory' else 25) or (50 if subj_type == 'Theory' else 25))
        cfg_raw = getattr(subject, 'component_config', None)

    parsed_config = None
    if cfg_raw:
        try:
            parsed_config = json.loads(cfg_raw) if isinstance(cfg_raw, str) else cfg_raw
        except Exception:
            parsed_config = None

    if subj_type == 'Theory':
        t1_max = float(parsed_config.get('test1', 20)) if (parsed_config and 'test1' in parsed_config) else 20.0
        t2_max = float(parsed_config.get('test2', 20)) if (parsed_config and 'test2' in parsed_config) else 20.0
        t3_max = float(parsed_config.get('test3', 20)) if (parsed_config and 'test3' in parsed_config) else 20.0
        best2_max = float(parsed_config.get('best2', 20)) if (parsed_config and 'best2' in parsed_config) else 20.0
        if parsed_config and 'internal_exam' in parsed_config:
            ie_max = float(parsed_config['internal_exam'])
        else:
            ie_max = internal_max
        al_max = float(parsed_config.get('active_learning', 5)) if (parsed_config and 'active_learning' in parsed_config) else 5.0
        ca_max = float(parsed_config.get('class_assignment', 5)) if (parsed_config and 'class_assignment' in parsed_config) else 5.0
        ha_max = float(parsed_config.get('home_assignment', 5)) if (parsed_config and 'home_assignment' in parsed_config) else 5.0
        att_max = float(parsed_config.get('attendance', 5)) if (parsed_config and 'attendance' in parsed_config) else 5.0

        components = [
            {"field": "test1", "label": "Class Test 1", "short_label": "Test 1", "max": t1_max, "is_calc": False, "is_auto": False},
            {"field": "test2", "label": "Class Test 2", "short_label": "Test 2", "max": t2_max, "is_calc": False, "is_auto": False},
            {"field": "test3", "label": "Class Test 3", "short_label": "Test 3", "max": t3_max, "is_calc": False, "is_auto": False},
            {"field": "best2", "label": "Best 2 of 3 Class Tests", "short_label": "Best 2", "max": best2_max, "is_calc": True, "is_auto": False},
            {"field": "internal_exam", "label": "Internal Exam", "short_label": "Internal Exam", "max": ie_max, "is_calc": False, "is_auto": False},
            {"field": "active_learning", "label": "Active Learning", "short_label": "Active Lrn", "max": al_max, "is_calc": False, "is_auto": False},
            {"field": "class_assignment", "label": "Class Assignment", "short_label": "Class Assign", "max": ca_max, "is_calc": False, "is_auto": False},
            {"field": "home_assignment", "label": "Home Assignment", "short_label": "Home Assign", "max": ha_max, "is_calc": False, "is_auto": False},
            {"field": "attendance", "label": "Attendance", "short_label": "Attendance", "max": att_max, "is_calc": False, "is_auto": True},
        ]
        
        max_sum = best2_max + ie_max + al_max + ca_max + ha_max + att_max

        return {
            "type": "Theory",
            "max_internal": internal_max,
            "max_sum": max_sum,
            "components": components,
            "maxes": {
                "test1": t1_max, "test2": t2_max, "test3": t3_max, "best2": best2_max,
                "internal_exam": ie_max, "active_learning": al_max,
                "class_assignment": ca_max, "home_assignment": ha_max, "attendance": att_max
            }
        }

    else:
        ie_max = float(parsed_config.get('internal_exam', 10)) if parsed_config else 10.0
        pe_max = float(parsed_config.get('practical_eval', 10)) if parsed_config else 10.0
        jo_max = float(parsed_config.get('journal', 5)) if parsed_config else 5.0
        vi_max = float(parsed_config.get('viva', 0)) if parsed_config else 0.0

        components = [
            {"field": "internal_exam", "label": "Viva / Interview Marks", "short_label": "Viva / Interview", "max": ie_max, "is_calc": False, "is_auto": False},
            {"field": "practical_eval", "label": "Coding / Practical Marks", "short_label": "Coding / Practical", "max": pe_max, "is_calc": False, "is_auto": False},
        ]
        if vi_max > 0:
            components.append({"field": "viva", "label": "Viva", "short_label": "Viva", "max": vi_max, "is_calc": False, "is_auto": False})
        components.append({"field": "journal", "label": "Journal", "short_label": "Journal", "max": jo_max, "is_calc": False, "is_auto": False})

        max_sum = ie_max + pe_max + jo_max + vi_max

        return {
            "type": "Practical",
            "max_internal": internal_max,
            "max_sum": max_sum,
            "components": components,
            "maxes": {
                "internal_exam": ie_max, "practical_eval": pe_max, "journal": jo_max, "viva": vi_max
            }
        }


def get_all_subjects(semester=None, course=None):
    """
    Fetches all subject records with optional semester and course filtering.
    """
    query = Subject.query

    # Filter by semester if provided
    if semester:
        try:
            sem_val = int(semester)
            if 1 <= sem_val <= 6:
                query = query.filter(Subject.semester == sem_val)
        except (ValueError, TypeError):
            pass

    # Filter by course if provided
    if course:
        query = query.filter(Subject.course == course)

    # Return subjects sorted by semester and subject code
    return query.order_by(Subject.semester.asc(), Subject.subject_code.asc()).all()

def get_subjects_by_semester(semester):
    """
    Get list of subjects for a specific semester.
    """
    return get_all_subjects(semester=semester)

def get_subject_by_id(subject_id):
    """
    Fetch a single subject by ID.
    """
    if not subject_id:
        return None
    return Subject.query.get(int(subject_id))

def add_subject(form_data, default_course='BCA'):
    """
    Adds a new subject record with validation.
    """
    try:
        subject_code = form_data.get('subject_code', '').strip().upper()
        subject_name = form_data.get('subject_name', '').strip()
        course = form_data.get('course', '').strip() or default_course or 'BCA'
        semester_raw = form_data.get('semester', '').strip()
        subject_type = form_data.get('subject_type', 'Theory').strip()
        credits_raw = form_data.get('credits', '4').strip()
        internal_raw = form_data.get('internal_marks', '30').strip()
        external_raw = form_data.get('external_marks', '70').strip()
        total_raw = form_data.get('total_marks', '').strip()
        status = form_data.get('status', 'Active').strip()
        comp_config_raw = form_data.get('component_config', '').strip()

        # Validate required subject code
        if not subject_code:
            return None, "Subject Code is required (e.g. BCA101)."

        # Validate required subject name
        if not subject_name:
            return None, "Subject Name is required."

        # Validate semester range (1 to 6)
        try:
            semester = int(semester_raw)
            if not (1 <= semester <= 6):
                return None, "Semester must be between 1 and 6."
        except (ValueError, TypeError):
            return None, "Invalid semester value."

        # Validate subject type
        if subject_type not in ['Theory', 'Practical']:
            subject_type = 'Theory'

        # Validate credits numeric value
        try:
            credits = int(credits_raw)
            if credits < 0:
                return None, "Credits must be a positive number."
        except (ValueError, TypeError):
            credits = 4

        # Parse exam marks
        try:
            internal_marks = int(internal_raw)
        except (ValueError, TypeError):
            internal_marks = 30

        try:
            external_marks = int(external_raw)
        except (ValueError, TypeError):
            external_marks = 70

        try:
            total_marks = int(total_raw) if total_raw else (internal_marks + external_marks)
        except (ValueError, TypeError):
            total_marks = internal_marks + external_marks

        # Validate JSON component_config if provided
        comp_config = None
        if comp_config_raw:
            try:
                json.loads(comp_config_raw)
                comp_config = comp_config_raw
            except Exception:
                comp_config = None

        # Check duplicate subject code for the same course
        existing = Subject.query.filter_by(course=course, subject_code=subject_code).first()
        if existing:
            return None, f"Subject code '{subject_code}' already exists for course '{course}'."

        # Create new Subject record
        new_subject = Subject(
            subject_code=subject_code,
            subject_name=subject_name,
            course=course,
            semester=semester,
            subject_type=subject_type,
            credits=credits,
            internal_marks=internal_marks,
            external_marks=external_marks,
            total_marks=total_marks,
            component_config=comp_config,
            status=status if status in ['Active', 'Inactive'] else 'Active'
        )

        db.session.add(new_subject)
        db.session.commit()
        return new_subject, None

    except Exception as e:
        db.session.rollback()
        return None, f"Failed to add subject: {str(e)}"

def update_subject(subject_id, form_data):
    """
    Updates existing subject record by ID.
    """
    try:
        subject = get_subject_by_id(subject_id)
        if not subject:
            return None, "Subject record not found."

        subject_code = form_data.get('subject_code', '').strip().upper()
        subject_name = form_data.get('subject_name', '').strip()
        course = form_data.get('course', '').strip() or subject.course
        semester_raw = form_data.get('semester', '').strip()
        subject_type = form_data.get('subject_type', 'Theory').strip()
        credits_raw = form_data.get('credits', '4').strip()
        internal_raw = form_data.get('internal_marks', str(subject.internal_marks)).strip()
        external_raw = form_data.get('external_marks', str(subject.external_marks)).strip()
        total_raw = form_data.get('total_marks', str(subject.total_marks)).strip()
        status = form_data.get('status', 'Active').strip()
        comp_config_raw = form_data.get('component_config', '').strip()

        # Validate required subject code
        if not subject_code:
            return None, "Subject Code is required."

        # Validate required subject name
        if not subject_name:
            return None, "Subject Name is required."

        # Validate semester range (1 to 6)
        try:
            semester = int(semester_raw)
            if not (1 <= semester <= 6):
                return None, "Semester must be between 1 and 6."
        except (ValueError, TypeError):
            return None, "Invalid semester value."

        # Validate credits
        try:
            credits = int(credits_raw)
            if credits < 0:
                return None, "Credits must be a positive number."
        except (ValueError, TypeError):
            credits = subject.credits

        # Parse exam marks
        try:
            internal_marks = int(internal_raw)
        except (ValueError, TypeError):
            internal_marks = subject.internal_marks

        try:
            external_marks = int(external_raw)
        except (ValueError, TypeError):
            external_marks = subject.external_marks

        try:
            total_marks = int(total_raw) if total_raw else (internal_marks + external_marks)
        except (ValueError, TypeError):
            total_marks = internal_marks + external_marks

        comp_config = subject.component_config
        if comp_config_raw:
            try:
                json.loads(comp_config_raw)
                comp_config = comp_config_raw
            except Exception:
                pass

        # Check duplicate subject code for same course (excluding current subject)
        existing = Subject.query.filter(
            Subject.course == course,
            Subject.subject_code == subject_code,
            Subject.id != subject_id
        ).first()

        if existing:
            return None, f"Subject code '{subject_code}' is already used by another subject in '{course}'."

        # Update subject fields
        subject.subject_code = subject_code
        subject.subject_name = subject_name
        subject.course = course
        subject.semester = semester
        subject.subject_type = subject_type if subject_type in ['Theory', 'Practical'] else subject.subject_type
        subject.credits = credits
        subject.internal_marks = internal_marks
        subject.external_marks = external_marks
        subject.total_marks = total_marks
        subject.component_config = comp_config
        subject.status = status if status in ['Active', 'Inactive'] else subject.status

        db.session.commit()
        return subject, None

    except Exception as e:
        db.session.rollback()
        return None, f"Failed to update subject: {str(e)}"

def delete_subject(subject_id):
    """
    Deletes subject record by ID.
    """
    try:
        subject = get_subject_by_id(subject_id)
        if not subject:
            return False, "Subject record not found."

        db.session.delete(subject)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, f"Failed to delete subject: {str(e)}"

def toggle_subject_status(subject_id):
    """
    Toggles subject status between Active and Inactive.
    """
    try:
        subject = get_subject_by_id(subject_id)
        if not subject:
            return None, "Subject record not found."

        # Toggle status
        subject.status = 'Inactive' if subject.status == 'Active' else 'Active'
        db.session.commit()
        return subject, None

    except Exception as e:
        db.session.rollback()
        return None, f"Failed to change status: {str(e)}"
