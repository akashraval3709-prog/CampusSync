"""
CampusSync Database Migration Script
Adds QR Attendance, Device Fingerprinting, and Campus Timings/Geofence columns
to existing MySQL database without affecting other tables.
"""
import pymysql
import os
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_NAME = os.getenv('DB_NAME', 'campussync')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

print(f"Connecting to MySQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT}...")
conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cur = conn.cursor()

def add_column_if_not_exists(table, col, col_def):
    cur.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s;", (col,))
    row = cur.fetchone()
    if not row:
        print(f"  + Adding column `{col}` to `{table}`...")
        cur.execute(f"ALTER TABLE `{table}` ADD COLUMN `{col}` {col_def};")
    else:
        print(f"  * Column `{col}` already exists in `{table}`.")

# 1. college_settings
print("\n[1/5] Updating `college_settings` table...")
add_column_if_not_exists('college_settings', 'campus_latitude', 'decimal(10,8) DEFAULT 23.83680000')
add_column_if_not_exists('college_settings', 'campus_longitude', 'decimal(11,8) DEFAULT 72.11240000')
add_column_if_not_exists('college_settings', 'campus_radius_meters', 'int DEFAULT 150')
add_column_if_not_exists('college_settings', 'campus_plus_code', "varchar(100) DEFAULT '5C53+R58 Palanpur, Gujarat'")
add_column_if_not_exists('college_settings', 'college_start_time', "varchar(10) DEFAULT '10:00'")
add_column_if_not_exists('college_settings', 'college_end_time', "varchar(10) DEFAULT '17:00'")

# Set active college default coordinates & timings
cur.execute("""
UPDATE college_settings 
SET campus_latitude=24.15953750, campus_longitude=72.40295313, campus_radius_meters=800,
    campus_plus_code='5C53+R58 Palanpur, Gujarat', college_start_time='10:00', college_end_time='17:00'
WHERE id=1;
""")

# 2. students
print("\n[2/5] Updating `students` table...")
add_column_if_not_exists('students', 'device_fingerprint', 'varchar(500) DEFAULT NULL')
add_column_if_not_exists('students', 'device_model', 'varchar(100) DEFAULT NULL')
add_column_if_not_exists('students', 'device_bound_at', 'datetime DEFAULT NULL')
add_column_if_not_exists('students', 'device_reset_allowed', 'tinyint(1) DEFAULT 0')

# Update known student devices from dump
cur.execute("""
UPDATE students SET device_fingerprint='ATjSNRsq0IIRZPGnMgu2ye69kdlFmEzvwmsiftMVQse8gyMsNS8NQMs8lyRUp9siTXYg_usbK4eDlRoGgdN8AuE',
device_model='Android Phone', device_bound_at='2026-09-26 19:11:27' WHERE id=156 AND device_fingerprint IS NULL;
""")
cur.execute("""
UPDATE students SET device_bound_at='2026-09-26 03:49:57' WHERE id=200 AND device_bound_at IS NULL;
""")
cur.execute("""
UPDATE students SET device_bound_at='2026-09-26 03:47:54' WHERE id=201 AND device_bound_at IS NULL;
""")
cur.execute("""
UPDATE students SET device_bound_at='2026-09-26 05:05:26' WHERE id=203 AND device_bound_at IS NULL;
""")

# 3. lecture_attendance_sessions
print("\n[3/5] Updating `lecture_attendance_sessions` table...")
add_column_if_not_exists('lecture_attendance_sessions', 'attendance_mode', "enum('Manual','QR') DEFAULT 'Manual'")
add_column_if_not_exists('lecture_attendance_sessions', 'qr_session_token', 'varchar(255) DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_sessions', 'qr_session_expires_at', 'datetime DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_sessions', 'is_qr_active', 'tinyint(1) DEFAULT 0')
add_column_if_not_exists('lecture_attendance_sessions', 'session_type', "varchar(20) DEFAULT 'Lecture'")
add_column_if_not_exists('lecture_attendance_sessions', 'start_time', 'varchar(10) DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_sessions', 'end_time', 'varchar(10) DEFAULT NULL')
cur.execute("ALTER TABLE `lecture_attendance_sessions` MODIFY COLUMN `lecture_no` varchar(100) NOT NULL DEFAULT 'Lecture 1';")

# 4. lecture_attendance_students
print("\n[4/5] Updating `lecture_attendance_students` table...")
add_column_if_not_exists('lecture_attendance_students', 'marked_method', "varchar(30) DEFAULT 'MANUAL'")
add_column_if_not_exists('lecture_attendance_students', 'scanned_at', 'datetime DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_students', 'device_fingerprint', 'varchar(500) DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_students', 'scan_latitude', 'decimal(10,8) DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_students', 'scan_longitude', 'decimal(11,8) DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_students', 'distance_meters', 'float DEFAULT NULL')
add_column_if_not_exists('lecture_attendance_students', 'is_verified', 'tinyint(1) DEFAULT 1')

# 5. attendance_security_alerts
print("\n[5/5] Ensuring `attendance_security_alerts` table...")
cur.execute("""
CREATE TABLE IF NOT EXISTS `attendance_security_alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `student_id` int NOT NULL,
  `attempted_roll` varchar(20) DEFAULT NULL,
  `device_fingerprint` varchar(500) DEFAULT NULL,
  `conflicting_student_id` int DEFAULT NULL,
  `alert_type` enum('DUPLICATE_DEVICE','OUT_OF_GEOFENCE','EXPIRED_TOKEN','UNBOUND_DEVICE') NOT NULL,
  `alert_message` text,
  `scan_latitude` decimal(10,8) DEFAULT NULL,
  `scan_longitude` decimal(11,8) DEFAULT NULL,
  `distance_meters` float DEFAULT NULL,
  `faculty_action` enum('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
  `resolved_by_faculty_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session` (`session_id`),
  KEY `idx_student` (`student_id`),
  KEY `idx_alert_type` (`alert_type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
""")

conn.commit()
print("\nAll database migrations completed successfully!")
conn.close()
