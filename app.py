from flask import Flask, send_from_directory, session, request, redirect, url_for, flash
import os
import traceback
from datetime import datetime
from sqlalchemy import inspect

from config import Config
from extensions import db, mail
from utils.db import test_connection

# Import Blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.faculty import faculty_bp
from routes.student import student_bp
from routes.alumni import alumni_bp
from routes.api import api_bp

# Initialize Flask application
app = Flask(__name__)

# Apply ProxyFix for reverse proxy deployments (Railway, Cloudflare, Nginx)
# Accurately detects HTTPS protocol and client IP via X-Forwarded-* headers
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

# Load configuration settings (Secret key, Database credentials)
app.config.from_object(Config)
db.init_app(app)
mail.init_app(app)

# High-Performance Compression: automatically compress HTML, CSS, JS, and JSON via Gzip/Brotli
try:
    from flask_compress import Compress
    Compress(app)
except ImportError:
    pass

# ------------------------------------------------------------------------------
# Security: Enforce HTTPS in Production Deployments
# ------------------------------------------------------------------------------
@app.before_request
def enforce_https():
    """Redirect plain HTTP requests to HTTPS on production deployments only."""
    # Never enforce HTTPS on localhost, 127.0.0.1, or local area network IPs
    host = request.host.split(':')[0].lower()
    if host in ('localhost', '127.0.0.1', '0.0.0.0') or host.startswith('192.168.') or host.startswith('10.') or host.endswith('.local'):
        return

    proto = request.headers.get('X-Forwarded-Proto', request.scheme)
    if proto == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)


# ------------------------------------------------------------------------------
# Security: Session Inactivity Timeout (30 Minutes)
# ------------------------------------------------------------------------------
@app.before_request
def enforce_session_inactivity_timeout():
    """
    Enforces a 30-minute inactivity session expiry.
    If 30 minutes pass without requests from the logged-in user, clears session
    and redirects user to the respective login page.
    """
    # Skip static files, assets, and uploaded media routes
    if request.endpoint == 'static' or request.path.startswith('/static') or request.path.startswith('/assets') or request.path.startswith('/uploads'):
        return

    is_admin = 'admin_id' in session
    is_faculty = 'faculty_id' in session
    is_student = 'student_id' in session

    if not (is_admin or is_faculty or is_student):
        return

    now_ts = datetime.utcnow().timestamp()
    last_active = session.get('last_active')
    TIMEOUT_SECONDS = 1800  # 30 minutes (1800 seconds)

    if last_active and (now_ts - last_active > TIMEOUT_SECONDS):
        target_login = 'student_login'
        if is_admin:
            target_login = 'admin_login'
        elif is_faculty:
            target_login = 'faculty_login'

        session.clear()
        flash("Your session has expired due to 30 minutes of inactivity. Please log in again.", "warning")
        return redirect(url_for(target_login, expired='1'))

    # Update activity timestamp and keep session permanent
    session['last_active'] = now_ts
    session.permanent = True


# ------------------------------------------------------------------------------
# Security & Performance: Cache-Control Headers
# ------------------------------------------------------------------------------
@app.after_request
def add_cache_control_headers(response):
    """
    Prevents browser from caching authenticated/dynamic pages.
    When a logged-out user clicks the browser 'Back' button, the browser is
    forced to re-request the page from the server, preventing dashboard display.

    Static assets and uploaded media files are cached by the browser for high performance
    and instant sub-millisecond subsequent loads.
    """
    if request.path.startswith('/static') or request.path.startswith('/assets') or request.path.startswith('/uploads'):
        response.headers["Cache-Control"] = "public, max-age=86400"
        return response

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Global context processor to inject college settings dynamically into all templates
from services.college_service import get_college_settings

@app.context_processor
def inject_global_college():
    """Injects dynamic college settings into all Jinja templates across the entire website."""
    try:
        college = get_college_settings()
    except Exception:
        college = None
    return dict(college=college)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(student_bp)
app.register_blueprint(alumni_bp)
app.register_blueprint(api_bp)

# Register endpoint aliases for backward compatibility with existing templates calling url_for('endpoint_name')
for rule in list(app.url_map.iter_rules()):
    if '.' in rule.endpoint:
        short_ep = rule.endpoint.split('.', 1)[1]
        if short_ep not in app.view_functions:
            app.view_functions[short_ep] = app.view_functions[rule.endpoint]
            app.add_url_rule(rule.rule, endpoint=short_ep, view_func=app.view_functions[rule.endpoint], methods=rule.methods)

# Auto-create tables from SQLAlchemy models if they don't exist
with app.app_context():
    import models
    from models import (
        Admin, Student, CollegeSetting, AcademicSetting, Subject, EmailLog,
        Faculty, FacultySubjectAssignment, InternalMark, AttendanceRecord,
        ArchivedStudent, ArchivedInternalMark, ArchivedStudentOTP, Notification, NotificationRead,
        AssignmentSubmission, GalleryItem, HomePageSetting, ResultDeclaration,
        LectureAttendanceSession, LectureAttendanceStudent, AttendanceSecurityAlert
    )
    upload_dirs = [
        'admin', 'assignments', 'college', 'excel', 'faculty',
        'gallery', 'homepage', 'notices', 'notifications', 'students', 'student'
    ]
    for sub in upload_dirs:
        os.makedirs(os.path.join(app.root_path, 'uploads', sub), exist_ok=True)
    try:
        print(f"DEBUG: Connected to -> {db.engine.url}")

        inspector_before = inspect(db.engine)
        print(f"DEBUG: Tables in MySQL BEFORE create_all -> {inspector_before.get_table_names()}")

        db.create_all()

        # IMPORTANT: dispose + fresh inspector to avoid a stale connection cache
        db.engine.dispose()
        inspector_after = inspect(db.engine)
        actual_tables = inspector_after.get_table_names()
        print(f"DEBUG: Tables in MySQL AFTER create_all -> {actual_tables}")

        # Auto-seed default Administrator if admins table is empty
        if 'admins' in actual_tables:
            try:
                if Admin.query.first() is None:
                    from werkzeug.security import generate_password_hash
                    default_admin = Admin(
                        username='admin',
                        password=generate_password_hash('admin'),
                        full_name='System Administrator',
                        email='admin@campussync.edu',
                        status='Active'
                    )
                    db.session.add(default_admin)
                    db.session.commit()
                    print("SUCCESS: Default administrator account ('admin' / 'admin') initialized.")
            except Exception as seed_err:
                print(f"Notice: Admin auto-seed error: {seed_err}")

        if 'students' not in actual_tables:
            print("ERROR: 'students' table STILL missing after create_all()! "
                  "Check MySQL user privileges (CREATE TABLE) and DB_NAME in .env")
        else:
            print("SUCCESS: 'students' table confirmed present in MySQL.")

        if 'gallery_items' in actual_tables:
            print("SUCCESS: 'gallery_items' table confirmed present in MySQL.")
            g_cols = [c['name'] for c in inspector_after.get_columns('gallery_items')]
            if 'views_count' not in g_cols:
                with db.engine.connect() as conn:
                    try:
                        conn.execute(db.text("ALTER TABLE gallery_items ADD COLUMN views_count INT NOT NULL DEFAULT 0"))
                        conn.commit()
                        print("SUCCESS: Added 'views_count' column to 'gallery_items'.")
                    except Exception as ge:
                        print(f"Notice: Could not add views_count: {ge}")

        if 'students' in actual_tables:
            stud_cols = [c['name'] for c in inspector_after.get_columns('students')]
            if 'academic_year' not in stud_cols:
                print("Migrating database: Adding missing 'academic_year' column to 'students' table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE students ADD COLUMN academic_year VARCHAR(20) NULL"))
                    conn.commit()
                print("SUCCESS: Added 'academic_year' column to 'students'.")

            # Missing device fingerprint columns
            student_new_cols = [
                ('device_fingerprint', 'VARCHAR(500) NULL'),
                ('device_model', 'VARCHAR(100) NULL'),
                ('device_bound_at', 'DATETIME NULL'),
                ('device_reset_allowed', 'SMALLINT DEFAULT 0')
            ]
            with db.engine.connect() as conn:
                for col_name, col_def in student_new_cols:
                    if col_name not in stud_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE students ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                            print(f"SUCCESS: Added '{col_name}' column to 'students'.")
                        except Exception as e:
                            print(f"Notice: Could not add {col_name} to students: {e}")

            # Check existing indexes on 'students' table to migrate unique constraints safely
            stud_indexes = inspector_after.get_indexes('students')
            index_names = [idx['name'] for idx in stud_indexes]

            with db.engine.connect() as conn:
                # Drop old single-column unique index on roll_number if present
                if 'roll_number' in index_names:
                    print("Migrating database: Dropping old single-column UNIQUE index on 'roll_number'...")
                    try:
                        conn.execute(db.text("ALTER TABLE students DROP INDEX roll_number"))
                        conn.commit()
                        print("SUCCESS: Dropped old 'roll_number' UNIQUE index.")
                    except Exception as drop_err:
                        print(f"Notice: Could not drop old roll_number index: {drop_err}")

                # Drop old composite UNIQUE constraint (academic_year, course, roll_number) if present
                if 'uq_academic_course_roll' in index_names:
                    print("Migrating database: Dropping redundant UNIQUE constraint uq_academic_course_roll...")
                    try:
                        conn.execute(db.text("ALTER TABLE students DROP INDEX uq_academic_course_roll"))
                        conn.commit()
                        print("SUCCESS: Dropped old uq_academic_course_roll UNIQUE constraint.")
                    except Exception as drop_err:
                        print(f"Notice: Could not drop uq_academic_course_roll: {drop_err}")

                # Add composite UNIQUE constraint (academic_year, course, semester, roll_number) if not present
                if 'uq_academic_course_sem_roll' not in index_names:
                    print("Migrating database: Adding composite UNIQUE constraint uq_academic_course_sem_roll...")
                    try:
                        conn.execute(db.text("ALTER TABLE students ADD CONSTRAINT uq_academic_course_sem_roll UNIQUE (academic_year, course, semester, roll_number)"))
                        conn.commit()
                        print("SUCCESS: Added composite UNIQUE constraint uq_academic_course_sem_roll.")
                    except Exception as add_err:
                        print(f"Notice: Could not add uq_academic_course_sem_roll: {add_err}")

        if 'academic_settings' in actual_tables:
            acad_cols = [c['name'] for c in inspector_after.get_columns('academic_settings')]
            if 'students_per_division' not in acad_cols:
                print("Migrating database: Adding missing 'students_per_division' column to 'academic_settings' table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE academic_settings ADD COLUMN students_per_division INT NOT NULL DEFAULT 70"))
                    conn.commit()
                print("SUCCESS: Added 'students_per_division' column to 'academic_settings'.")

        if 'college_settings' in actual_tables:
            columns = [c['name'] for c in inspector_after.get_columns('college_settings')]
            if 'college_type' not in columns:
                print("Migrating database: Adding missing 'college_type' column to 'college_settings' table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE college_settings ADD COLUMN college_type VARCHAR(50) NULL DEFAULT 'BCA'"))
                    conn.commit()
                print("SUCCESS: Added 'college_type' column to 'college_settings'.")

        if 'subjects' in actual_tables:
            subj_cols = [c['name'] for c in inspector_after.get_columns('subjects')]
            if 'internal_marks' not in subj_cols:
                print("Migrating database: Adding missing exam marks columns to 'subjects' table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE subjects ADD COLUMN internal_marks INT NOT NULL DEFAULT 30, ADD COLUMN external_marks INT NOT NULL DEFAULT 70, ADD COLUMN total_marks INT NOT NULL DEFAULT 100"))
                    conn.commit()
                print("SUCCESS: Added exam marks columns to 'subjects'.")
            if 'component_config' not in subj_cols:
                print("Migrating database: Adding missing 'component_config' column to 'subjects' table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE subjects ADD COLUMN component_config TEXT NULL"))
                    conn.commit()
                print("SUCCESS: Added 'component_config' column to 'subjects'.")

        if 'internal_marks' in actual_tables:
            im_cols = [c['name'] for c in inspector_after.get_columns('internal_marks')]
            needed_cols = [
                ('test1', 'FLOAT NULL'), ('test2', 'FLOAT NULL'), ('test3', 'FLOAT NULL'),
                ('internal_exam', 'FLOAT NULL'),
                ('active_learning', 'FLOAT NULL'), ('class_assignment', 'FLOAT NULL'), ('home_assignment', 'FLOAT NULL'),
                ('attendance', 'FLOAT NULL'), ('practical_eval', 'FLOAT NULL'), ('viva', 'FLOAT NULL'),
                ('journal', 'FLOAT NULL'), ('component_data', 'TEXT NULL')
            ]
            missing_cols = [col for col in needed_cols if col[0] not in im_cols]
            if missing_cols:
                print("Migrating database: Adding missing component columns to 'internal_marks' table...")
                with db.engine.connect() as conn:
                    for col_name, col_type in missing_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE internal_marks ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                        except Exception as col_err:
                            print(f"Notice: Could not add column {col_name}: {col_err}")
                print("SUCCESS: Component columns verified/added in 'internal_marks'.")

            # Automatically drop legacy unused quiz columns if present in database
            legacy_quiz_cols = [c for c in ['quiz1', 'quiz2', 'quiz3', 'quiz4'] if c in im_cols]
            if legacy_quiz_cols:
                print(f"Migrating database: Dropping legacy unused quiz columns from 'internal_marks': {legacy_quiz_cols}...")
                with db.engine.connect() as conn:
                    for col_name in legacy_quiz_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE internal_marks DROP COLUMN {col_name}"))
                            conn.commit()
                        except Exception as drop_err:
                            print(f"Notice: Could not drop column {col_name}: {drop_err}")
                print("SUCCESS: Removed legacy quiz columns from 'internal_marks'.")

        # Migrate reset_otp and otp_expiry for Password Reset Feature
        for tbl_name in ['students', 'faculty', 'admins']:
            if tbl_name in actual_tables:
                t_cols = [c['name'] for c in inspector_after.get_columns(tbl_name)]
                with db.engine.connect() as conn:
                    if 'reset_otp' not in t_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE {tbl_name} ADD COLUMN reset_otp VARCHAR(255) NULL"))
                            conn.commit()
                            print(f"SUCCESS: Added 'reset_otp' column to '{tbl_name}'.")
                        except Exception as e:
                            print(f"Notice: Could not add reset_otp to {tbl_name}: {e}")
                    if 'otp_expiry' not in t_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE {tbl_name} ADD COLUMN otp_expiry DATETIME NULL"))
                            conn.commit()
                            print(f"SUCCESS: Added 'otp_expiry' column to '{tbl_name}'.")
                        except Exception as e:
                            print(f"Notice: Could not add otp_expiry to {tbl_name}: {e}")
                    if 'otp_attempts' not in t_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE {tbl_name} ADD COLUMN otp_attempts INT NOT NULL DEFAULT 0"))
                            conn.commit()
                            print(f"SUCCESS: Added 'otp_attempts' column to '{tbl_name}'.")
                        except Exception as e:
                            print(f"Notice: Could not add otp_attempts to {tbl_name}: {e}")
                    if 'otp_blocked_until' not in t_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE {tbl_name} ADD COLUMN otp_blocked_until DATETIME NULL"))
                            conn.commit()
                            print(f"SUCCESS: Added 'otp_blocked_until' column to '{tbl_name}'.")
                        except Exception as e:
                            print(f"Notice: Could not add otp_blocked_until to {tbl_name}: {e}")

        # Migrate all columns for notifications table
        if 'notifications' in actual_tables:
            notif_cols = [c['name'] for c in inspector_after.get_columns('notifications')]
            notif_new_cols = [
                ('category', "VARCHAR(50) NOT NULL DEFAULT 'General'"),
                ('photo_file', "VARCHAR(255) NULL"),
                ('file_type', "VARCHAR(20) NULL"),
                ('start_date', "DATETIME NULL"),
                ('end_date', "DATETIME NULL"),
                ('posted_by_role', "ENUM('Admin','Faculty') NOT NULL DEFAULT 'Admin'"),
                ('admin_id', "INT NULL"),
                ('faculty_id', "INT NULL"),
                ('target_audience', "ENUM('All','Guest','Faculty','Student') NOT NULL DEFAULT 'All'"),
                ('target_semester', "SMALLINT NULL"),
                ('target_division', "VARCHAR(10) NULL DEFAULT 'All'"),
                ('subject_id', "INT NULL"),
                ('target_student_id', "INT NULL"),
                ('priority', "ENUM('Normal','Important','Urgent') NOT NULL DEFAULT 'Normal'"),
                ('is_active', "TINYINT(1) NOT NULL DEFAULT 1"),
                ('is_final_saved', "TINYINT(1) NOT NULL DEFAULT 0"),
                ('final_saved_at', "DATETIME NULL"),
                ('final_saved_by', "INT NULL")
            ]
            with db.engine.connect() as conn:
                for col_name, col_def in notif_new_cols:
                    if col_name not in notif_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE notifications ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                            print(f"SUCCESS: Added '{col_name}' column to 'notifications'.")
                        except Exception as e:
                            print(f"Notice: Could not add {col_name} to notifications: {e}")

                try:
                    conn.execute(db.text("ALTER TABLE notifications CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    conn.commit()
                except Exception:
                    pass

        # Migrate college_settings Campus Geofencing & College Timing Columns
        if 'college_settings' in actual_tables:
            cs_cols = [c['name'] for c in inspector_after.get_columns('college_settings')]
            cs_new_cols = [
                ('campus_latitude', 'DECIMAL(10,8) DEFAULT 24.15953750'),
                ('campus_longitude', 'DECIMAL(11,8) DEFAULT 72.40295313'),
                ('campus_radius_meters', 'INT DEFAULT 800'),
                ('campus_plus_code', "VARCHAR(100) DEFAULT '5C53+R58 Palanpur, Gujarat'"),
                ('college_start_time', "VARCHAR(10) DEFAULT '10:00'"),
                ('college_end_time', "VARCHAR(10) DEFAULT '17:00'")
            ]
            with db.engine.connect() as conn:
                for col_name, col_def in cs_new_cols:
                    if col_name not in cs_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE college_settings ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                            print(f"SUCCESS: Added '{col_name}' to 'college_settings'.")
                        except Exception as e:
                            print(f"Notice: Could not add {col_name} to college_settings: {e}")

        # Migrate lecture_attendance_sessions QR Attendance Columns
        if 'lecture_attendance_sessions' in actual_tables:
            las_cols = [c['name'] for c in inspector_after.get_columns('lecture_attendance_sessions')]
            las_new_cols = [
                ('attendance_mode', "VARCHAR(20) DEFAULT 'Manual'"),
                ('qr_session_token', 'VARCHAR(255) NULL'),
                ('qr_session_expires_at', 'DATETIME NULL'),
                ('is_qr_active', 'TINYINT(1) DEFAULT 0'),
                ('session_type', "VARCHAR(20) DEFAULT 'Lecture'"),
                ('start_time', 'VARCHAR(10) NULL'),
                ('end_time', 'VARCHAR(10) NULL')
            ]
            with db.engine.connect() as conn:
                for col_name, col_def in las_new_cols:
                    if col_name not in las_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE lecture_attendance_sessions ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                            print(f"SUCCESS: Added '{col_name}' to 'lecture_attendance_sessions'.")
                        except Exception as e:
                            print(f"Notice: Could not add {col_name} to lecture_attendance_sessions: {e}")

        # Migrate lecture_attendance_students QR Scanned & Geolocation Columns
        if 'lecture_attendance_students' in actual_tables:
            lat_cols = [c['name'] for c in inspector_after.get_columns('lecture_attendance_students')]
            lat_new_cols = [
                ('marked_method', "VARCHAR(30) DEFAULT 'MANUAL'"),
                ('scanned_at', 'DATETIME NULL'),
                ('device_fingerprint', 'VARCHAR(500) NULL'),
                ('scan_latitude', 'DECIMAL(10,8) NULL'),
                ('scan_longitude', 'DECIMAL(11,8) NULL'),
                ('distance_meters', 'FLOAT NULL'),
                ('is_verified', 'TINYINT(1) DEFAULT 1')
            ]
            with db.engine.connect() as conn:
                for col_name, col_def in lat_new_cols:
                    if col_name not in lat_cols:
                        try:
                            conn.execute(db.text(f"ALTER TABLE lecture_attendance_students ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                            print(f"SUCCESS: Added '{col_name}' to 'lecture_attendance_students'.")
                        except Exception as e:
                            print(f"Notice: Could not add {col_name} to lecture_attendance_students: {e}")

        # Ensure attendance_security_alerts table exists
        with db.engine.connect() as conn:
            try:
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS attendance_security_alerts (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        session_id INT NOT NULL,
                        student_id INT NOT NULL,
                        attempted_roll VARCHAR(20) NULL,
                        device_fingerprint VARCHAR(500) NULL,
                        conflicting_student_id INT NULL,
                        alert_type ENUM('DUPLICATE_DEVICE','OUT_OF_GEOFENCE','EXPIRED_TOKEN','UNBOUND_DEVICE') NOT NULL,
                        alert_message TEXT NULL,
                        scan_latitude DECIMAL(10,8) NULL,
                        scan_longitude DECIMAL(11,8) NULL,
                        distance_meters FLOAT NULL,
                        faculty_action ENUM('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
                        resolved_by_faculty_id INT NULL,
                        created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
            except Exception as e:
                print(f"Notice: Could not ensure attendance_security_alerts table: {e}")

            # Ensure notification_reads table exists
            try:
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS notification_reads (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        notification_id INT NOT NULL,
                        user_role ENUM('Admin', 'Faculty', 'Student') NOT NULL,
                        user_id INT NOT NULL,
                        read_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY uq_notification_user_read (notification_id, user_role, user_id),
                        KEY idx_user_role_id (user_role, user_id)
                    )
                """))
                conn.commit()
                print("SUCCESS: Ensured 'notification_reads' table in MySQL.")
            except Exception as e:
                print(f"Notice: Could not ensure notification_reads table: {e}")

    except Exception as e:
        print("--------------------------------------------------")
        print("SQLAlchemy Table Creation ERROR (FULL TRACEBACK):")
        traceback.print_exc()
        print("--------------------------------------------------")

# Test Database Connection on server startup
print("--------------------------------------------------")
print("Initializing CampusSync Application Backend...")
if test_connection():
    print("SUCCESS: Database connection to 'campussync' established successfully!")
else:
    print("WARNING: Could not connect to MySQL database. Please check your .env settings or import database/campussync.sql.")
print("--------------------------------------------------")

# Serve assets fallback handler
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, filename)

# Universal uploads file serving handler
@app.route('/uploads/<path:filename>', endpoint='global_serve_uploads')
def global_serve_uploads(filename):
    uploads_dir = os.path.join(app.root_path, 'uploads')
    target_path = os.path.join(uploads_dir, filename)
    if not os.path.exists(target_path):
        if filename.startswith('student/'):
            alt = os.path.join(uploads_dir, 'students', filename[len('student/'):])
            if os.path.exists(alt):
                return send_from_directory(os.path.join(uploads_dir, 'students'), filename[len('student/'):])
        elif filename.startswith('students/'):
            alt = os.path.join(uploads_dir, 'student', filename[len('students/'):])
            if os.path.exists(alt):
                return send_from_directory(os.path.join(uploads_dir, 'student'), filename[len('students/'):])
# ------------------------------------------------------------------------------
# Test Email Route (Brevo API Production Verification)
# ------------------------------------------------------------------------------
@app.route('/test-email')
@app.route('/test-mail')
def test_email_route():
    """
    Direct browser test endpoint to verify Brevo HTTPS API email delivery on Railway.
    Usage: /test-email or /test-email?to=your_email@gmail.com
    """
    to_email = request.args.get('to', app.config.get('MAIL_DEFAULT_SENDER', 'devidparmar8954@gmail.com'))
    from mail.brevo_service import is_brevo_configured, send_brevo_email
    brevo_active = is_brevo_configured()
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
        <h2 style="color: #2563eb; margin-top: 0;">🎉 CampusSync - Brevo Email Test Successful!</h2>
        <p style="font-size: 15px; color: #334155;">This is a live test email sent directly from <strong>CampusSync ERP on Railway</strong>.</p>
        <div style="background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; margin: 16px 0;">
            <p style="margin: 4px 0;"><strong>Brevo API Status:</strong> <span style="color: #16a34a; font-weight: bold;">ACTIVE (Port 443 HTTPS)</span></p>
            <p style="margin: 4px 0;"><strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p style="margin: 4px 0;"><strong>Delivered To:</strong> {to_email}</p>
        </div>
        <p style="color: #64748b; font-size: 13px; margin-bottom: 0;">If you see this in your inbox, your email delivery system is working 100% on Railway!</p>
    </div>
    """
    
    if brevo_active:
        success, info = send_brevo_email(
            to_email=to_email,
            subject="CampusSync - Brevo Email Test Successful",
            html_content=html,
            to_name="CampusSync Admin",
            text_content="CampusSync live email test via Brevo was successful!"
        )
        if success:
            return f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 50px auto; padding: 30px; border-radius: 14px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <h2 style="margin-top: 0; color: #047857;">✅ Email Sent Successfully via Brevo!</h2>
                <p style="font-size: 15px;">A live test email was successfully dispatched to: <strong>{to_email}</strong></p>
                <p style="font-size: 13px; color: #065f46; background: #d1fae5; padding: 10px 14px; border-radius: 8px;"><strong>Brevo Message ID:</strong> <code>{info}</code></p>
                <p style="margin-top: 20px; font-weight: 500;">Your Railway environment, Brevo API key, and HTTPS email delivery are functioning <strong>100% correctly</strong>!</p>
                <div style="margin-top: 24px;">
                    <a href="/admin/email-logs" style="display: inline-block; background: #059669; color: #ffffff; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-right: 10px;">Go to Email Logs</a>
                    <a href="/admin/login" style="display: inline-block; background: #ffffff; color: #059669; border: 1px solid #059669; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 600;">Admin Login</a>
                </div>
            </div>
            """
        else:
            return f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 50px auto; padding: 30px; border-radius: 14px; background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <h2 style="margin-top: 0; color: #b91c1c;">❌ Brevo Email Delivery Failed</h2>
                <p>Attempted to send to: <strong>{to_email}</strong></p>
                <div style="background: #fee2e2; padding: 12px 14px; border-radius: 8px; font-family: monospace; font-size: 13px; margin: 16px 0; word-break: break-all;">
                    {info}
                </div>
                <p style="font-size: 14px; color: #7f1d1d;"><strong>Troubleshooting Tip:</strong> Ensure that your <code>MAIL_DEFAULT_SENDER</code> in Railway matches the verified sender in your Brevo account.</p>
            </div>
            """, 500
    else:
        return f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 50px auto; padding: 30px; border-radius: 14px; background: #fffbeb; border: 1px solid #fde68a; color: #92400e; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <h2 style="margin-top: 0; color: #b45309;">⚠️ BREVO_API_KEY Not Found</h2>
            <p>The <code>BREVO_API_KEY</code> environment variable is missing or empty on this server.</p>
            <p>Please ensure you added <code>BREVO_API_KEY</code> in Railway Dashboard ➔ Variables and clicked <strong>Deploy</strong>.</p>
        </div>
        """, 400

# Production Error Handlers
from flask import render_template

@app.errorhandler(404)
def handle_404_error(e):
    return render_template('public/404.html'), 404

@app.errorhandler(500)
def handle_500_error(e):
    try:
        db.session.rollback()
    except Exception:
        pass
    from flask import request
    app.logger.error(f"500 Internal Server Error at {request.path}: {e}", exc_info=True)
    return render_template('public/500.html'), 500

@app.errorhandler(403)
def handle_403_error(e):
    return render_template('public/403.html'), 403

# Run Flask server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host=host, port=port, debug=debug)