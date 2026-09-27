import os
from urllib.parse import urlsplit
import mysql.connector
from mysql.connector import Error
from config import Config

def _get_db_params():
    """Extracts database connection parameters from SQLALCHEMY_DATABASE_URI or Config."""
    raw_url = getattr(Config, 'SQLALCHEMY_DATABASE_URI', '')
    if raw_url and ('@' in raw_url):
        clean_url = raw_url.replace('mysql+pymysql://', 'mysql://').replace('postgresql://', 'mysql://')
        parsed = urlsplit(clean_url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 3306,
            'user': parsed.username or 'root',
            'password': parsed.password or '',
            'database': (parsed.path or '').lstrip('/') or 'campussync'
        }
    return {
        'host': getattr(Config, 'DB_HOST', 'localhost'),
        'port': getattr(Config, 'DB_PORT', 3306),
        'user': getattr(Config, 'DB_USER', 'root'),
        'password': getattr(Config, 'DB_PASSWORD', ''),
        'database': getattr(Config, 'DB_NAME', 'campussync')
    }

def init_database_if_missing():
    """
    Auto-creates the 'campussync' database and imports 'campussync.sql' 
    if the database does not exist yet.
    """
    params = _get_db_params()
    try:
        # Connect to MySQL server without specifying database
        server_conn = mysql.connector.connect(
            host=params['host'],
            port=params['port'],
            user=params['user'],
            password=params['password']
        )
        if server_conn.is_connected():
            cursor = server_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{params['database']}` DEFAULT CHARACTER SET utf8mb4;")
            cursor.execute(f"USE `{params['database']}`;")
            
            # Path to campussync.sql script
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sql_file_path = os.path.join(base_dir, 'database', 'campussync.sql')

            if os.path.exists(sql_file_path):
                with open(sql_file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Split SQL queries by semicolon and execute
                commands = sql_content.split(';')
                for command in commands:
                    cmd = command.strip()
                    if cmd:
                        cursor.execute(cmd)
                server_conn.commit()
                print(f"[Auto Setup]: Database '{params['database']}' created and table 'admins' imported successfully!")
            
            cursor.close()
            server_conn.close()
            return True
    except Error as err:
        print(f"[Auto Setup Notice]: Could not auto-create database (might be cloud-managed). Details: {err}")
        return False

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Uses credentials loaded from config.py / .env file.
    If database does not exist (Error 1049), attempts auto-creation.
    """
    params = _get_db_params()
    try:
        connection = mysql.connector.connect(
            host=params['host'],
            port=params['port'],
            database=params['database'],
            user=params['user'],
            password=params['password']
        )
        if connection.is_connected():
            return connection
    except Error as err:
        # Error 1049: Unknown database 'campussync'
        if err.errno == 1049:
            print(f"[Notice]: Database '{params['database']}' not found. Attempting automatic creation...")
            if init_database_if_missing():
                try:
                    return mysql.connector.connect(
                        host=params['host'],
                        port=params['port'],
                        database=params['database'],
                        user=params['user'],
                        password=params['password']
                    )
                except Error as retry_err:
                    print(f"[MySQL Retry Error]: {retry_err}")
                    return None
        
        # Print helpful error message for debugging
        print(f"[MySQL Connection Error]: Unable to connect to database '{params['database']}'.")
        print(f"[Details]: {err}")
        return None

def test_connection():
    """
    Simple helper function to verify if database connection is working.
    Returns True if connected, False otherwise.
    """
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            conn.close()
            return True
    except Exception:
        pass

    try:
        from extensions import db
        with db.engine.connect() as conn:
            return True
    except Exception:
        return False
