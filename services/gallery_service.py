# services/gallery_service.py
import os
import uuid
import ssl
import urllib.request
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from extensions import db
from models import GalleryItem

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'}
GALLERY_CATEGORIES = [
    'Campus Life',
    'Events & Fests',
    'Sports',
    'Academic & Seminars',
    'Achievements',
    'Celebrations'
]

# Curated high-resolution seeds (3 items per section, Celebrations keeps David & akash raval + adds 1)
CURATED_GALLERY_SEEDS = [
    # 1. Campus Life (3 items)
    {
        "title": "Modern Central Library & Study Wing",
        "category": "Campus Life",
        "description": "Quiet air-conditioned digital library with thousands of reference books, e-journals, and peaceful study pods.",
        "url": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_campus_life_1.jpg",
        "is_featured": True,
        "views_count": 84,
        "grad_from": "#1e3a8a",
        "grad_to": "#0f172a"
    },
    {
        "title": "Green Smart Campus Walkway & Gardens",
        "category": "Campus Life",
        "description": "Eco-friendly landscaped gardens, tree-lined walking tracks, and open-air seating for students between lectures.",
        "url": "https://images.unsplash.com/photo-1562774053-701939374585?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_campus_life_2.jpg",
        "is_featured": False,
        "views_count": 52,
        "grad_from": "#065f46",
        "grad_to": "#022c22"
    },
    {
        "title": "Advanced Computer & AI Research Lab",
        "category": "Campus Life",
        "description": "High-performance computing systems, dual-monitor programming workstations, and high-speed campus WiFi network.",
        "url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_campus_life_3.jpg",
        "is_featured": False,
        "views_count": 67,
        "grad_from": "#0f766e",
        "grad_to": "#134e4a"
    },

    # 2. Events & Fests (3 items)
    {
        "title": "Annual Cultural Fest & Live Concert",
        "category": "Events & Fests",
        "description": "High-energy musical concert night featuring celebrity artists, laser show lights, and enthusiastic crowd.",
        "url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_events_fests_1.jpg",
        "is_featured": True,
        "views_count": 142,
        "grad_from": "#6d28d9",
        "grad_to": "#31104b"
    },
    {
        "title": "Campus Youth Hackathon 2026",
        "category": "Events & Fests",
        "description": "24-hour inter-college coding marathon where teams built innovative web, mobile, and AI solutions overnight.",
        "url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_events_fests_2.jpg",
        "is_featured": False,
        "views_count": 96,
        "grad_from": "#1d4ed8",
        "grad_to": "#172554"
    },
    {
        "title": "TechFusion Robotics & Project Expo",
        "category": "Events & Fests",
        "description": "Annual state-level technical exhibition showcasing student-built robotics, IoT automation, and drone demonstrations.",
        "url": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_events_fests_3.jpg",
        "is_featured": False,
        "views_count": 78,
        "grad_from": "#b45309",
        "grad_to": "#451a03"
    },

    # 3. Sports (3 items)
    {
        "title": "Inter-College Cricket Tournament",
        "category": "Sports",
        "description": "Thrilling championship cricket match under lights at the university sports complex with loud student cheers.",
        "url": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_sports_1.jpg",
        "is_featured": True,
        "views_count": 115,
        "grad_from": "#15803d",
        "grad_to": "#052e16"
    },
    {
        "title": "Annual Football Championship Finals",
        "category": "Sports",
        "description": "Exciting final clash of the inter-department football tournament on the main green athletic turf.",
        "url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_sports_2.jpg",
        "is_featured": False,
        "views_count": 89,
        "grad_from": "#047857",
        "grad_to": "#064e3b"
    },
    {
        "title": "Campus Basketball League & Athletics Meet",
        "category": "Sports",
        "description": "High-paced basketball finals and track races showcasing outstanding student athleticism and team spirit.",
        "url": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_sports_3.jpg",
        "is_featured": False,
        "views_count": 64,
        "grad_from": "#c2410c",
        "grad_to": "#431407"
    },

    # 4. Academic & Seminars (3 items)
    {
        "title": "International Seminar on AI & Machine Learning",
        "category": "Academic & Seminars",
        "description": "Keynote address by leading global industry experts on generative AI trends in the campus auditorium.",
        "url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_academic_1.jpg",
        "is_featured": True,
        "views_count": 103,
        "grad_from": "#4338ca",
        "grad_to": "#1e1b4b"
    },
    {
        "title": "Interactive Faculty Workshop & Hands-on Coding",
        "category": "Academic & Seminars",
        "description": "Intensive skill-building workshop where students collaborated closely with mentors on cloud architecture.",
        "url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_academic_2.jpg",
        "is_featured": False,
        "views_count": 71,
        "grad_from": "#2563eb",
        "grad_to": "#1e3a8a"
    },
    {
        "title": "Science Innovation & Research Symposium",
        "category": "Academic & Seminars",
        "description": "Young researchers and undergraduate students demonstrating working hardware models and research papers.",
        "url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_academic_3.jpg",
        "is_featured": False,
        "views_count": 59,
        "grad_from": "#0e7490",
        "grad_to": "#164e63"
    },

    # 5. Achievements (3 items)
    {
        "title": "Annual Convocation Ceremony & Graduation",
        "category": "Achievements",
        "description": "Proud moment as the graduating batch tosses convocation caps in celebration of their academic success.",
        "url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_achievements_1.jpg",
        "is_featured": True,
        "views_count": 168,
        "grad_from": "#b45309",
        "grad_to": "#451a03"
    },
    {
        "title": "State Championship Trophy Award",
        "category": "Achievements",
        "description": "Campus team proudly lifting the overall championship trophy at the state inter-university athletic meet.",
        "url": "https://images.unsplash.com/photo-1578269174936-2709b6aeb913?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_achievements_2.jpg",
        "is_featured": False,
        "views_count": 112,
        "grad_from": "#ca8a04",
        "grad_to": "#422006"
    },
    {
        "title": "National Hackathon Gold Medalist Felicitation",
        "category": "Achievements",
        "description": "College felicitation ceremony honoring the 1st prize winners of the Smart India Hackathon with cash prize and medals.",
        "url": "https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_achievements_3.jpg",
        "is_featured": False,
        "views_count": 94,
        "grad_from": "#059669",
        "grad_to": "#064e3b"
    },

    # 6. Celebrations (Add 1 photo to pair with David & akash raval -> 3 total in Celebrations)
    {
        "title": "Campus Traditional Day & Garba Mahotsav",
        "category": "Celebrations",
        "description": "Joyous celebration of cultural heritage with vibrant ethnic attires, traditional music, and campus-wide unity.",
        "url": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=1200&auto=format&fit=crop&q=80",
        "filename": "gallery_seed_celebrations_3.jpg",
        "is_featured": True,
        "views_count": 135,
        "grad_from": "#be123c",
        "grad_to": "#4c0519"
    }
]


def allowed_gallery_file(filename):
    """Checks if file extension is an allowed image format."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def get_gallery_upload_folder():
    """Returns absolute path to uploads/gallery directory."""
    folder = os.path.join(current_app.root_path, 'uploads', 'gallery')
    os.makedirs(folder, exist_ok=True)
    return folder


def save_seed_photo_file(item_def, upload_folder):
    """
    Downloads image from URL or creates a beautiful SVG card if network is unavailable.
    Returns the final filename used.
    """
    target_jpg = os.path.join(upload_folder, item_def["filename"])
    target_svg = os.path.join(upload_folder, item_def["filename"].replace(".jpg", ".svg"))

    # If JPG already exists and is non-empty, use it
    if os.path.exists(target_jpg) and os.path.getsize(target_jpg) > 1000:
        return item_def["filename"]

    # If SVG already exists and is non-empty, use it
    if os.path.exists(target_svg) and os.path.getsize(target_svg) > 200:
        return item_def["filename"].replace(".jpg", ".svg")

    # Try downloading from URL
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            item_def["url"],
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=6, context=ctx) as response:
            content = response.read()
            if content and len(content) > 1000:
                with open(target_jpg, 'wb') as f:
                    f.write(content)
                return item_def["filename"]
    except Exception as dl_err:
        print(f"Notice: Could not download {item_def['title']}: {dl_err}. Creating SVG visual...")

    # Fallback to high-quality responsive SVG illustration
    c1 = item_def.get("grad_from", "#1e3a8a")
    c2 = item_def.get("grad_to", "#0f172a")
    category = item_def["category"]
    title = item_def["title"]
    
    words = title.split()
    mid = len(words) // 2
    line1 = " ".join(words[:mid]) if mid > 0 else title
    line2 = " ".join(words[mid:]) if mid > 0 else ""

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 520" width="800" height="520">
  <defs>
    <linearGradient id="grad_{item_def['filename'][:14]}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}" />
      <stop offset="100%" stop-color="{c2}" />
    </linearGradient>
    <pattern id="pat_{item_def['filename'][:14]}" width="36" height="36" patternUnits="userSpaceOnUse">
      <path d="M 36 0 L 0 0 0 36" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1.2"/>
    </pattern>
  </defs>
  <rect width="800" height="520" fill="url(#grad_{item_def['filename'][:14]})" />
  <rect width="800" height="520" fill="url(#pat_{item_def['filename'][:14]})" />
  <circle cx="720" cy="90" r="160" fill="rgba(255,255,255,0.05)" />
  <circle cx="120" cy="450" r="200" fill="rgba(255,255,255,0.03)" />
  <g transform="translate(60, 160)">
    <rect x="0" y="0" width="160" height="34" rx="17" fill="rgba(255,255,255,0.18)" />
    <text x="18" y="22" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700" fill="#ffffff" letter-spacing="1">{category.upper()}</text>
    <text x="0" y="90" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="34" font-weight="800" fill="#ffffff">{line1}</text>
    <text x="0" y="136" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="30" font-weight="700" fill="#93c5fd">{line2}</text>
    <text x="0" y="190" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="15" fill="rgba(255,255,255,0.85)">★ Official Campus Gallery Showcase • CampusSync</text>
  </g>
</svg>'''
    with open(target_svg, 'w', encoding='utf-8') as sf:
        sf.write(svg_content)
    return item_def["filename"].replace(".jpg", ".svg")


def ensure_category_photos_seeded():
    """
    Ensures initial 3 photos per category are seeded once.
    Once initial seeding is completed, it creates a persistent marker file
    '.seed_completed' so deleted photos are NEVER re-added.
    """
    upload_folder = get_gallery_upload_folder()
    marker_path = os.path.join(upload_folder, '.seed_completed')

    # If already completed initial seed, do nothing! Deleted photos stay deleted!
    if os.path.exists(marker_path):
        return

    # Deduplicate: if multiple items have identical titles, keep only the lowest ID
    all_items = GalleryItem.query.order_by(GalleryItem.id.asc()).all()
    seen_titles = set()
    duplicates_removed = False
    for item in all_items:
        norm_title = item.title.strip().lower()
        if norm_title in seen_titles:
            # Delete duplicate item record
            db.session.delete(item)
            duplicates_removed = True
        else:
            seen_titles.add(norm_title)

    if duplicates_removed:
        try:
            db.session.commit()
            db.session.expire_all()
        except Exception:
            db.session.rollback()

    # Check existing titles in database
    existing_items = GalleryItem.query.all()
    existing_titles = {i.title.strip().lower() for i in existing_items}

    added_any = False
    for seed in CURATED_GALLERY_SEEDS:
        if seed["title"].strip().lower() in existing_titles:
            continue

        final_filename = save_seed_photo_file(seed, upload_folder)
        new_item = GalleryItem(
            title=seed["title"],
            category=seed["category"],
            description=seed["description"],
            image_file=final_filename,
            is_featured=seed["is_featured"],
            views_count=seed["views_count"],
            status='Active',
            uploaded_by_id=None
        )
        db.session.add(new_item)
        added_any = True
        existing_titles.add(seed["title"].strip().lower())

    if added_any:
        try:
            db.session.commit()
            print("SUCCESS: Gallery category photos successfully seeded with 3 items per section.")
        except Exception as e:
            db.session.rollback()
            print(f"Notice: Gallery seed commit failed: {e}")

    # Mark as completed so photos deleted by admin will never be resurrected!
    try:
        with open(marker_path, 'w', encoding='utf-8') as mf:
            mf.write('completed')
    except Exception as e:
        print(f"Notice: Could not write seed marker: {e}")


def save_gallery_photo(file_obj):
    """
    Saves an uploaded photo with a secure unique filename.
    Returns the filename if successful, or None.
    """
    if not file_obj or file_obj.filename == '':
        return None, "No file selected."

    if not allowed_gallery_file(file_obj.filename):
        return None, "Invalid image format. Allowed formats: JPG, JPEG, PNG, WEBP, GIF, SVG."

    original_name = secure_filename(file_obj.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
    unique_name = f"gallery_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

    upload_folder = get_gallery_upload_folder()
    destination = os.path.join(upload_folder, unique_name)
    file_obj.save(destination)

    return unique_name, None


def get_active_gallery_items(category=None, limit=None, featured_only=False):
    """
    Fetches active gallery photos for public display.
    Ordered by featured status first, then newest first.
    """
    try:
        ensure_category_photos_seeded()
    except Exception as seed_err:
        print(f"Notice: Gallery auto-seed: {seed_err}")

    query = GalleryItem.query.filter_by(status='Active')

    if featured_only:
        query = query.filter_by(is_featured=True)

    if category and category != 'All':
        query = query.filter(GalleryItem.category == category)

    query = query.order_by(GalleryItem.is_featured.desc(), GalleryItem.created_at.desc())

    if limit:
        query = query.limit(limit)

    return query.all()


def get_admin_gallery_items(category=None, search=None, sort='newest'):
    """
    Fetches all gallery items for Admin management with search, filter, and sorting.
    """
    try:
        ensure_category_photos_seeded()
    except Exception as seed_err:
        print(f"Notice: Gallery auto-seed: {seed_err}")

    query = GalleryItem.query

    if category and category != 'All':
        query = query.filter(GalleryItem.category == category)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            db.or_(
                GalleryItem.title.ilike(search_term),
                GalleryItem.description.ilike(search_term),
                GalleryItem.category.ilike(search_term)
            )
        )

    if sort == 'oldest':
        query = query.order_by(GalleryItem.created_at.asc())
    elif sort == 'featured':
        query = query.order_by(GalleryItem.is_featured.desc(), GalleryItem.created_at.desc())
    elif sort == 'title':
        query = query.order_by(GalleryItem.title.asc())
    else:  # 'newest' default
        query = query.order_by(GalleryItem.created_at.desc())

    return query.all()


def get_gallery_stats():
    """
    Calculates summary statistics for Admin Gallery dashboard.
    """
    total = GalleryItem.query.count()
    active = GalleryItem.query.filter_by(status='Active').count()
    featured = GalleryItem.query.filter_by(is_featured=True).count()
    categories_count = db.session.query(GalleryItem.category).distinct().count()
    total_views = db.session.query(db.func.coalesce(db.func.sum(GalleryItem.views_count), 0)).scalar() or 0

    cat_counts_query = db.session.query(GalleryItem.category, db.func.count(GalleryItem.id)).group_by(GalleryItem.category).all()
    category_counts = {cat: count for cat, count in cat_counts_query}

    return {
        "total": total,
        "active": active,
        "featured": featured,
        "categories_count": categories_count or len(GALLERY_CATEGORIES),
        "total_views": int(total_views),
        "category_counts": category_counts
    }


def create_gallery_item(title, category, file_obj, description='', is_featured=False, admin_id=None):
    """
    Creates and saves a new gallery item in database.
    """
    if not title or not title.strip():
        return False, "Photo title is required.", None

    filename, err = save_gallery_photo(file_obj)
    if err:
        return False, err, None

    if category not in GALLERY_CATEGORIES:
        category = 'Campus Life'

    item = GalleryItem(
        title=title.strip(),
        category=category,
        description=description.strip() if description else None,
        image_file=filename,
        is_featured=bool(is_featured),
        status='Active',
        uploaded_by_id=admin_id
    )

    db.session.add(item)
    db.session.commit()
    return True, "Gallery photo uploaded successfully!", item


def update_gallery_item(item_id, title=None, category=None, description=None, is_featured=None, status=None, file_obj=None):
    """
    Updates an existing gallery item.
    """
    item = GalleryItem.query.get(item_id)
    if not item:
        return False, "Gallery item not found."

    if title is not None and title.strip():
        item.title = title.strip()

    if category is not None and category in GALLERY_CATEGORIES:
        item.category = category

    if description is not None:
        item.description = description.strip() if description else None

    if is_featured is not None:
        item.is_featured = bool(is_featured)

    if status is not None and status in ('Active', 'Inactive'):
        item.status = status

    if file_obj and file_obj.filename:
        new_filename, err = save_gallery_photo(file_obj)
        if not err and new_filename:
            # Delete old image file safely
            old_path = os.path.join(get_gallery_upload_folder(), item.image_file)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass
            item.image_file = new_filename

    item.updated_at = datetime.utcnow()
    db.session.commit()
    return True, "Gallery photo updated successfully!"


def delete_gallery_item(item_id):
    """
    Deletes a gallery item from database and removes its file from disk.
    """
    item = GalleryItem.query.get(item_id)
    if not item:
        return False, "Gallery item not found."

    image_filename = item.image_file
    try:
        db.session.delete(item)
        db.session.commit()
        db.session.expire_all()
    except Exception as e:
        db.session.rollback()
        return False, f"Database error deleting item: {str(e)}"

    # Safely remove image file if not referenced by any other gallery item
    try:
        if image_filename:
            other_references = GalleryItem.query.filter_by(image_file=image_filename).count()
            if other_references == 0:
                file_to_remove = os.path.join(get_gallery_upload_folder(), image_filename)
                if os.path.exists(file_to_remove):
                    os.remove(file_to_remove)
    except Exception as file_err:
        print(f"Notice: Image file remove warning: {file_err}")

    return True, "Gallery photo deleted successfully."


def toggle_gallery_item_status(item_id):
    """
    Toggles photo visibility between Active and Inactive.
    """
    item = GalleryItem.query.get(item_id)
    if not item:
        return False, "Gallery item not found.", None

    item.status = 'Inactive' if item.status == 'Active' else 'Active'
    item.updated_at = datetime.utcnow()
    db.session.commit()
    return True, f"Photo status updated to {item.status}.", item.status


def toggle_gallery_item_featured(item_id):
    """
    Toggles featured badge status.
    """
    item = GalleryItem.query.get(item_id)
    if not item:
        return False, "Gallery item not found.", None

    item.is_featured = not item.is_featured
    item.updated_at = datetime.utcnow()
    db.session.commit()
    msg = "Marked as featured on homepage." if item.is_featured else "Removed from featured."
    return True, msg, item.is_featured


def increment_gallery_view(item_id):
    """
    Increments views_count by 1 for a gallery item when clicked/viewed.
    Returns the new views_count.
    """
    item = GalleryItem.query.get(item_id)
    if item:
        item.views_count = (item.views_count or 0) + 1
        db.session.commit()
        return item.views_count
    return 0
