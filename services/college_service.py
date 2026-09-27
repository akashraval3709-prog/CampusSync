"""
CampusSync ERP - College Settings Service
=========================================
File: services/college_service.py

Provides functions to fetch and update college profile and information.
"""

from models import CollegeSetting
from extensions import db
import time

_cached_college_snapshot = None
_cached_college_time = 0
COLLEGE_CACHE_TTL = 120  # 2 minutes in-memory cache

class CollegeSettingSnapshot:
    """Thread-safe detached snapshot of CollegeSetting attributes for 0ms template rendering."""
    def __init__(self, record):
        for col in record.__table__.columns:
            setattr(self, col.name, getattr(record, col.name))

def invalidate_college_cache():
    """Invalidates the in-memory college settings snapshot cache."""
    global _cached_college_snapshot, _cached_college_time
    _cached_college_snapshot = None
    _cached_college_time = 0

def get_college_settings(force_refresh=False):
    """
    Get the single college settings record.
    Uses an in-memory snapshot cache to eliminate database round-trips on template rendering.
    """
    global _cached_college_snapshot, _cached_college_time
    now = time.time()
    if not force_refresh and _cached_college_snapshot is not None and (now - _cached_college_time < COLLEGE_CACHE_TTL):
        return _cached_college_snapshot

    college = CollegeSetting.query.first()
    
    # Create default record if database table is empty
    if not college:
        college = CollegeSetting(
            college_name="CampusSync College",
            college_short_name="CampusSync",
            college_type="BCA",
            logo="default-logo.png",
            address="College Campus Road",
            city="Palanpur",
            state="Gujarat",
            pincode="385001",
            phone="+91 00000 00000",
            email="info@college.edu",
            website="https://campussync.edu",
            principal_name="Dr. Principal",
            established_year="2020",
            description="Welcome to our college management system."
        )
        db.session.add(college)
        db.session.commit()
        
    _cached_college_snapshot = CollegeSettingSnapshot(college)
    _cached_college_time = now
    return _cached_college_snapshot

def update_college_settings(form_data, logo_filename=None, stamp_filename=None, signature_filename=None):
    """
    Update college settings details.
    Creates record if it does not exist, updates fields, saves to database,
    and invalidates the in-memory cache.
    """
    try:
        # Get existing record or create new one
        college = CollegeSetting.query.first()
        if not college:
            get_college_settings(force_refresh=True)
            college = CollegeSetting.query.first()

        # Update basic information
        college.college_name = form_data.get('college_name', '').strip() or college.college_name
        college.college_short_name = form_data.get('college_short_name', '').strip()
        college.college_type = form_data.get('college_type', '').strip()
        
        # Update logo, stamp, and signature filenames if new ones were uploaded
        if logo_filename:
            college.logo = logo_filename
        if stamp_filename:
            college.college_stamp = stamp_filename
        if signature_filename:
            college.principal_signature = signature_filename

        # Update contact details
        college.address = form_data.get('address', '').strip()
        college.city = form_data.get('city', '').strip()
        college.state = form_data.get('state', '').strip()
        college.pincode = form_data.get('pincode', '').strip()
        college.phone = form_data.get('phone', '').strip()
        college.email = form_data.get('email', '').strip()
        college.website = form_data.get('website', '').strip()

        # Update academic / institution details
        college.principal_name = form_data.get('principal_name', '').strip()
        college.established_year = form_data.get('established_year', '').strip()
        college.description = form_data.get('description', '').strip()

        # Update Campus GPS Geofence Settings
        college.campus_plus_code = form_data.get('campus_plus_code', '5C53+R58 Palanpur, Gujarat').strip()
        try:
            if form_data.get('campus_latitude'):
                college.campus_latitude = float(form_data.get('campus_latitude'))
        except (ValueError, TypeError):
            pass
        try:
            if form_data.get('campus_longitude'):
                college.campus_longitude = float(form_data.get('campus_longitude'))
        except (ValueError, TypeError):
            pass
        try:
            college.campus_radius_meters = int(form_data.get('campus_radius_meters', 500))
        except (ValueError, TypeError):
            college.campus_radius_meters = 500

        # Update attendance eligibility thresholds
        try:
            val = float(form_data.get('min_overall_attendance', 75.0))
            college.min_overall_attendance = max(1.0, min(100.0, val))
        except (ValueError, TypeError):
            college.min_overall_attendance = 75.0

        try:
            val = float(form_data.get('min_subject_attendance', 75.0))
            college.min_subject_attendance = max(1.0, min(100.0, val))
        except (ValueError, TypeError):
            college.min_subject_attendance = 75.0

        try:
            val = float(form_data.get('attendance_warning_threshold', 60.0))
            college.attendance_warning_threshold = max(1.0, min(100.0, val))
        except (ValueError, TypeError):
            college.attendance_warning_threshold = 60.0

        # Update College Operating Hours
        college.college_start_time = form_data.get('college_start_time', '10:00').strip() or '10:00'
        college.college_end_time = form_data.get('college_end_time', '17:00').strip() or '17:00'

        # Commit changes to database
        db.session.commit()
        invalidate_college_cache()
        return college, None
    except Exception as e:
        db.session.rollback()
        return None, f"Failed to save college settings: {str(e)}"
