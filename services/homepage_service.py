# services/homepage_service.py
import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from extensions import db
from models import HomePageSetting

ALLOWED_BANNER_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_banner_file(filename):
    """Checks if file extension is an allowed image format for homepage banner."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_BANNER_EXTENSIONS


def get_homepage_upload_folder():
    """Returns absolute path to uploads/homepage directory."""
    folder = os.path.join(current_app.root_path, 'uploads', 'homepage')
    os.makedirs(folder, exist_ok=True)
    return folder


import time

_cached_homepage_snapshot = None
_cached_homepage_time = 0
HOMEPAGE_CACHE_TTL = 120

class HomePageSettingSnapshot:
    """Thread-safe snapshot of HomePageSetting for sub-millisecond rendering."""
    def __init__(self, record):
        for col in record.__table__.columns:
            setattr(self, col.name, getattr(record, col.name))

def invalidate_homepage_cache():
    """Invalidates the in-memory homepage settings cache."""
    global _cached_homepage_snapshot, _cached_homepage_time
    _cached_homepage_snapshot = None
    _cached_homepage_time = 0

def get_homepage_settings(force_refresh=False):
    """Fetches the singleton HomePageSetting object with in-memory snapshot caching."""
    global _cached_homepage_snapshot, _cached_homepage_time
    now = time.time()
    if not force_refresh and _cached_homepage_snapshot is not None and (now - _cached_homepage_time < HOMEPAGE_CACHE_TTL):
        return _cached_homepage_snapshot

    record = HomePageSetting.get_settings()
    _cached_homepage_snapshot = HomePageSettingSnapshot(record)
    _cached_homepage_time = now
    return _cached_homepage_snapshot


def update_homepage_settings(form_data, file_obj=None):
    """
    Updates HomePageSetting fields from admin form submission.
    Handles optional hero banner image upload.
    Returns (success: bool, message: str)
    """
    settings = HomePageSetting.get_settings()

    try:
        # 1. Hero Section
        if 'hero_headline' in form_data and form_data['hero_headline'].strip():
            settings.hero_headline = form_data['hero_headline'].strip()

        if 'hero_subtitle' in form_data and form_data['hero_subtitle'].strip():
            settings.hero_subtitle = form_data['hero_subtitle'].strip()

        if 'hero_pill_badge' in form_data and form_data['hero_pill_badge'].strip():
            settings.hero_pill_badge = form_data['hero_pill_badge'].strip()

        if 'hero_cta1_text' in form_data and form_data['hero_cta1_text'].strip():
            settings.hero_cta1_text = form_data['hero_cta1_text'].strip()

        if 'hero_cta1_link' in form_data and form_data['hero_cta1_link'].strip():
            settings.hero_cta1_link = form_data['hero_cta1_link'].strip()

        if 'hero_cta2_text' in form_data and form_data['hero_cta2_text'].strip():
            settings.hero_cta2_text = form_data['hero_cta2_text'].strip()

        if 'hero_cta2_link' in form_data and form_data['hero_cta2_link'].strip():
            settings.hero_cta2_link = form_data['hero_cta2_link'].strip()

        # Handle Hero Banner Image Upload
        if file_obj and file_obj.filename:
            if not allowed_banner_file(file_obj.filename):
                return False, "Invalid image format for banner. Allowed: JPG, PNG, WEBP."

            original_name = secure_filename(file_obj.filename)
            ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
            new_filename = f"hero_banner_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.{ext}"

            upload_folder = get_homepage_upload_folder()
            destination = os.path.join(upload_folder, new_filename)
            file_obj.save(destination)

            # Safely remove previous custom image if exists
            if settings.hero_banner_image:
                old_path = os.path.join(upload_folder, settings.hero_banner_image)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass

            settings.hero_banner_image = new_filename

        # Remove banner image if requested
        if form_data.get('remove_banner_image') == '1':
            if settings.hero_banner_image:
                old_path = os.path.join(get_homepage_upload_folder(), settings.hero_banner_image)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass
                settings.hero_banner_image = None

        # 2. Campus Statistics Counters
        settings.stat1_number = form_data.get('stat1_number', '5,000+').strip()
        settings.stat1_label = form_data.get('stat1_label', 'Enrolled Students').strip()
        settings.stat1_active = bool(form_data.get('stat1_active'))

        settings.stat2_number = form_data.get('stat2_number', '150+').strip()
        settings.stat2_label = form_data.get('stat2_label', 'Faculty Members').strip()
        settings.stat2_active = bool(form_data.get('stat2_active'))

        settings.stat3_number = form_data.get('stat3_number', '99.8%').strip()
        settings.stat3_label = form_data.get('stat3_label', 'Attendance Accuracy').strip()
        settings.stat3_active = bool(form_data.get('stat3_active'))

        settings.stat4_number = form_data.get('stat4_number', '100%').strip()
        settings.stat4_label = form_data.get('stat4_label', 'Placement Assistance').strip()
        settings.stat4_active = bool(form_data.get('stat4_active'))

        # 3. News Ticker
        settings.ticker_active = bool(form_data.get('ticker_active'))
        settings.ticker_badge = form_data.get('ticker_badge', 'LATEST').strip()
        settings.ticker_text = form_data.get('ticker_text', '').strip()

        # 4. Feature Highlights
        settings.feat1_title = form_data.get('feat1_title', 'QR Attendance').strip()
        settings.feat1_desc = form_data.get('feat1_desc', '').strip()

        settings.feat2_title = form_data.get('feat2_title', 'Grade Entry').strip()
        settings.feat2_desc = form_data.get('feat2_desc', '').strip()

        settings.feat3_title = form_data.get('feat3_title', 'Web Management').strip()
        settings.feat3_desc = form_data.get('feat3_desc', '').strip()

        settings.feat4_title = form_data.get('feat4_title', 'Yearly Reports').strip()
        settings.feat4_desc = form_data.get('feat4_desc', '').strip()

        settings.updated_at = datetime.utcnow()
        db.session.commit()
        invalidate_homepage_cache()
        return True, "Home page content updated successfully!"

    except Exception as e:
        db.session.rollback()
        return False, f"Failed to save homepage settings: {str(e)}"
