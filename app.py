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

# Auto-create tables and perform resilient database migrations
def run_all_database_migrations():
    """
    Comprehensive, resilient database schema migration for MySQL.
    Every single table and column is checked and altered in its own isolated try-except block,
    ensuring that errors in one table never cascade or abort migrations in other tables.
    """
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

    report = {"migrated": [], "errors": []}

    try:
        db.create_all()
    except Exception as e:
        report["errors"].append(f"create_all: {e}")

    try:
        db.engine.dispose()
    except Exception:
        pass

    # 1. PRIORITY 1: Notifications table columns (especially target_student_id)
    try:
        from services.notification_service import ensure_notification_columns, ensure_notification_reads_table
        ensure_notification_columns()
        ensure_notification_reads_table()
        report["migrated"].append("notifications_and_reads")
    except Exception as e:
        report["errors"].append(f"ensure_notification_columns: {e}")

    # 2. attendance_security_alerts table
    try:
        with db.engine.connect() as conn:
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
            report["migrated"].append("attendance_security_alerts")
    except Exception as e:
        report["errors"].append(f"attendance_security_alerts: {e}")

    # 3. students table columns and constraints
    try:
        with db.engine.connect() as conn:
            s_existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM students")).fetchall()
                s_existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass

            student_cols = [
                ('academic_year', 'VARCHAR(20) NULL'),
                ('device_fingerprint', 'VARCHAR(500) NULL'),
                ('device_model', 'VARCHAR(100) NULL'),
                ('device_bound_at', 'DATETIME NULL'),
                ('device_reset_allowed', 'SMALLINT DEFAULT 0')
            ]
            for col_name, col_def in student_cols:
                if col_name.lower() not in s_existing:
                    try:
                        conn.execute(db.text(f"ALTER TABLE students ADD COLUMN {col_name} {col_def}"))
                        conn.commit()
                        s_existing.add(col_name.lower())
                        report["migrated"].append(f"students.{col_name}")
                    except Exception as err:
                        report["errors"].append(f"students.{col_name}: {err}")

            # Index migrations for students
            try:
                res_idx = conn.execute(db.text("SHOW INDEX FROM students")).fetchall()
                idx_names = {str(r[2]) for r in res_idx if len(r) > 2}
            except Exception:
                idx_names = set()

            if 'roll_number' in idx_names:
                try:
                    conn.execute(db.text("ALTER TABLE students DROP INDEX roll_number"))
                    conn.commit()
                except Exception:
                    pass

            if 'uq_academic_course_roll' in idx_names:
                try:
                    conn.execute(db.text("ALTER TABLE students DROP INDEX uq_academic_course_roll"))
                    conn.commit()
                except Exception:
                    pass

            if 'uq_academic_course_sem_roll' not in idx_names:
                try:
                    conn.execute(db.text("ALTER TABLE students ADD CONSTRAINT uq_academic_course_sem_roll UNIQUE (academic_year, course, semester, roll_number)"))
                    conn.commit()
                except Exception:
                    pass
    except Exception as e:
        report["errors"].append(f"students_table: {e}")

    # 4. Default Administrator auto-seed
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
            report["migrated"].append("default_admin_seeded")
    except Exception as e:
        db.session.rollback()
        report["errors"].append(f"admin_autoseed: {e}")

    # 5. academic_settings table
    try:
        with db.engine.connect() as conn:
            existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM academic_settings")).fetchall()
                existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass
            if 'students_per_division' not in existing:
                try:
                    conn.execute(db.text("ALTER TABLE academic_settings ADD COLUMN students_per_division INT NOT NULL DEFAULT 70"))
                    conn.commit()
                    report["migrated"].append("academic_settings.students_per_division")
                except Exception as err:
                    report["errors"].append(f"academic_settings: {err}")
    except Exception as e:
        report["errors"].append(f"academic_settings_block: {e}")

    # 6. college_settings table
    try:
        with db.engine.connect() as conn:
            existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM college_settings")).fetchall()
                existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass

            cs_cols = [
                ('college_type', "VARCHAR(50) NULL DEFAULT 'BCA'"),
                ('campus_latitude', 'DECIMAL(10,8) DEFAULT 24.15953750'),
                ('campus_longitude', 'DECIMAL(11,8) DEFAULT 72.40295313'),
                ('campus_radius_meters', 'INT DEFAULT 800'),
                ('campus_plus_code', "VARCHAR(100) DEFAULT '5C53+R58 Palanpur, Gujarat'"),
                ('college_start_time', "VARCHAR(10) DEFAULT '10:00'"),
                ('college_end_time', "VARCHAR(10) DEFAULT '17:00'")
            ]
            for col_name, col_def in cs_cols:
                if col_name.lower() not in existing:
                    try:
                        conn.execute(db.text(f"ALTER TABLE college_settings ADD COLUMN {col_name} {col_def}"))
                        conn.commit()
                        existing.add(col_name.lower())
                        report["migrated"].append(f"college_settings.{col_name}")
                    except Exception as err:
                        report["errors"].append(f"college_settings.{col_name}: {err}")
    except Exception as e:
        report["errors"].append(f"college_settings_block: {e}")

    # 7. subjects table
    try:
        with db.engine.connect() as conn:
            existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM subjects")).fetchall()
                existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass

            subj_cols = [
                ('internal_marks', 'INT NOT NULL DEFAULT 30'),
                ('external_marks', 'INT NOT NULL DEFAULT 70'),
                ('total_marks', 'INT NOT NULL DEFAULT 100'),
                ('component_config', 'TEXT NULL')
            ]
            for col_name, col_def in subj_cols:
                if col_name.lower() not in existing:
                    try:
                        conn.execute(db.text(f"ALTER TABLE subjects ADD COLUMN {col_name} {col_def}"))
                        conn.commit()
                        existing.add(col_name.lower())
                        report["migrated"].append(f"subjects.{col_name}")
                    except Exception as err:
                        report["errors"].append(f"subjects.{col_name}: {err}")
    except Exception as e:
        report["errors"].append(f"subjects_block: {e}")

    # 8. internal_marks table
    try:
        with db.engine.connect() as conn:
            existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM internal_marks")).fetchall()
                existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass

            needed_cols = [
                ('test1', 'FLOAT NULL'), ('test2', 'FLOAT NULL'), ('test3', 'FLOAT NULL'),
                ('internal_exam', 'FLOAT NULL'),
                ('active_learning', 'FLOAT NULL'), ('class_assignment', 'FLOAT NULL'), ('home_assignment', 'FLOAT NULL'),
                ('attendance', 'FLOAT NULL'), ('practical_eval', 'FLOAT NULL'), ('viva', 'FLOAT NULL'),
                ('journal', 'FLOAT NULL'), ('component_data', 'TEXT NULL')
            ]
            for col_name, col_def in needed_cols:
                if col_name.lower() not in existing:
                    try:
                        conn.execute(db.text(f"ALTER TABLE internal_marks ADD COLUMN {col_name} {col_def}"))
                        conn.commit()
                        existing.add(col_name.lower())
                        report["migrated"].append(f"internal_marks.{col_name}")
                    except Exception as err:
                        report["errors"].append(f"internal_marks.{col_name}: {err}")

            for q in ['quiz1', 'quiz2', 'quiz3', 'quiz4']:
                if q in existing:
                    try:
                        conn.execute(db.text(f"ALTER TABLE internal_marks DROP COLUMN {q}"))
                        conn.commit()
                    except Exception:
                        pass
    except Exception as e:
        report["errors"].append(f"internal_marks_block: {e}")

    # 9. Password reset OTP columns for students, faculty, admins
    for tbl_name in ['students', 'faculty', 'admins']:
        try:
            with db.engine.connect() as conn:
                existing = set()
                try:
                    res = conn.execute(db.text(f"SHOW COLUMNS FROM {tbl_name}")).fetchall()
                    existing = {str(r[0]).lower() for r in res}
                except Exception:
                    continue

                otp_cols = [
                    ('reset_otp', 'VARCHAR(255) NULL'),
                    ('otp_expiry', 'DATETIME NULL'),
                    ('otp_attempts', 'INT NOT NULL DEFAULT 0'),
                    ('otp_blocked_until', 'DATETIME NULL')
                ]
                for col_name, col_def in otp_cols:
                    if col_name.lower() not in existing:
                        try:
                            conn.execute(db.text(f"ALTER TABLE {tbl_name} ADD COLUMN {col_name} {col_def}"))
                            conn.commit()
                            existing.add(col_name.lower())
                            report["migrated"].append(f"{tbl_name}.{col_name}")
                        except Exception as err:
                            report["errors"].append(f"{tbl_name}.{col_name}: {err}")
        except Exception as e:
            report["errors"].append(f"otp_{tbl_name}: {e}")

    # 10. gallery_items views_count
    try:
        with db.engine.connect() as conn:
            existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM gallery_items")).fetchall()
                existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass
            if 'views_count' not in existing:
                try:
                    conn.execute(db.text("ALTER TABLE gallery_items ADD COLUMN views_count INT NOT NULL DEFAULT 0"))
                    conn.commit()
                    report["migrated"].append("gallery_items.views_count")
                except Exception as err:
                    report["errors"].append(f"gallery_items: {err}")
    except Exception as e:
        report["errors"].append(f"gallery_items_block: {e}")

    # 11. lecture_attendance_sessions
    try:
        with db.engine.connect() as conn:
            existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM lecture_attendance_sessions")).fetchall()
                existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass

            las_cols = [
                ('attendance_mode', "VARCHAR(20) DEFAULT 'Manual'"),
                ('qr_session_token', 'VARCHAR(255) NULL'),
                ('qr_session_expires_at', 'DATETIME NULL'),
                ('is_qr_active', 'TINYINT(1) DEFAULT 0'),
                ('session_type', "VARCHAR(20) DEFAULT 'Lecture'"),
                ('start_time', 'VARCHAR(10) NULL'),
                ('end_time', 'VARCHAR(10) NULL')
            ]
            for col_name, col_def in las_cols:
                if col_name.lower() not in existing:
                    try:
                        conn.execute(db.text(f"ALTER TABLE lecture_attendance_sessions ADD COLUMN {col_name} {col_def}"))
                        conn.commit()
                        existing.add(col_name.lower())
                        report["migrated"].append(f"lecture_attendance_sessions.{col_name}")
                    except Exception as err:
                        report["errors"].append(f"lecture_attendance_sessions.{col_name}: {err}")
    except Exception as e:
        report["errors"].append(f"lecture_attendance_sessions_block: {e}")

    # 12. lecture_attendance_students
    try:
        with db.engine.connect() as conn:
            existing = set()
            try:
                res = conn.execute(db.text("SHOW COLUMNS FROM lecture_attendance_students")).fetchall()
                existing = {str(r[0]).lower() for r in res}
            except Exception:
                pass

            lat_cols = [
                ('marked_method', "VARCHAR(30) DEFAULT 'MANUAL'"),
                ('scanned_at', 'DATETIME NULL'),
                ('device_fingerprint', 'VARCHAR(500) NULL'),
                ('scan_latitude', 'DECIMAL(10,8) NULL'),
                ('scan_longitude', 'DECIMAL(11,8) NULL'),
                ('distance_meters', 'FLOAT NULL'),
                ('is_verified', 'TINYINT(1) DEFAULT 1')
            ]
            for col_name, col_def in lat_cols:
                if col_name.lower() not in existing:
                    try:
                        conn.execute(db.text(f"ALTER TABLE lecture_attendance_students ADD COLUMN {col_name} {col_def}"))
                        conn.commit()
                        existing.add(col_name.lower())
                        report["migrated"].append(f"lecture_attendance_students.{col_name}")
                    except Exception as err:
                        report["errors"].append(f"lecture_attendance_students.{col_name}: {err}")
    except Exception as e:
        report["errors"].append(f"lecture_attendance_students_block: {e}")

    # 13. Default official public notices auto-seed
    try:
        from models import Notification
        pub_count = Notification.query.filter(
            Notification.target_audience.in_(['Guest', 'All']),
            Notification.is_active == True
        ).count()
        if pub_count < 2:
            seed_notices = [
                Notification(
                    title="Admissions Open for Academic Year 2026-27",
                    message="Applications are now open for BCA, B.Sc. IT, and Diploma programs for the academic year 2026-27. Prospective students can submit their online registration via the admissions portal.",
                    category="Academic",
                    target_audience="All",
                    target_semester=None,
                    target_division="All",
                    posted_by_role="Admin",
                    priority="Important",
                    is_active=True
                ),
                Notification(
                    title="Official Examination Guidelines & Schedule Published",
                    message="All semester students are hereby informed that the upcoming internal assessment and semester exam schedule has been released. Please check your respective course timetable.",
                    category="Exam",
                    target_audience="All",
                    target_semester=None,
                    target_division="All",
                    posted_by_role="Admin",
                    priority="Normal",
                    is_active=True
                ),
                Notification(
                    title="Smart Multimedia Classrooms & Campus Wi-Fi Operational",
                    message="CampusSync digital classrooms and campus-wide high-speed Wi-Fi infrastructure are now fully operational. Students and faculty may connect using their portal credentials.",
                    category="General",
                    target_audience="All",
                    target_semester=None,
                    target_division="All",
                    posted_by_role="Admin",
                    priority="Normal",
                    is_active=True
                )
            ]
            db.session.add_all(seed_notices)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        report["errors"].append(f"default_notices_seed: {e}")

    # 14. Reset student device fingerprints as requested by admin
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("UPDATE students SET device_fingerprint = NULL, device_model = NULL, device_bound_at = NULL, device_reset_allowed = 1 WHERE device_fingerprint IS NOT NULL"))
            conn.commit()
            report["migrated"].append("all_student_devices_reset")
    except Exception as e:
        report["errors"].append(f"reset_student_devices: {e}")

    return report


# Run schema migration during application startup
with app.app_context():
    try:
        migration_results = run_all_database_migrations()
        print(f"DATABASE MIGRATION SUMMARY: Migrated={len(migration_results['migrated'])}, Errors={len(migration_results['errors'])}")
    except Exception as e:
        print(f"Database migration top-level error: {e}")
        traceback.print_exc()

# Dedicated endpoint to trigger/verify database migrations anytime
@app.route('/system/migrate-db', methods=['GET', 'POST'])
def trigger_database_migration():
    """Manual or automated endpoint to run database migrations on Railway."""
    res = run_all_database_migrations()
    return {
        "status": "success",
        "migrated_count": len(res["migrated"]),
        "migrated_items": res["migrated"],
        "error_count": len(res["errors"]),
        "errors": res["errors"]
    }

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
    return send_from_directory(uploads_dir, filename)
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