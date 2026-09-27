import os
from app import app

# For WSGI servers (Gunicorn, uWSGI, Waitress, mod_wsgi, Passenger)
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1")
    app.run(host="0.0.0.0", port=port, debug=debug)
