"""
Database Migration: Add stamp, signature to college_settings and create result_declarations table
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text
from models import ResultDeclaration, CollegeSetting

with app.app_context():
    db.create_all()
    # Check if college_stamp and principal_signature exist on college_settings
    cols = [r[0] for r in db.session.execute(text("SHOW COLUMNS FROM college_settings")).fetchall()]
    print('Existing college_settings columns:', cols)
    if 'college_stamp' not in cols:
        db.session.execute(text("ALTER TABLE college_settings ADD COLUMN college_stamp VARCHAR(255) NULL DEFAULT 'default-stamp.png'"))
        print('Added college_stamp column.')
    if 'principal_signature' not in cols:
        db.session.execute(text("ALTER TABLE college_settings ADD COLUMN principal_signature VARCHAR(255) NULL DEFAULT 'default-signature.png'"))
        print('Added principal_signature column.')
    db.session.commit()
    print('DB migration complete!')
