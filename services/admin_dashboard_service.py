"""
CampusSync ERP - Admin Dashboard Service
========================================
File: services/admin_dashboard_service.py
Provides real-time aggregated metrics and distributions for the Admin Dashboard.
"""

from models import (
    db,
    Student,
    Faculty,
    Subject,
    AttendanceRecord,
    LectureAttendanceSession,
    LectureAttendanceStudent,
    ResultDeclaration,
    EmailLog
)
from services.college_service import get_college_settings
from sqlalchemy import func


def get_admin_dashboard_data():
    """
    Computes and aggregates dynamic real-time metrics for the Admin Dashboard.
    Returns:
        dict: Real database counts, attendance statistics, semester distributions,
              recent student admissions, and lecture sessions.
    """
    college = get_college_settings()
    current_ay = getattr(college, 'current_academic_year', '2026-27') or '2026-27'

    from services.academic_service import get_academic_settings, get_active_semesters
    academic = get_academic_settings()
    cycle = academic.semester_cycle if academic else 'Odd'
    active_semesters = get_active_semesters(cycle)

    # 1. Primary Metrics (scoped to active cycle)
    total_students = Student.query.filter(Student.status == 'Active', Student.semester.in_(active_semesters)).count()
    total_faculty = Faculty.query.filter_by(status='Active').count()
    total_subjects = Subject.query.filter(Subject.status == 'Active', Subject.semester.in_(active_semesters)).count()
    total_sessions = LectureAttendanceSession.query.filter(LectureAttendanceSession.semester.in_(active_semesters)).count()

    # 2. Campus-Wide Average Attendance Percentage (High-speed single SQL aggregate)
    att_stats = db.session.query(
        func.coalesce(func.sum(AttendanceRecord.total_lectures), 0),
        func.coalesce(func.sum(AttendanceRecord.attended_lectures), 0)
    ).join(Student).filter(
        Student.status == 'Active',
        Student.semester.in_(active_semesters),
        AttendanceRecord.total_lectures > 0
    ).first()

    tot_conducted = att_stats[0] if att_stats else 0
    tot_attended = att_stats[1] if att_stats else 0
    avg_attendance = round((float(tot_attended) / float(tot_conducted)) * 100.0, 1) if tot_conducted > 0 else 0.0

    # 3. Semester-Wise Student Distribution (Active cycle semesters only)
    sem_counts_raw = dict(
        db.session.query(Student.semester, func.count(Student.id))
        .filter(Student.status == 'Active', Student.semester.in_(active_semesters))
        .group_by(Student.semester)
        .all()
    )
    semester_distribution = []
    for sem in active_semesters:
        cnt = sem_counts_raw.get(sem, 0)
        pct = round((cnt / float(total_students)) * 100.0, 1) if total_students > 0 else 0.0
        semester_distribution.append({
            "semester": sem,
            "count": cnt,
            "percentage": pct
        })

    # 4. Recent Student Registrations (Latest 5 active cycle students)
    recent_students = Student.query.filter(Student.status == 'Active', Student.semester.in_(active_semesters)).order_by(Student.id.desc()).limit(5).all()

    # 5. Recent Lecture Attendance Sessions (Batch-eager loaded in 2 queries instead of 20)
    from sqlalchemy.orm import joinedload
    recent_sessions_raw = (
        LectureAttendanceSession.query
        .options(
            joinedload(LectureAttendanceSession.subject),
            joinedload(LectureAttendanceSession.faculty)
        )
        .filter(LectureAttendanceSession.semester.in_(active_semesters))
        .order_by(LectureAttendanceSession.lecture_date.desc(), LectureAttendanceSession.id.desc())
        .limit(5)
        .all()
    )

    session_ids = [s.id for s in recent_sessions_raw]
    counts_map = {}
    if session_ids:
        rows = db.session.query(
            LectureAttendanceStudent.session_id,
            LectureAttendanceStudent.status,
            func.count(LectureAttendanceStudent.id)
        ).filter(
            LectureAttendanceStudent.session_id.in_(session_ids)
        ).group_by(
            LectureAttendanceStudent.session_id,
            LectureAttendanceStudent.status
        ).all()
        for sid, st, cnt in rows:
            if sid not in counts_map:
                counts_map[sid] = {"present": 0, "total": 0}
            counts_map[sid]["total"] += cnt
            if st == 'Present':
                counts_map[sid]["present"] += cnt

    recent_sessions = []
    for sess in recent_sessions_raw:
        c_info = counts_map.get(sess.id, {"present": 0, "total": 0})
        recent_sessions.append({
            "id": sess.id,
            "date": sess.lecture_date.strftime('%d-%m-%Y') if sess.lecture_date else "—",
            "lecture_no": sess.lecture_no or "Lecture",
            "subject_code": sess.subject.subject_code if sess.subject else "—",
            "subject_name": sess.subject.subject_name if sess.subject else "General",
            "faculty_name": sess.faculty.full_name if sess.faculty else "Faculty",
            "semester": sess.semester,
            "division": sess.division,
            "present_count": c_info["present"],
            "total_count": c_info["total"]
        })

    # 6. Result Declaration Status
    declared_count = ResultDeclaration.query.filter_by(academic_year=current_ay, is_declared=True).count()

    # 7. Total Email Logs
    total_emails = EmailLog.query.count()

    # 8. Minimum attendance threshold from college settings
    min_overall = float(college.min_overall_attendance) if (college and getattr(college, 'min_overall_attendance', None) is not None) else 75.0

    return {
        "college": college,
        "current_ay": current_ay,
        "semester_cycle": cycle,
        "active_semesters": active_semesters,
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_subjects": total_subjects,
        "total_sessions": total_sessions,
        "avg_attendance": avg_attendance,
        "min_overall_threshold": min_overall,
        "semester_distribution": semester_distribution,
        "recent_students": recent_students,
        "recent_sessions": recent_sessions,
        "declared_count": declared_count,
        "total_emails": total_emails
    }
