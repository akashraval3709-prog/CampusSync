"""
Script to import QR sessions, scan entries, and security alerts from SQL dump into current database.
Uses INSERT IGNORE / ON DUPLICATE KEY UPDATE so existing records are preserved.
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_NAME = os.getenv('DB_NAME', 'campussync')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cur = conn.cursor()

# 1. Insert QR Sessions from dump
sessions = [
    (25, 6, 1, 2, 'A', '2026-27', '2026-09-25', 'Lecture 1', 'Draft', '2026-09-25 08:31:56', '2026-09-25 09:02:50', 'QR', 'CS-BCA101-A-535A1E', '2026-09-25 14:44:50', 0, 'Lecture', None, None),
    (26, 11, 6, 5, 'A', '2026-27', '2026-09-25', 'Lecture 1', 'Draft', '2026-09-25 08:50:09', '2026-09-25 12:48:12', 'QR', 'CS-BCA501-A-27C3A0', '2026-09-25 18:26:07', 0, 'Lecture', None, None),
    (27, 11, 5, 5, 'A', '2026-27', '2026-09-25', 'Lecture 2', 'Draft', '2026-09-25 12:18:42', '2026-09-25 12:47:41', 'QR', 'CS-BCA501A-A-8F3426', '2026-09-25 18:02:42', 0, 'Lecture', None, None),
    (28, 1, 5, 5, 'A', '2026-27', '2026-09-26', 'Lecture 1', 'Draft', '2026-09-25 20:58:58', '2026-09-26 13:35:19', 'QR', 'CS-BCA501A-A-1A5891', '2026-09-26 22:05:19', 1, 'Lecture', None, None),
    (29, 11, 6, 5, 'A', '2026-27', '2026-09-26', 'Lecture 1', 'Submitted', '2026-09-25 21:45:25', '2026-09-25 23:41:56', 'QR', 'CS-BCA501-A-253D3A', '2026-09-26 05:21:33', 0, 'Lecture', None, None),
    (30, 11, 5, 5, 'A', '2026-27', '2026-09-26', 'Lecture 2', 'Draft', '2026-09-25 23:26:11', '2026-09-25 23:43:05', 'QR', 'CS-BCA501A-A-3E0E30', '2026-09-26 05:22:09', 0, 'Lecture', None, None),
    (31, 11, 6, 5, 'A', '2026-27', '2026-09-27', 'Lecture 1', 'Submitted', '2026-09-26 13:01:20', '2026-09-26 13:40:12', 'QR', 'CS-BCA501-A-1A1C78', '2026-09-26 19:17:57', 0, 'Lecture', None, None),
    (32, 11, 5, 5, 'A', '2026-27', '2026-09-27', 'Lecture 2', 'Submitted', '2026-09-26 13:40:49', '2026-09-26 14:07:33', 'QR', 'CS-BCA501A-A-033BE4', '2026-09-26 19:45:44', 0, 'Lecture', None, None),
    (34, 11, 6, 5, 'A', '2026-27', '2026-09-27', 'Lecture (11:00 - 12:00)', 'Draft', '2026-09-26 15:33:45', '2026-09-26 15:33:57', 'QR', 'CS-BCA501-A-4D98A4', '2026-09-26 21:13:45', 0, 'Lecture', '11:00', '12:00')
]

for s in sessions:
    cur.execute("""
    INSERT INTO lecture_attendance_sessions 
    (id, faculty_id, subject_id, semester, division, academic_year, lecture_date, lecture_no, status, created_at, updated_at, attendance_mode, qr_session_token, qr_session_expires_at, is_qr_active, session_type, start_time, end_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
      attendance_mode=VALUES(attendance_mode),
      qr_session_token=VALUES(qr_session_token),
      qr_session_expires_at=VALUES(qr_session_expires_at),
      is_qr_active=VALUES(is_qr_active),
      session_type=VALUES(session_type),
      start_time=VALUES(start_time),
      end_time=VALUES(end_time);
    """, s)

# 2. Insert QR student attendance rows
students_att = [
    (59, 25, 127, 'Present', '2026-09-25 08:31:56', '2026-09-25 08:31:56', 'QR', '2026-09-25 14:01:56', 'DEV-TEST-PHONE-1', 24.15960000, 72.40300000, 8.42081, 1),
    (60, 26, 156, 'Present', '2026-09-25 09:43:57', '2026-09-25 11:09:13', 'QR', '2026-09-25 16:39:13', 'DEV-VM9L63RN-MUH6QKXB', None, None, 0, 1),
    (61, 26, 200, 'Present', '2026-09-25 09:43:57', '2026-09-25 12:12:34', 'QR', '2026-09-25 17:42:34', 'DEV-CHIRAG-OWN-PHONE-999', 24.16216216, 72.39668186, 699.99, 1),
    (62, 26, 201, 'Present', '2026-09-25 09:43:57', '2026-09-25 11:25:19', 'QR', '2026-09-25 16:55:19', 'DEV-HETVI-TEST-PHONE', 24.16216216, 72.39668186, 699.99, 1),
    (63, 26, 202, 'Absent', '2026-09-25 09:43:57', '2026-09-25 09:43:57', 'Manual', None, None, None, None, None, 1),
    (64, 26, 203, 'Absent', '2026-09-25 09:43:57', '2026-09-25 09:43:57', 'Manual', None, None, None, None, None, 1),
    (65, 26, 204, 'Absent', '2026-09-25 09:43:57', '2026-09-25 09:43:57', 'Manual', None, None, None, None, None, 1),
    (66, 27, 156, 'Present', '2026-09-25 12:19:29', '2026-09-25 12:19:29', 'QR', '2026-09-25 17:49:29', 'DEV-VM9L63RN-MUH6QKXB', 24.16216216, 72.39668186, 699.99, 1),
    (67, 27, 200, 'Present', '2026-09-25 12:22:46', '2026-09-25 12:22:46', 'QR', '2026-09-25 17:52:46', 'DEV-VM9L63RN-MUH6QKXB', None, None, None, 1),
    (70, 29, 201, 'Absent', '2026-09-25 21:46:03', '2026-09-25 21:46:03', 'REJECTED_PROXY', None, None, None, None, None, 0),
    (71, 29, 200, 'Present', '2026-09-25 21:46:37', '2026-09-25 21:46:37', 'QR', '2026-09-26 03:16:37', 'DEV-URARHCM9-MUHA8SVC', 24.15956670, 72.40287750, 8.33176, 1),
    (72, 29, 156, 'Present', '2026-09-25 21:49:00', '2026-09-25 21:49:00', 'QR', '2026-09-26 03:19:00', 'DEV-U7CYYMC7-MUHQK77Z', 24.15956250, 72.40291520, 4.74724, 1),
    (73, 29, 202, 'Present', '2026-09-25 21:52:12', '2026-09-25 21:52:12', 'QR', '2026-09-26 03:22:12', 'DEV-0FIZNV46-MUHTOV6F', 24.15956350, 72.40291920, 4.49536, 1),
    (74, 29, 203, 'Absent', '2026-09-25 23:41:45', '2026-09-25 23:41:45', 'Manual', None, None, None, None, None, 1),
    (75, 29, 204, 'Absent', '2026-09-25 23:41:45', '2026-09-25 23:41:45', 'Manual', None, None, None, None, None, 1),
    (88, 32, 156, 'Present', '2026-09-26 13:41:27', '2026-09-26 13:41:27', 'QR', '2026-09-26 19:11:27', 'ATjSNRsq0IIRZPGnMgu2ye69kdlFmEzvwmsiftMVQse8gyMsNS8NQMs8lyRUp9siTXYg_usbK4eDlRoGgdN8AuE', 24.15959550, 72.40263260, 33.1528, 1)
]

for sa in students_att:
    cur.execute("""
    INSERT INTO lecture_attendance_students
    (id, session_id, student_id, status, created_at, updated_at, marked_method, scanned_at, device_fingerprint, scan_latitude, scan_longitude, distance_meters, is_verified)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      status=VALUES(status),
      marked_method=VALUES(marked_method),
      scanned_at=VALUES(scanned_at),
      device_fingerprint=VALUES(device_fingerprint),
      scan_latitude=VALUES(scan_latitude),
      scan_longitude=VALUES(scan_longitude),
      distance_meters=VALUES(distance_meters),
      is_verified=VALUES(is_verified);
    """, sa)

# 3. Insert Attendance Security Alerts
alerts = [
    (1, 25, 127, '1', 'DEV-TEST-PHONE-1', None, 'OUT_OF_GEOFENCE', 'Student scanned from 127593m away (Allowed: 500m).', 23.02250000, 72.57140000, 127593, 'APPROVED', 6, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
    (13, 30, 203, '4', 'HW-7AD44D3B-BDB2739B', None, 'UNBOUND_DEVICE', 'Attempted scan from unrecognized device #HW-7AD44 (Registered device: #HW-0B4FB).', None, None, None, 'PENDING', None, '2026-09-25 23:42:13', '2026-09-25 23:42:13'),
    (3, 26, 201, '2', 'DEV-VM9L63RN-MUH6QKXB', None, 'OUT_OF_GEOFENCE', 'Student scanned from 700m away (Allowed: 500m).', 24.16216216, 72.39668186, 699.99, 'REJECTED', 11, '2026-09-25 11:12:52', '2026-09-25 11:27:46'),
    (5, 26, 200, '1', 'DEV-VM9L63RN-MUH6QKXB', 156, 'DUPLICATE_DEVICE', 'Device hash was already used by Roll 6 (Sachin Rathod). Potential proxy scan attempt.', None, None, None, 'APPROVED', 11, '2026-09-25 11:37:55', '2026-09-25 12:46:40'),
    (14, 31, 156, '6', 'HW-7D85DE6D-59D78201', None, 'UNBOUND_DEVICE', 'Attempted scan from unrecognized device #HW-7D85D (Registered device: #HW-81774).', None, None, None, 'REJECTED', 11, '2026-09-26 13:03:34', '2026-09-26 13:04:46'),
    (12, 29, 201, '2', 'DEV-URARHCM9-MUHA8SVC', 200, 'DUPLICATE_DEVICE', 'Device hash belongs to Roll 1 (Chirag Panchal). Potential proxy scan attempt.', 24.15951470, 72.40291590, None, 'REJECTED', 11, '2026-09-25 21:45:38', '2026-09-25 21:46:03')
]

for a in alerts:
    cur.execute("""
    INSERT INTO attendance_security_alerts
    (id, session_id, student_id, attempted_roll, device_fingerprint, conflicting_student_id, alert_type, alert_message, scan_latitude, scan_longitude, distance_meters, faculty_action, resolved_by_faculty_id, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      alert_message=VALUES(alert_message),
      faculty_action=VALUES(faculty_action),
      resolved_by_faculty_id=VALUES(resolved_by_faculty_id);
    """, a)

conn.commit()
print("QR data imported successfully!")
conn.close()
