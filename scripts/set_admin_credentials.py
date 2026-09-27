import os
import sys

# Ensure the project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from extensions import db
from models import Admin
from werkzeug.security import generate_password_hash


def set_admin_credentials(new_username='admin', new_password='admin'):
    """Set the admin account's username and password to the given values.
    If an admin record does not exist, it will be created.
    """
    admin = Admin.query.filter_by(username=new_username).first()
    if not admin:
        # Try to get any admin record
        admin = Admin.query.first()
    if not admin:
        # No admin exists, create one
        admin = Admin(
            username=new_username,
            password=generate_password_hash(new_password),
            full_name='Administrator',
            email='admin@example.com',
            mobile='0000000000',
            status='Active'
        )
        db.session.add(admin)
        db.session.commit()
        print('Created new admin with username and password set to "admin"')
        return
    # Update existing admin
    admin.username = new_username
    admin.password = generate_password_hash(new_password)
    db.session.commit()
    print(f'Admin credentials updated: username={new_username}, password={new_password}')

if __name__ == '__main__':
    # Running within Flask app context
    from app import app
    with app.app_context():
        set_admin_credentials()
