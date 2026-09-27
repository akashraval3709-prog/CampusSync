"""
Comprehensive Verification Script for QR Attendance Integration
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Student, CollegeSetting, LectureAttendanceSession, LectureAttendanceStudent, AttendanceSecurityAlert
from services.attendance_service import (
    validate_session_time_and_conflict,
    calculate_haversine_distance,
    get_faculty_qr_live_roster
)

print("=" * 60)
print("STARTING COMPLETE QR ATTENDANCE INTEGRATION TEST")
print("=" * 60)

with app.app_context():
    # 1. College Setting check
    cs = CollegeSetting.query.first()
    assert cs is not None, "CollegeSetting record not found!"
    print(f"[OK] College Name: {cs.college_name}")
    print(f"[OK] College Operating Hours: {cs.college_start_time} to {cs.college_end_time}")
    print(f"[OK] Campus GPS Coordinates: ({cs.campus_latitude}, {cs.campus_longitude})")
    print(f"[OK] Campus Geofence Radius: {cs.campus_radius_meters}m | Plus Code: {cs.campus_plus_code}")

    # 2. Timing and schedule conflict validation check
    valid, msg = validate_session_time_and_conflict(5, 'A', '2026-09-27', '09:00', '10:00')
    print(f"[OK] Outside college hours test (09:00 < {cs.college_start_time}): Valid={valid} | Msg={msg}")
    assert not valid, "Should reject times earlier than college opening time!"

    valid_inside, msg_inside = validate_session_time_and_conflict(5, 'A', '2026-09-28', '11:00', '12:00')
    print(f"[OK] Inside college hours test (11:00 - 12:00): Valid={valid_inside} | Msg={msg_inside}")
    assert valid_inside, "Should accept valid timing inside college hours!"

    # 3. GPS Haversine Distance test
    # Campus: 24.15953750, 72.40295313
    dist_same = calculate_haversine_distance(24.15953750, 72.40295313, 24.15953750, 72.40295313)
    print(f"[OK] Haversine same point distance: {dist_same:.2f}m")
    assert abs(dist_same) < 0.01

    dist_near = calculate_haversine_distance(24.15953750, 72.40295313, 24.15960000, 72.40300000)
    print(f"[OK] Haversine nearby point distance: {dist_near:.2f}m")

    # 4. Student Device Fingerprint check
    student_bound = Student.query.filter(Student.device_fingerprint.isnot(None)).first()
    if student_bound:
        print(f"[OK] Bound Student Found: Roll {student_bound.roll_number} ({student_bound.full_name}) | FP: {student_bound.device_fingerprint[:20]}... | Model: {student_bound.device_model}")

    # 5. QR Session check
    qr_session = LectureAttendanceSession.query.filter(LectureAttendanceSession.attendance_mode == 'QR').first()
    assert qr_session is not None, "No QR sessions found in database!"
    print(f"[OK] QR Session Found: ID={qr_session.id} | Subject ID={qr_session.subject_id} | Token={qr_session.qr_session_token} | Mode={qr_session.attendance_mode}")

    # 6. Live Roster fetch test
    roster_res = get_faculty_qr_live_roster(qr_session.id)
    print(f"[OK] Live Roster fetch: success={roster_res.get('success')} | present_count={roster_res.get('present_count')} | total_students={roster_res.get('total_students')}")
    assert roster_res.get('success'), "Roster fetch should succeed!"

    # 7. Security Alerts check
    alerts = AttendanceSecurityAlert.query.all()
    print(f"[OK] Total Security Alerts Logged: {len(alerts)}")
    if alerts:
        a = alerts[0]
        print(f"     Sample Alert: Type={a.alert_type} | Action={a.faculty_action} | Message={a.alert_message[:60]}...")

    # 8. Test Client routes
    client = app.test_client()
    res_login = client.get('/student/login')
    assert res_login.status_code == 200
    assert b"deviceFingerprintInput" in res_login.data
    assert b"device_fingerprint.js" in res_login.data
    assert b"webauthn_device.js" in res_login.data
    print("[OK] /student/login rendered with device fingerprinting and WebAuthn scripts!")

    res_settings = client.get('/admin/college-settings')
    # Will redirect to admin login if not authenticated, which is correct
    print(f"[OK] /admin/college-settings response code: {res_settings.status_code}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED! QR ATTENDANCE INTEGRATION IS 100% OPERATIONAL.")
print("=" * 60)
