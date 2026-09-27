# 📊 CampusSync - Attendance Module Summary Report

This summary report documents all database modifications, backend services, routes, and UI enhancements implemented for both **Faculty Attendance Register** and **Student Attendance Dashboard & QR Scanner System**.

---

## 1. 🎓 Student Attendance Dashboard & QR Scanner

### A. 🎯 Overall Attendance Circular Ring Gauge
- **SVG Circular Progress Gauge**: Displays the student's overall attendance percentage dynamically (e.g. `84.5%`).
- **University Threshold Color Indicators**:
  - 🟢 **Safe / Eligible (>= 75%)**: Meets HNGU University eligibility criteria.
  - 🟡 **Warning (60% - 74%)**: Caution alert for low attendance.
  - 🔴 **Shortage Alert (< 60%)**: Critical shortage alert.
- **Summary Badges**: Total Conducted Lectures, Attended Lectures, and Missed Lectures.

### B. 📘 Subject-Wise Breakdown Cards
- Displays every enrolled subject for the student's current semester.
- Shows total lectures held, lectures attended, progress bar, attendance percentage, and converted **HNGU Internal Assessment Score (/5.0 Marks)**.

### C. 📜 Daily Lecture History Table
- Displays recent 15 lecture attendance logs with Date, Session/Lecture No, Subject, Faculty Name, and Status (**Present (P)** in Green / **Absent (A)** in Red).

### D. 📱 QR Code Attendance Scanning (`/student/scan`)
- Allows students to scan or simulate scanning active faculty QR codes.
- Automatically records student status as **Present (P)** in real-time in the database and updates attendance percentage.

---

## 2. 👨‍🏫 Faculty Attendance Register System

- **Save as Draft vs Final Submit Locking**:
  - **Save as Draft**: Saves session data in `Draft` state so faculty can reload and edit attendance for any student.
  - **Final Submit**: Sets session status to `Submitted`, locks all radio controls & buttons on frontend/backend, and updates student cumulative totals in `attendance_records`.
- **Dynamic Semester Cycle (Odd / Even) Filter**:
  - Automatically filters assigned subjects dropdown according to `AcademicSetting.semester_cycle` (**Odd**: Sem 1, 3, 5 / **Even**: Sem 2, 4, 6).

---

## 3. 🗄️ Database Schema Summary

- `lecture_attendance_sessions`: `(id, faculty_id, subject_id, semester, division, academic_year, lecture_date, lecture_no, status['Draft'/'Submitted'])`
- `lecture_attendance_students`: `(id, session_id, student_id, status['Present'/'Absent'])`
- `attendance_records`: Cumulative summaries updated automatically upon Final Submit & QR scan.
