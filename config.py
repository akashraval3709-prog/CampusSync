import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Application Configuration Class
    Loads database settings and secret keys from environment variables (.env)
    """
    # Database Settings
    raw_db_url = (
        os.getenv('DATABASE_URL') or 
        os.getenv('MYSQL_URL') or 
        os.getenv('CLEARDB_DATABASE_URL') or 
        os.getenv('JAWSDB_URL')
    )
    if raw_db_url:
        if raw_db_url.startswith('mysql://') or raw_db_url.startswith('mysql+pymysql://'):
            uri = raw_db_url.replace('mysql://', 'mysql+pymysql://', 1)
            if 'charset=' not in uri:
                uri += ('&' if '?' in uri else '?') + 'charset=utf8mb4'
            SQLALCHEMY_DATABASE_URI = uri
        elif raw_db_url.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = raw_db_url.replace('postgres://', 'postgresql://', 1)
        else:
            SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        try:
            DB_PORT = int(os.getenv('DB_PORT', 3306))
        except (ValueError, TypeError):
            DB_PORT = 3306
        DB_NAME = os.getenv('DB_NAME', 'campussync')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Production Database Connection Pool (prevents 'MySQL server has gone away' on hosting servers)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_timeout': 30,
        'max_overflow': 15,
    }

    # Flask Application Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'campussync_default_production_key_change_me')
    from datetime import timedelta
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload payload

    # Flask-Mail SMTP Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    try:
        MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    except (ValueError, TypeError):
        MAIL_PORT = 587
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'devidparmar8954@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'kjdu cius cygw nhyl')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'devidparmar8954@gmail.com')

    # Brevo REST API Configuration (Bypasses SMTP port blocking on Railway / Cloud hosting)
    BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')

    # Flask-Compress Optimization
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'image/svg+xml'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

