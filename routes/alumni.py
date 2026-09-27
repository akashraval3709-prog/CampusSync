"""
CampusSync ERP - Alumni / Old Student Routes
============================================
File: routes/alumni.py

Handles public alumni result verification flow:
1. Search by Enrollment Number or Registered Email ID
2. Dispatch 6-digit hashed OTP to student's email
3. OTP verification with session authorization
4. Display complete semester results and internal marks
5. PDF Marksheet downloads (Single Semester & Consolidated All Semesters)
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from services.alumni_service import (
    find_old_student,
    generate_and_send_alumni_otp,
    verify_alumni_otp,
    get_archived_student_results,
    generate_archived_student_semester_pdf,
    generate_archived_student_consolidated_pdf
)

alumni_bp = Blueprint('alumni', __name__)


@alumni_bp.route('/alumni/results', methods=['GET'], endpoint='alumni_results')
@alumni_bp.route('/old-student/results', methods=['GET'])
def alumni_results():
    """
    Renders the public lookup page for graduated / old students.
    If already verified in current session, redirects directly to result dashboard.
    """
    if "alumni_verified_enrollment" in session:
        return redirect(url_for('alumni.alumni_dashboard'))

    return render_template('alumni/search.html')


@alumni_bp.route('/alumni/request-otp', methods=['POST'], endpoint='alumni_request_otp')
def alumni_request_otp():
    """
    Processes student identification (Enrollment No or Registered Email),
    generates a secure 6-digit OTP, hashes it in DB, and dispatches via email.
    """
    identifier = request.form.get('identifier', '').strip()
    if not identifier:
        flash("Please enter your Enrollment Number or Registered Email Address.", "danger")
        return redirect(url_for('alumni.alumni_results'))

    student = find_old_student(identifier)
    if not student:
        flash("No graduated or archived student record was found matching the provided details. Please verify your enrollment number / email or contact college administration.", "danger")
        return redirect(url_for('alumni.alumni_results'))

    # Generate and send OTP
    success, masked_email, err_msg = generate_and_send_alumni_otp(student)
    if not success:
        flash(f"Could not send OTP: {err_msg}", "danger")
        return redirect(url_for('alumni.alumni_results'))

    # Store pending verification state in session
    session['alumni_pending_enrollment'] = student.enrollment_no
    session['alumni_masked_email'] = masked_email

    flash(f"A 6-digit verification OTP has been sent to your registered email ({masked_email}). Please check your inbox.", "success")
    return redirect(url_for('alumni.alumni_verify_otp'))


@alumni_bp.route('/alumni/verify-otp', methods=['GET', 'POST'], endpoint='alumni_verify_otp')
def alumni_verify_otp():
    """
    Renders OTP verification form (GET) and validates submitted OTP (POST).
    """
    pending_enrollment = session.get('alumni_pending_enrollment')
    if not pending_enrollment:
        flash("Session expired or invalid. Please search for your record again.", "warning")
        return redirect(url_for('alumni.alumni_results'))

    masked_email = session.get('alumni_masked_email', 'registered email')

    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        if not otp:
            flash("Please enter the 6-digit OTP received on your email.", "danger")
            return render_template('alumni/verify_otp.html', masked_email=masked_email)

        # Verify against active hashed OTP in database
        is_valid, err_msg = verify_alumni_otp(pending_enrollment, otp)
        if not is_valid:
            flash(err_msg or "Invalid OTP. Please try again.", "danger")
            return render_template('alumni/verify_otp.html', masked_email=masked_email)

        # Authorized session established
        session.pop('alumni_pending_enrollment', None)
        session.pop('alumni_masked_email', None)
        session['alumni_verified_enrollment'] = pending_enrollment

        flash("Identity verified successfully! Welcome to your Academic Results Portal.", "success")
        return redirect(url_for('alumni.alumni_dashboard'))

    return render_template('alumni/verify_otp.html', masked_email=masked_email)


@alumni_bp.route('/alumni/resend-otp', methods=['POST'], endpoint='alumni_resend_otp')
def alumni_resend_otp():
    """
    Resends fresh OTP to the pending student's email.
    """
    pending_enrollment = session.get('alumni_pending_enrollment')
    if not pending_enrollment:
        flash("Verification session expired. Please start again.", "warning")
        return redirect(url_for('alumni.alumni_results'))

    student = find_old_student(pending_enrollment)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for('alumni.alumni_results'))

    success, masked_email, err_msg = generate_and_send_alumni_otp(student)
    if not success:
        flash(f"Could not resend OTP: {err_msg}", "danger")
    else:
        flash(f"A fresh OTP has been sent to {masked_email}.", "info")

    return redirect(url_for('alumni.alumni_verify_otp'))


@alumni_bp.route('/alumni/dashboard', endpoint='alumni_dashboard')
def alumni_dashboard():
    """
    Protected results dashboard for authenticated alumni/old students.
    Shows semester-wise marks, subjects, percentages, and overall graduation summary.
    """
    verified_enrollment = session.get('alumni_verified_enrollment')
    if not verified_enrollment:
        flash("Please authenticate with your OTP to access historical results.", "info")
        return redirect(url_for('alumni.alumni_results'))

    student_dict, semesters_data, consolidated_summary = get_archived_student_results(verified_enrollment)
    if not student_dict:
        session.pop('alumni_verified_enrollment', None)
        flash("No academic record found for this account.", "danger")
        return redirect(url_for('alumni.alumni_results'))

    return render_template(
        'alumni/results.html',
        student=student_dict,
        semesters=semesters_data,
        summary=consolidated_summary
    )


@alumni_bp.route('/alumni/download-pdf', endpoint='alumni_download_semester_pdf')
def alumni_download_semester_pdf():
    """
    Downloads official single-semester PDF marksheet for the verified alumni.
    """
    verified_enrollment = session.get('alumni_verified_enrollment')
    if not verified_enrollment:
        return redirect(url_for('alumni.alumni_results'))

    semester = request.args.get('semester', type=int)
    if not semester:
        flash("Invalid semester parameter.", "danger")
        return redirect(url_for('alumni.alumni_dashboard'))

    try:
        pdf_buffer = generate_archived_student_semester_pdf(verified_enrollment, semester)
        filename = f"Marksheet_Sem_{semester}_{verified_enrollment}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        flash(f"Failed to generate marksheet PDF: {str(e)}", "danger")
        return redirect(url_for('alumni.alumni_dashboard'))


@alumni_bp.route('/alumni/download-consolidated-pdf', endpoint='alumni_download_consolidated_pdf')
def alumni_download_consolidated_pdf():
    """
    Downloads official Consolidated All-Semesters PDF marksheet for the verified alumni.
    """
    verified_enrollment = session.get('alumni_verified_enrollment')
    if not verified_enrollment:
        return redirect(url_for('alumni.alumni_results'))

    try:
        pdf_buffer = generate_archived_student_consolidated_pdf(verified_enrollment)
        filename = f"Consolidated_Marksheet_{verified_enrollment}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        flash(f"Failed to generate consolidated PDF: {str(e)}", "danger")
        return redirect(url_for('alumni.alumni_dashboard'))


@alumni_bp.route('/alumni/logout', endpoint='alumni_logout')
def alumni_logout():
    """
    Clears verified alumni session and returns to homepage.
    """
    session.pop('alumni_verified_enrollment', None)
    session.pop('alumni_pending_enrollment', None)
    session.pop('alumni_masked_email', None)
    flash("You have successfully signed out of the Alumni Results Portal.", "info")
    return redirect(url_for('home'))
