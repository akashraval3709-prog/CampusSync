# models.py
from extensions import db  # <--- MUST import from extensions
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    mobile = db.Column(db.String(15), nullable=True)
    profile_photo = db.Column(db.String(255), default='default-avatar.png')
    status = db.Column(db.Enum('Active', 'Inactive'), default='Active')
    reset_otp = db.Column(db.String(255), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, default=0, nullable=False)
    otp_blocked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username=None, password=None, full_name=None, email=None,
                 mobile=None, profile_photo='default-avatar.png', status='Active',
                 reset_otp=None, otp_expiry=None, otp_attempts=0, otp_blocked_until=None, **kwargs):
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.mobile = mobile
        self.profile_photo = profile_photo
        self.status = status
        self.reset_otp = reset_otp
        self.otp_expiry = otp_expiry
        self.otp_attempts = otp_attempts
        self.otp_blocked_until = otp_blocked_until
        for k, v in kwargs.items():
            setattr(self, k, v)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String(20), nullable=False)
    enrollment_no = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    course = db.Column(db.String(50), nullable=True)
    semester = db.Column(db.SmallInteger, nullable=True)
    division = db.Column(db.String(10), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.String(255), default='default-avatar.png')
    status = db.Column(db.Enum('Active', 'Inactive'), default='Active')
    password_changed = db.Column(db.SmallInteger, default=0)
    last_login = db.Column(db.DateTime, nullable=True)
    reset_otp = db.Column(db.String(255), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, default=0, nullable=False)
    otp_blocked_until = db.Column(db.DateTime, nullable=True)
    device_fingerprint = db.Column(db.String(500), nullable=True)
    device_model = db.Column(db.String(100), nullable=True)
    device_bound_at = db.Column(db.DateTime, nullable=True)
    device_reset_allowed = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('academic_year', 'course', 'semester', 'roll_number', name='uq_academic_course_sem_roll'),
    )

    def __init__(self, roll_number=None, enrollment_no=None, full_name=None, email=None,
                 mobile=None, dob=None, course=None, semester=None, division=None,
                 academic_year=None, password=None, profile_photo='default-avatar.png',
                 status='Active', password_changed=0, last_login=None, reset_otp=None,
                 otp_expiry=None, otp_attempts=0, otp_blocked_until=None, **kwargs):
        self.roll_number = roll_number
        self.enrollment_no = enrollment_no
        self.full_name = full_name
        self.email = email
        self.mobile = mobile
        self.dob = dob
        self.course = course
        self.semester = semester
        self.division = division
        self.academic_year = academic_year
        self.password = password
        self.profile_photo = profile_photo
        self.status = status
        self.password_changed = password_changed
        self.last_login = last_login
        self.reset_otp = reset_otp
        self.otp_expiry = otp_expiry
        self.otp_attempts = otp_attempts
        self.otp_blocked_until = otp_blocked_until
        for k, v in kwargs.items():
            setattr(self, k, v)


class CollegeSetting(db.Model):
    """
    College Settings Model
    Stores single-tenant college profile details such as name, logo, address, and contacts.
    """
    __tablename__ = 'college_settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_name = db.Column(db.String(255), nullable=False, default='CampusSync College')
    college_short_name = db.Column(db.String(50), nullable=True)
    college_type = db.Column(db.String(50), nullable=True, default='BCA')
    logo = db.Column(db.String(255), nullable=True, default='default-logo.png')
    college_stamp = db.Column(db.String(255), nullable=True, default='default-stamp.png')
    principal_signature = db.Column(db.String(255), nullable=True, default='default-signature.png')
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    principal_name = db.Column(db.String(100), nullable=True)
    established_year = db.Column(db.String(10), nullable=True)
    description = db.Column(db.Text, nullable=True)
    min_overall_attendance = db.Column(db.Float, nullable=False, default=75.0)
    min_subject_attendance = db.Column(db.Float, nullable=False, default=75.0)
    attendance_warning_threshold = db.Column(db.Float, nullable=False, default=60.0)
    campus_latitude = db.Column(db.Numeric(10, 8), nullable=True, default=23.83680000)
    campus_longitude = db.Column(db.Numeric(11, 8), nullable=True, default=72.11240000)
    campus_radius_meters = db.Column(db.Integer, nullable=True, default=150)
    campus_plus_code = db.Column(db.String(100), nullable=True, default='5C53+R58 Palanpur, Gujarat')
    college_start_time = db.Column(db.String(10), nullable=True, default='10:00')
    college_end_time = db.Column(db.String(10), nullable=True, default='17:00')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "college_name": self.college_name,
            "college_short_name": self.college_short_name,
            "college_type": self.college_type,
            "logo": self.logo,
            "college_stamp": self.college_stamp,
            "principal_signature": self.principal_signature,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "principal_name": self.principal_name
        }


class ResultDeclaration(db.Model):
    """
    Result Declaration Model
    Tracks official publication/declaration of internal assessment results by Admin.
    Controls student portal marksheet download access.
    """
    __tablename__ = 'result_declarations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.SmallInteger, nullable=False)
    division = db.Column(db.String(10), nullable=False, default='All')
    is_declared = db.Column(db.Boolean, nullable=False, default=True)
    declared_at = db.Column(db.DateTime, default=datetime.utcnow)
    declared_by = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('academic_year', 'semester', 'division', name='uq_result_decl_ay_sem_div'),
    )


class AcademicSetting(db.Model):
    """
    Academic Settings Model
    Stores current academic year, semester cycle (Odd/Even), and cycle dates.
    """
    __tablename__ = 'academic_settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    academic_year = db.Column(db.String(20), nullable=False, default='2026-27')
    semester_cycle = db.Column(db.Enum('Odd', 'Even'), nullable=False, default='Odd')
    cycle_start_date = db.Column(db.Date, nullable=True)
    cycle_end_date = db.Column(db.Date, nullable=True)
    students_per_division = db.Column(db.Integer, nullable=False, default=70)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subject(db.Model):
    """
    Subject Model
    Stores semester-wise and course-wise subject details.
    """
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_code = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(150), nullable=False)
    course = db.Column(db.String(50), nullable=False, default='BCA')
    semester = db.Column(db.SmallInteger, nullable=False, default=1)
    subject_type = db.Column(db.Enum('Theory', 'Practical'), nullable=False, default='Theory')
    credits = db.Column(db.Integer, nullable=False, default=4)
    internal_marks = db.Column(db.Integer, nullable=False, default=30)
    external_marks = db.Column(db.Integer, nullable=False, default=70)
    total_marks = db.Column(db.Integer, nullable=False, default=100)
    status = db.Column(db.Enum('Active', 'Inactive'), nullable=False, default='Active')
    component_config = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailLog(db.Model):
    """
    Email Log Model
    Tracks transactional email delivery status (PENDING, SENDING, SENT, FAILED)
    and retry count for students.
    """
    __tablename__ = 'email_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    email_type = db.Column(db.String(50), nullable=False, default='WELCOME')
    recipient_email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum('PENDING', 'SENDING', 'SENT', 'FAILED'), nullable=False, default='PENDING')
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    retry_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('email_logs', cascade='all, delete-orphan', lazy=True))


class Faculty(db.Model):
    """
    Faculty Model
    Stores faculty profile details, contact information, credentials, and employment data.
    """
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faculty_code = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    qualification = db.Column(db.String(150), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    joining_date = db.Column(db.Date, nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    profile_photo = db.Column(db.String(255), default='default-avatar.png')
    password = db.Column(db.String(255), nullable=False)
    password_changed = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.Enum('Active', 'Inactive'), default='Active', nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    reset_otp = db.Column(db.String(255), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, default=0, nullable=False)
    otp_blocked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, faculty_code=None, full_name=None, email=None, mobile=None,
                 gender=None, dob=None, qualification=None, designation=None,
                 department=None, joining_date=None, address=None, city=None,
                 state=None, pincode=None, profile_photo='default-avatar.png',
                 password=None, password_changed=False, status='Active',
                 last_login=None, reset_otp=None, otp_expiry=None, otp_attempts=0,
                 otp_blocked_until=None, **kwargs):
        self.faculty_code = faculty_code
        self.full_name = full_name
        self.email = email
        self.mobile = mobile
        self.gender = gender
        self.dob = dob
        self.qualification = qualification
        self.designation = designation
        self.department = department
        self.joining_date = joining_date
        self.address = address
        self.city = city
        self.state = state
        self.pincode = pincode
        self.profile_photo = profile_photo
        self.password = password
        self.password_changed = password_changed
        self.status = status
        self.last_login = last_login
        self.reset_otp = reset_otp
        self.otp_expiry = otp_expiry
        self.otp_attempts = otp_attempts
        self.otp_blocked_until = otp_blocked_until
        for k, v in kwargs.items():
            setattr(self, k, v)

    # Relationships
    assignments = db.relationship('FacultySubjectAssignment', backref='faculty', cascade='all, delete-orphan', lazy=True)


class FacultySubjectAssignment(db.Model):
    """
    Faculty Subject Assignment Model
    Maps Faculty to Subjects with Division allocation.
    Normalized structure allowing many-to-many relationship with division attributes.
    """
    __tablename__ = 'faculty_subject_assignments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    division = db.Column(db.String(10), nullable=False, default='A')
    status = db.Column(db.Enum('Active', 'Inactive'), default='Active', nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subject = db.relationship('Subject', backref=db.backref('faculty_assignments', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('faculty_id', 'subject_id', 'division', name='uq_faculty_subject_division'),
    )


class InternalMark(db.Model):
    """
    Internal Mark Model
    Stores internal assessment marks scored by a student for a subject in a semester/academic year.
    """
    __tablename__ = 'internal_marks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    enrollment_no = db.Column(db.String(20), nullable=True, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.SmallInteger, nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    
    # HNGU Assessment Component Breakdown Fields (Theory & Practical)
    test1 = db.Column(db.Float, nullable=True)
    test2 = db.Column(db.Float, nullable=True)
    test3 = db.Column(db.Float, nullable=True)
    internal_exam = db.Column(db.Float, nullable=True)
    active_learning = db.Column(db.Float, nullable=True)
    class_assignment = db.Column(db.Float, nullable=True)
    home_assignment = db.Column(db.Float, nullable=True)
    attendance = db.Column(db.Float, nullable=True)
    practical_eval = db.Column(db.Float, nullable=True)
    viva = db.Column(db.Float, nullable=True)
    journal = db.Column(db.Float, nullable=True)
    component_data = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('internal_marks', cascade='all, delete-orphan', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('internal_marks_records', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'semester', 'academic_year', name='uq_student_internal_mark_sem_year'),
    )


class AttendanceRecord(db.Model):
    """
    Attendance Record Model
    Stores subject-wise attendance logs for a student per semester, academic year, and division.
    """
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.SmallInteger, nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    division = db.Column(db.String(10), nullable=False, default='A')
    total_lectures = db.Column(db.Integer, nullable=False, default=0)
    attended_lectures = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('attendance_records', cascade='all, delete-orphan', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('attendance_records', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'semester', 'academic_year', name='uq_student_attendance_sem_year'),
    )


class ArchivedStudent(db.Model):
    """
    Archived Student Model
    Stores historical records of graduated students (e.g. Sem 6 completed).
    """
    __tablename__ = 'archived_students'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_student_id = db.Column(db.Integer, nullable=True)
    roll_number = db.Column(db.String(20), nullable=False)
    enrollment_no = db.Column(db.String(20), nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    course = db.Column(db.String(50), nullable=True, default='BCA')
    final_semester = db.Column(db.SmallInteger, nullable=False, default=6)
    division = db.Column(db.String(10), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    profile_photo = db.Column(db.String(255), default='default-avatar.png')
    status = db.Column(db.String(20), default='Archived')
    archived_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "original_student_id": self.original_student_id,
            "roll_number": self.roll_number,
            "enrollment_no": self.enrollment_no,
            "full_name": self.full_name,
            "email": self.email,
            "mobile": self.mobile,
            "dob": str(self.dob) if self.dob else None,
            "course": self.course,
            "final_semester": self.final_semester,
            "division": self.division,
            "academic_year": self.academic_year,
            "archived_at": str(self.archived_at) if self.archived_at else None
        }


class ArchivedInternalMark(db.Model):
    """
    Archived Internal Mark Model
    Stores historical internal assessment marks for graduated / archived students.
    """
    __tablename__ = 'archived_internal_marks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_no = db.Column(db.String(20), nullable=False, index=True)
    student_name = db.Column(db.String(100), nullable=True)
    subject_id = db.Column(db.Integer, nullable=True)
    subject_code = db.Column(db.String(20), nullable=True)
    subject_name = db.Column(db.String(150), nullable=True)
    semester = db.Column(db.SmallInteger, nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    component_data = db.Column(db.Text, nullable=True)
    archived_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "enrollment_no": self.enrollment_no,
            "student_name": self.student_name,
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "semester": self.semester,
            "academic_year": self.academic_year,
            "marks_obtained": self.marks_obtained,
            "max_marks": self.max_marks,
            "component_data": self.component_data,
            "archived_at": str(self.archived_at) if self.archived_at else None
        }


class LectureAttendanceSession(db.Model):
    """
    Lecture Attendance Session Model
    Stores daily lecture session details created by faculty (Draft or Submitted).
    """
    __tablename__ = 'lecture_attendance_sessions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.SmallInteger, nullable=False)
    division = db.Column(db.String(10), nullable=False, default='A')
    academic_year = db.Column(db.String(20), nullable=False, default='2026-27')
    lecture_date = db.Column(db.Date, nullable=False)
    lecture_no = db.Column(db.String(100), nullable=False, default='Lecture 1')
    session_type = db.Column(db.String(20), nullable=False, default='Lecture')
    start_time = db.Column(db.String(10), nullable=True)
    end_time = db.Column(db.String(10), nullable=True)
    status = db.Column(db.Enum('Draft', 'Submitted'), nullable=False, default='Draft')
    attendance_mode = db.Column(db.Enum('Manual', 'QR'), nullable=False, default='Manual')
    qr_session_token = db.Column(db.String(255), nullable=True)
    qr_session_expires_at = db.Column(db.DateTime, nullable=True)
    is_qr_active = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    faculty = db.relationship('Faculty', backref=db.backref('attendance_sessions', cascade='all, delete-orphan', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('attendance_sessions', cascade='all, delete-orphan', lazy=True))
    student_entries = db.relationship('LectureAttendanceStudent', backref='session', cascade='all, delete-orphan', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('subject_id', 'semester', 'division', 'academic_year', 'lecture_date', 'lecture_no', name='uq_lecture_session'),
    )


class LectureAttendanceStudent(db.Model):
    """
    Lecture Attendance Student Entry Model
    Stores individual student attendance status (Present / Absent) for a specific lecture session.
    """
    __tablename__ = 'lecture_attendance_students'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lecture_attendance_sessions.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Enum('Present', 'Absent'), nullable=False, default='Present')
    marked_method = db.Column(db.String(30), nullable=False, default='Manual')
    scanned_at = db.Column(db.DateTime, nullable=True)
    device_fingerprint = db.Column(db.String(500), nullable=True)
    scan_latitude = db.Column(db.Numeric(10, 8), nullable=True)
    scan_longitude = db.Column(db.Numeric(11, 8), nullable=True)
    distance_meters = db.Column(db.Float, nullable=True)
    is_verified = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    student = db.relationship('Student', backref=db.backref('lecture_attendance_entries', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='uq_session_student_attendance'),
    )


class ArchivedStudentOTP(db.Model):
    """
    Archived Student OTP Model
    Stores secure, hashed OTPs with expiry timestamps for graduated / old students viewing results.
    """
    __tablename__ = 'archived_student_otps'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_no = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    blocked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "enrollment_no": self.enrollment_no,
            "email": self.email,
            "expires_at": str(self.expires_at) if self.expires_at else None,
            "is_verified": self.is_verified,
            "attempts": self.attempts,
            "blocked_until": str(self.blocked_until) if self.blocked_until else None,
            "created_at": str(self.created_at) if self.created_at else None
        }


class AttendanceSecurityAlert(db.Model):
    """
    Attendance Security Alert Model
    Logs anti-proxy violations (duplicate device scans, out of geofence, invalid token).
    """
    __tablename__ = 'attendance_security_alerts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lecture_attendance_sessions.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    attempted_roll = db.Column(db.String(20), nullable=True)
    device_fingerprint = db.Column(db.String(500), nullable=True)
    conflicting_student_id = db.Column(db.Integer, nullable=True)
    alert_type = db.Column(db.Enum('DUPLICATE_DEVICE', 'OUT_OF_GEOFENCE', 'EXPIRED_TOKEN', 'UNBOUND_DEVICE'), nullable=False)
    alert_message = db.Column(db.Text, nullable=True)
    scan_latitude = db.Column(db.Numeric(10, 8), nullable=True)
    scan_longitude = db.Column(db.Numeric(11, 8), nullable=True)
    distance_meters = db.Column(db.Float, nullable=True)
    faculty_action = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED'), default='PENDING')
    resolved_by_faculty_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = db.relationship('LectureAttendanceSession', backref=db.backref('security_alerts', cascade='all, delete-orphan', lazy=True))
    student = db.relationship('Student', backref=db.backref('attendance_alerts', cascade='all, delete-orphan', lazy=True))



class Notification(db.Model):
    """
    Notification & Announcement Model
    Supports role-based broadcasting (Admin to All, Guest, Faculty, Student)
    and Faculty subject-based notifications with categories, assignment deadlines,
    attachments, and urgency alerts.
    """
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Categories:
    # Faculty: 'Test', 'Assignment Submit Date', 'Subject Related', 'Other'
    # Admin: 'Academic', 'Events', 'Administrative', 'Urgency', 'Holiday', 'General'
    category = db.Column(db.String(50), nullable=False, default='General')

    # Attachments: Photo or PDF circular/document
    photo_file = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(20), nullable=True)  # 'image', 'pdf', 'doc', etc.

    # Assignment Timeline (Start date & Deadline end date)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    # Creator info
    posted_by_role = db.Column(db.Enum('Admin', 'Faculty'), nullable=False, default='Admin')
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='SET NULL'), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)

    # Target Audience
    target_audience = db.Column(db.Enum('All', 'Guest', 'Faculty', 'Student'), nullable=False, default='All')
    target_semester = db.Column(db.SmallInteger, nullable=True)  # 1 to 6, NULL means all semesters
    target_division = db.Column(db.String(10), nullable=True, default='All')  # 'A', 'B', 'All', NULL means all
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)

    priority = db.Column(db.Enum('Normal', 'Important', 'Urgent'), nullable=False, default='Normal')
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Assignment Final Save & Submission Lock
    is_final_saved = db.Column(db.Boolean, nullable=False, default=False)
    final_saved_at = db.Column(db.DateTime, nullable=True)
    final_saved_by = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)

    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    admin = db.relationship('Admin', backref=db.backref('posted_notifications', lazy=True))
    faculty = db.relationship('Faculty', backref=db.backref('posted_notifications', lazy=True), foreign_keys=[faculty_id])
    subject = db.relationship('Subject', backref=db.backref('subject_notifications', lazy=True))

    @property
    def author_name(self):
        """Returns the specific name of the faculty or admin who posted the notification."""
        if self.faculty and self.faculty.full_name:
            return self.faculty.full_name
        elif self.admin and self.admin.full_name:
            return self.admin.full_name
        elif self.posted_by_role == 'Faculty' and self.subject_id:
            assign = FacultySubjectAssignment.query.filter_by(
                subject_id=self.subject_id, status='Active'
            ).first()
            if assign and assign.faculty and assign.faculty.full_name:
                return assign.faculty.full_name
        return self.posted_by_role or 'Faculty'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "category": self.category,
            "photo_file": self.photo_file,
            "file_type": self.file_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "posted_by_role": self.posted_by_role,
            "posted_by_name": self.author_name,
            "faculty_name": self.faculty.full_name if self.faculty else None,
            "target_audience": self.target_audience,
            "target_semester": self.target_semester,
            "target_division": self.target_division,
            "subject_id": self.subject_id,
            "priority": self.priority,
            "is_active": self.is_active,
            "is_final_saved": self.is_final_saved,
            "final_saved_at": self.final_saved_at.isoformat() if self.final_saved_at else None,
            "final_saved_by": self.final_saved_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AssignmentSubmission(db.Model):
    """
    Assignment Submission Model
    Tracks per-student submission verification for assignment notifications.
    Stores submission status (Pending/Submitted), timestamp, awarded marks, and faculty verification.
    """
    __tablename__ = 'assignment_submissions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    is_submitted = db.Column(db.Boolean, default=False, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=True)
    marks_awarded = db.Column(db.Float, nullable=True)
    status = db.Column(db.Enum('Pending', 'Submitted', 'Late', 'Rejected'), default='Pending', nullable=False)
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notification = db.relationship('Notification', backref=db.backref('submissions', cascade='all, delete-orphan', lazy=True))
    student = db.relationship('Student', backref=db.backref('assignment_submissions', cascade='all, delete-orphan', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('assignment_submissions', cascade='all, delete-orphan', lazy=True))
    faculty = db.relationship('Faculty', backref=db.backref('verified_submissions', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('notification_id', 'student_id', name='uq_notification_student_submission'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "notification_id": self.notification_id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "faculty_id": self.faculty_id,
            "is_submitted": self.is_submitted,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "marks_awarded": self.marks_awarded,
            "status": self.status,
            "remarks": self.remarks
        }


class GalleryItem(db.Model):
    """
    Campus Gallery Item Model
    Stores photo gallery uploads for public website and campus showcase.
    Supports categorization (Campus Life, Events & Fests, Sports, etc.),
    featured display on homepage, and status toggles.
    """
    __tablename__ = 'gallery_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Campus Life')
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(255), nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    views_count = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.Enum('Active', 'Inactive'), default='Active', nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    uploaded_by = db.relationship('Admin', backref=db.backref('gallery_uploads', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "image_file": self.image_file,
            "is_featured": self.is_featured,
            "views_count": self.views_count,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class HomePageSetting(db.Model):
    """
    Public Home Page Content Management Model
    Allows administrators to dynamically manage hero banners, live statistical counters,
    breaking news ticker, and key capability highlight cards from the Admin Panel.
    """
    __tablename__ = 'home_page_settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 1. Hero Banner Section
    hero_headline = db.Column(db.String(255), nullable=False, default='CampusSync Digital ERP')
    hero_subtitle = db.Column(db.Text, nullable=False, default='A unified platform to streamline QR attendance, exam results, faculty registers, and campus announcements — all in one place.')
    hero_pill_badge = db.Column(db.String(120), nullable=False, default='✨ Smart QR Attendance System')
    hero_banner_image = db.Column(db.String(255), nullable=True)
    hero_cta1_text = db.Column(db.String(60), nullable=False, default='Access Portals')
    hero_cta1_link = db.Column(db.String(255), nullable=False, default='#portals')
    hero_cta2_text = db.Column(db.String(60), nullable=False, default='Explore Features')
    hero_cta2_link = db.Column(db.String(255), nullable=False, default='#features')

    # 2. Campus Statistics Counters (4 customizable counters)
    stat1_number = db.Column(db.String(50), nullable=False, default='5,000+')
    stat1_label = db.Column(db.String(100), nullable=False, default='Enrolled Students')
    stat1_active = db.Column(db.Boolean, nullable=False, default=True)

    stat2_number = db.Column(db.String(50), nullable=False, default='150+')
    stat2_label = db.Column(db.String(100), nullable=False, default='Faculty Members')
    stat2_active = db.Column(db.Boolean, nullable=False, default=True)

    stat3_number = db.Column(db.String(50), nullable=False, default='99.8%')
    stat3_label = db.Column(db.String(100), nullable=False, default='Attendance Accuracy')
    stat3_active = db.Column(db.Boolean, nullable=False, default=True)

    stat4_number = db.Column(db.String(50), nullable=False, default='100%')
    stat4_label = db.Column(db.String(100), nullable=False, default='Placement Assistance')
    stat4_active = db.Column(db.Boolean, nullable=False, default=True)

    # 3. News Ticker
    ticker_active = db.Column(db.Boolean, nullable=False, default=True)
    ticker_badge = db.Column(db.String(50), nullable=False, default='LATEST')
    ticker_text = db.Column(db.Text, nullable=False, default='Admissions open for Academic Year 2026-27. Submit applications online via student portal.')

    # 4. Feature Highlights (4 cards)
    feat1_title = db.Column(db.String(100), nullable=False, default='QR Attendance')
    feat1_desc = db.Column(db.Text, nullable=False, default='Faculty generates dynamic QR to prevent proxy attendance.')

    feat2_title = db.Column(db.String(100), nullable=False, default='Grade Entry')
    feat2_desc = db.Column(db.Text, nullable=False, default='Streamlined internal mark submission and grading tables.')

    feat3_title = db.Column(db.String(100), nullable=False, default='Web Management')
    feat3_desc = db.Column(db.Text, nullable=False, default='Admin manages banners, galleries, and public notices easily.')

    feat4_title = db.Column(db.String(100), nullable=False, default='Yearly Reports')
    feat4_desc = db.Column(db.Text, nullable=False, default='Visual yearly analytics on attendance and pass rates.')

    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_settings(cls):
        """Returns the singleton HomePageSetting row, creating it if it doesn't exist."""
        setting = cls.query.first()
        if not setting:
            setting = cls()
            db.session.add(setting)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
        return setting