"""
CampusSync ERP - Academic Settings Service
==========================================
File: services/academic_service.py

Provides simple functions to manage current Academic Year, 
Semester Cycle (Odd/Even), and Cycle Start/End dates.
"""

from datetime import datetime
from models import AcademicSetting, Student, InternalMark, ArchivedStudent, ArchivedInternalMark
from extensions import db

def get_academic_settings():
    """
    Get current academic settings.
    Creates a default record if database table is empty.
    """
    settings = AcademicSetting.query.first()
    
    # Create default record if database table is empty
    if not settings:
        settings = AcademicSetting(
            academic_year="2026-27",
            semester_cycle="Odd",
            cycle_start_date=None,
            cycle_end_date=None
        )
        db.session.add(settings)
        db.session.commit()
        
    return settings

def get_active_semesters(semester_cycle=None):
    """
    Determine active semesters list based on cycle.
    Odd Cycle: [1, 3, 5]
    Even Cycle: [2, 4, 6]
    """
    if not semester_cycle:
        settings = get_academic_settings()
        semester_cycle = settings.semester_cycle if settings else 'Odd'

    if semester_cycle == 'Odd':
        return [1, 3, 5]
    elif semester_cycle == 'Even':
        return [2, 4, 6]
    else:
        return [1, 3, 5]

def get_graduating_students_count(academic_year=None, semester=6):
    """
    Returns the count of active students currently in the final/graduating semester (default Semester 6).
    """
    query = Student.query.filter(Student.semester == semester, Student.status == 'Active')
    if academic_year:
        query = query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))
    return query.count()

def get_odd_semester_students_count(academic_year=None):
    """
    Returns the count of active students in Odd semesters (1, 3, 5).
    Returns dict: {'sem1': int, 'sem3': int, 'sem5': int, 'total': int}
    """
    base_query = Student.query.filter(Student.status == 'Active')
    if academic_year:
        base_query = base_query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))

    sem1_count = base_query.filter(Student.semester == 1).count()
    sem3_count = base_query.filter(Student.semester == 3).count()
    sem5_count = base_query.filter(Student.semester == 5).count()
    total = sem1_count + sem3_count + sem5_count

    return {
        'sem1': sem1_count,
        'sem3': sem3_count,
        'sem5': sem5_count,
        'total': total
    }

def get_even_semester_students_count(academic_year=None):
    """
    Returns the count of active students in Even semesters (2, 4, 6).
    Returns dict: {'sem2': int, 'sem4': int, 'sem6': int, 'total': int}
    """
    base_query = Student.query.filter(Student.status == 'Active')
    if academic_year:
        base_query = base_query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))

    sem2_count = base_query.filter(Student.semester == 2).count()
    sem4_count = base_query.filter(Student.semester == 4).count()
    sem6_count = base_query.filter(Student.semester == 6).count()
    total = sem2_count + sem4_count + sem6_count

    return {
        'sem2': sem2_count,
        'sem4': sem4_count,
        'sem6': sem6_count,
        'total': total
    }

def promote_even_to_odd_new_year(academic_year=None):
    """
    Executes Year-End Academic Transition across all active batches:
    1. Archives all active Semester 6 students to `ArchivedStudent` and `ArchivedInternalMark`,
       and marks them status='Inactive' in `Student` table to block portal login.
    2. Promotes active Semester 4 students -> Semester 5.
    3. Promotes active Semester 2 students -> Semester 3.
    4. Leaves Semester 1 empty for incoming fresh admissions.
    
    Returns:
        tuple: (archived_count, promoted_count, error_message)
    """
    try:
        base_query = Student.query.filter(Student.status == 'Active')

        # 1. Archive Semester 6 graduating students
        graduating_students = base_query.filter(Student.semester == 6).all()
        archived_count = 0
        for st in graduating_students:
            # Archive student profile
            existing_archived = ArchivedStudent.query.filter_by(enrollment_no=st.enrollment_no).first()
            if not existing_archived:
                archived_st = ArchivedStudent(
                    original_student_id=st.id,
                    roll_number=st.roll_number,
                    enrollment_no=st.enrollment_no,
                    full_name=st.full_name,
                    email=st.email,
                    mobile=st.mobile,
                    dob=st.dob,
                    course=st.course or 'BCA',
                    final_semester=st.semester,
                    division=st.division,
                    academic_year=st.academic_year or academic_year or '2026-27',
                    profile_photo=st.profile_photo or 'default-avatar.png',
                    status='Inactive'
                )
                db.session.add(archived_st)

            # Archive marks
            marks = InternalMark.query.filter_by(student_id=st.id).all()
            for m in marks:
                existing_m = ArchivedInternalMark.query.filter_by(
                    enrollment_no=st.enrollment_no,
                    subject_id=m.subject_id,
                    semester=m.semester,
                    academic_year=m.academic_year
                ).first()
                if not existing_m:
                    archived_m = ArchivedInternalMark(
                        enrollment_no=st.enrollment_no,
                        student_name=st.full_name,
                        subject_id=m.subject_id,
                        subject_code=m.subject.subject_code if m.subject else None,
                        subject_name=m.subject.subject_name if m.subject else None,
                        semester=m.semester,
                        academic_year=m.academic_year,
                        marks_obtained=m.marks_obtained,
                        max_marks=m.max_marks,
                        component_data=m.component_data
                    )
                    db.session.add(archived_m)

            # Set status to Inactive to disable student portal login
            st.status = 'Inactive'
            archived_count += 1

        # 2. Promote active Semester 4 students -> Semester 5
        from utils.helpers import generate_roll_number
        promoted_count = 0
        sem4_students = base_query.filter(Student.semester == 4).all()
        for st in sem4_students:
            existing = Student.query.filter(
                Student.semester == 5,
                Student.academic_year == st.academic_year,
                Student.course == st.course,
                Student.roll_number == st.roll_number,
                Student.id != st.id
            ).first()
            if existing:
                st.roll_number = generate_roll_number(semester=5, academic_year=st.academic_year, course=st.course)
            st.semester = 5
            promoted_count += 1

        # 3. Promote active Semester 2 students -> Semester 3
        sem2_students = base_query.filter(Student.semester == 2).all()
        for st in sem2_students:
            existing = Student.query.filter(
                Student.semester == 3,
                Student.academic_year == st.academic_year,
                Student.course == st.course,
                Student.roll_number == st.roll_number,
                Student.id != st.id
            ).first()
            if existing:
                st.roll_number = generate_roll_number(semester=3, academic_year=st.academic_year, course=st.course)
            st.semester = 3
            promoted_count += 1

        db.session.commit()
        return archived_count, promoted_count, None

    except Exception as e:
        db.session.rollback()
        return 0, 0, f"Error performing academic year transition: {str(e)}"

def promote_odd_to_even_students(academic_year=None):
    """
    Promotes all active students in Odd semesters to corresponding Even semesters:
      - Semester 5 -> Semester 6
      - Semester 3 -> Semester 4
      - Semester 1 -> Semester 2
    Executed in strictly descending order to prevent cascading/double promotions.
    
    Returns:
        tuple: (promoted_count, None) or (0, error_message)
    """
    try:
        from utils.helpers import generate_roll_number
        base_query = Student.query.filter(Student.status == 'Active')
        if academic_year:
            base_query = base_query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))

        promoted_count = 0
        # Descending order is crucial: 5 -> 6, 3 -> 4, 1 -> 2
        for odd_sem in [5, 3, 1]:
            target_sem = odd_sem + 1
            students = base_query.filter(Student.semester == odd_sem).all()
            for st in students:
                existing = Student.query.filter(
                    Student.semester == target_sem,
                    Student.academic_year == st.academic_year,
                    Student.course == st.course,
                    Student.roll_number == st.roll_number,
                    Student.id != st.id
                ).first()
                if existing:
                    st.roll_number = generate_roll_number(semester=target_sem, academic_year=st.academic_year, course=st.course)
                st.semester = target_sem
                promoted_count += 1

        db.session.commit()
        return promoted_count, None
    except Exception as e:
        db.session.rollback()
        return 0, f"Error moving odd semester students to even: {str(e)}"

def move_even_to_odd_students(academic_year=None):
    """
    Transitions all active students in Even semesters to corresponding Odd semesters:
      - Semester 2 -> Semester 1
      - Semester 4 -> Semester 3
      - Semester 6 -> Semester 5
    Executed in strictly ascending order (2 -> 1, 4 -> 3, 6 -> 5) to prevent cascading.
    Safely preserves all marks, attendance, and student history without data loss.
    
    Returns:
        tuple: (moved_count, None) or (0, error_message)
    """
    try:
        from utils.helpers import generate_roll_number
        base_query = Student.query.filter(Student.status == 'Active')
        if academic_year:
            base_query = base_query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))

        moved_count = 0
        # Ascending order is crucial: 2 -> 1, 4 -> 3, 6 -> 5
        for even_sem in [2, 4, 6]:
            target_sem = even_sem - 1
            students = base_query.filter(Student.semester == even_sem).all()
            for st in students:
                existing = Student.query.filter(
                    Student.semester == target_sem,
                    Student.academic_year == st.academic_year,
                    Student.course == st.course,
                    Student.roll_number == st.roll_number,
                    Student.id != st.id
                ).first()
                if existing:
                    st.roll_number = generate_roll_number(semester=target_sem, academic_year=st.academic_year, course=st.course)
                st.semester = target_sem
                moved_count += 1

        db.session.commit()
        return moved_count, None
    except Exception as e:
        db.session.rollback()
        return 0, f"Error moving even semester students to odd: {str(e)}"

def archive_graduating_students(academic_year=None, semester=6):
    """
    Archives students who completed their final semester (Semester 6) and their marks.
    1. Copies student records to `archived_students`.
    2. Copies all their internal marks to `archived_internal_marks`.
    3. Marks them status='Inactive' in `students` to preserve historical data without CASCADE deletion.
    Returns:
        tuple: (archived_count, None) or (0, error_message)
    """
    try:
        query = Student.query.filter(Student.semester == semester, Student.status == 'Active')
        if academic_year:
            query = query.filter((Student.academic_year == academic_year) | (Student.academic_year.is_(None)))

        graduating_students = query.all()
        if not graduating_students:
            return 0, None

        archived_count = 0
        for st in graduating_students:
            # 1. Archive student profile
            archived_st = ArchivedStudent(
                original_student_id=st.id,
                roll_number=st.roll_number,
                enrollment_no=st.enrollment_no,
                full_name=st.full_name,
                email=st.email,
                mobile=st.mobile,
                dob=st.dob,
                course=st.course or 'BCA',
                final_semester=st.semester,
                division=st.division,
                academic_year=st.academic_year or academic_year,
                profile_photo=st.profile_photo or 'default-avatar.png',
                status='Archived'
            )
            db.session.add(archived_st)

            # 2. Archive all marks for this student
            marks = InternalMark.query.filter_by(student_id=st.id).all()
            for m in marks:
                archived_m = ArchivedInternalMark(
                    enrollment_no=st.enrollment_no,
                    student_name=st.full_name,
                    subject_id=m.subject_id,
                    subject_code=m.subject.subject_code if m.subject else None,
                    subject_name=m.subject.subject_name if m.subject else None,
                    semester=m.semester,
                    academic_year=m.academic_year,
                    marks_obtained=m.marks_obtained,
                    max_marks=m.max_marks,
                    component_data=m.component_data
                )
                db.session.add(archived_m)

            # 3. Set status to Inactive to preserve active historical records while disabling portal login
            st.status = 'Inactive'
            archived_count += 1

        db.session.commit()
        return archived_count, None

    except Exception as e:
        db.session.rollback()
        return 0, f"Error archiving graduating students: {str(e)}"

def update_academic_settings(form_data):
    """
    Update current academic settings with validation, bidirectional cycle student transitions (Odd <-> Even),
    and optional archiving.
    Returns:
        tuple: (settings, None, archived_count, promoted_count) on success
        tuple: (None, error_message, 0, 0) on failure
    """
    try:
        settings = get_academic_settings()

        academic_year = form_data.get('academic_year', '').strip()
        semester_cycle = form_data.get('semester_cycle', '').strip()
        start_date_raw = form_data.get('cycle_start_date', '').strip()
        end_date_raw = form_data.get('cycle_end_date', '').strip()
        archive_sem6 = form_data.get('archive_sem6', 'no').strip().lower()
        move_odd_students = form_data.get('move_odd_students', 'no').strip().lower()
        move_even_students = form_data.get('move_even_students', 'no').strip().lower()
        transition_academic_year = form_data.get('transition_academic_year', 'no').strip().lower()

        # Validate required cycle start date
        if not start_date_raw:
            return None, "Cycle Start Date is required.", 0, 0

        # Validate required cycle end date
        if not end_date_raw:
            return None, "Cycle End Date is required.", 0, 0

        # Parse date strings to date objects
        try:
            start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()
        except ValueError:
            return None, "Invalid date format provided.", 0, 0

        # Validate that End Date is after Start Date
        if end_date <= start_date:
            return None, "Cycle End Date must be after Cycle Start Date.", 0, 0

        # Automatically calculate Academic Year from Cycle Start and End Dates
        if end_date.year > start_date.year:
            academic_year = f"{start_date.year}-{str(end_date.year)[-2:]}"
        else:
            academic_year = f"{start_date.year}-{str(start_date.year + 1)[-2:]}"

        # Validate required semester cycle
        if semester_cycle not in ['Odd', 'Even']:
            semester_cycle = 'Odd'

        current_year = settings.academic_year if settings else None
        year_is_new = (current_year is not None and academic_year != current_year)

        archived_count = 0
        promoted_count = 0

        # 1. New Academic Year Transition: Archive Sem 6 (set inactive) & Move Sem 2->3, 4->5 & Reset to Odd
        if year_is_new and transition_academic_year in ['yes', 'true', '1']:
            archived_count, promoted_count, trans_err = promote_even_to_odd_new_year(academic_year=current_year or academic_year)
            if trans_err:
                return None, trans_err, 0, 0
            # Academic Year transition automatically enforces Odd Semester cycle
            semester_cycle = 'Odd'

        # 2. Perform Odd-to-Even student promotion if requested (within same academic year)
        elif semester_cycle == 'Even' and move_odd_students in ['yes', 'true', '1']:
            promoted_count, prom_err = promote_odd_to_even_students(academic_year=settings.academic_year)
            if prom_err:
                return None, prom_err, 0, 0

        # 3. Perform Even-to-Odd student transition if requested (within same academic year)
        elif semester_cycle == 'Odd' and move_even_students in ['yes', 'true', '1']:
            promoted_count, prom_err = move_even_to_odd_students(academic_year=settings.academic_year)
            if prom_err:
                return None, prom_err, 0, 0

        # 4. Perform standalone archive if requested
        elif archive_sem6 in ['yes', 'true', '1']:
            archived_count, arch_err = archive_graduating_students(academic_year=settings.academic_year, semester=6)
            if arch_err:
                return None, arch_err, 0, 0

        # Save values to record
        settings.academic_year = academic_year
        settings.semester_cycle = semester_cycle
        settings.cycle_start_date = start_date
        settings.cycle_end_date = end_date

        students_per_div_raw = form_data.get('students_per_division', '').strip()
        if students_per_div_raw:
            try:
                students_per_div = int(students_per_div_raw)
                if students_per_div > 0:
                    settings.students_per_division = students_per_div
            except (ValueError, TypeError):
                pass

        # Commit changes to database
        db.session.commit()
        return settings, None, archived_count, promoted_count

    except Exception as e:
        db.session.rollback()
        return None, f"Failed to save academic settings: {str(e)}", 0, 0

def save_academic_settings(form_data):
    """
    Save academic settings (Alias for update_academic_settings).
    """
    return update_academic_settings(form_data)
