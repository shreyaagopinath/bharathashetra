"""
Bharathashetra Backend - Phase 1
Database + CSV Import + Parent PIN Login + Admin Password Login
"""
import os

# SET SECRETS BEFORE ANY IMPORTS OF JWT
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'bharathashetra-secret-key-2024'
if 'JWT_SECRET_KEY' not in os.environ:
    os.environ['JWT_SECRET_KEY'] = 'bharathashetra-jwt-secret-2024'

from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
from extensions import db, jwt
from datetime import timedelta

# Get absolute paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), 'frontend')

# Resolve the database URI once, correctly, for both Postgres and SQLite.
#
# NOTE: this block previously wrapped EVERY value in `sqlite:///`, so a valid
# DATABASE_URL like `postgresql://user@host/db` became
# `sqlite:///postgresql://user@host/db` - i.e. a throwaway SQLite file with a
# very strange name. The app appeared to boot fine but every record was wiped
# on each restart/redeploy. Do not reintroduce that fallback.
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Heroku/Render-style URLs use the legacy postgres:// scheme
    DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    DB_FILE = os.getenv('DATABASE_PATH', 'bharathashetra.db')
    if DB_FILE.startswith('sqlite:'):
        DATABASE_URI = DB_FILE
    else:
        abs_path = DB_FILE if os.path.isabs(DB_FILE) else os.path.join(BACKEND_DIR, DB_FILE)
        os.makedirs(os.path.dirname(abs_path) or '.', exist_ok=True)
        DATABASE_URI = f'sqlite:///{abs_path}'

DATABASE_PATH = DATABASE_URI  # kept for the startup banner below

def create_app():
    """Application factory"""
    app = Flask(__name__)

    # Configuration
    db_uri = DATABASE_URI
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    print(f"→ Database engine: {'PostgreSQL (persistent)' if db_uri.startswith('postgres') else 'SQLite (EPHEMERAL on Render)'}")

    # Connection pooling only for PostgreSQL, not SQLite
    if db_uri.startswith('postgresql://') or db_uri.startswith('postgresql+psycopg2://'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'connect_args': {'connect_timeout': 10}
        }
    # Set secrets FIRST before JWT init
    secret_key = 'bharathashetra-secret-key-production-2024'
    jwt_secret = 'bharathashetra-jwt-secret-production-2024'

    # FORCE set secrets - no environment variable checking
    app.config['SECRET_KEY'] = secret_key
    app.config['JWT_SECRET_KEY'] = jwt_secret
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Verify secrets are set
    assert app.config['JWT_SECRET_KEY'], "JWT_SECRET_KEY not set!"
    assert app.config['SECRET_KEY'], "SECRET_KEY not set!"

    # Import models BEFORE creating tables
    from models import (
        User, Parent, Student, DanceClass, Enrollment,
        ClassSession, Attendance, Payment, Form, FormField,
        FormResponse, Video, Announcement, Setting, BackupLog,
        PhotoAlbum, Photo, ContactMessage
    )

    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints
    from routes.auth_v2 import auth_bp
    from routes.import_csv import import_bp
    from routes.payments import payments_bp
    from routes.attendance import attendance_bp
    from routes.students import students_bp
    from routes.photos import photos_bp
    from routes.contact import contact_bp
    from routes.announcements import announcements_bp
    from routes.videos import videos_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(import_bp, url_prefix='/api')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(photos_bp, url_prefix='/api/photos')
    app.register_blueprint(contact_bp, url_prefix='/api/contact')
    app.register_blueprint(announcements_bp, url_prefix='/api/announcements')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')

    # Create tables and setup
    with app.app_context():
        db.create_all()

        # Create default admin if it doesn't exist
        try:
            admin_exists = db.session.query(User).filter_by(role='admin').first()
            if not admin_exists:
                admin = User(email='admin@dance.local', role='admin')
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✓ Created default admin: admin@dance.local / Admin123!")
        except Exception as e:
            print(f"Note: Could not create default admin: {e}")

    # API Health check + storage diagnostics (no credentials exposed)
    @app.route('/api/health', methods=['GET'])
    def health():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        engine = 'postgresql' if uri.startswith('postgres') else 'sqlite'
        info = {
            'status': 'ok',
            'phase': 'phase-1',
            'db_engine': engine,
            'persistent': engine == 'postgresql',
            'database_url_env_set': bool(os.getenv('DATABASE_URL')),
        }
        try:
            from models import Student
            info['student_count'] = db.session.query(Student).count()
        except Exception as e:
            info['student_count'] = None
            info['db_error'] = str(e)[:200]
        if engine == 'sqlite':
            info['warning'] = ('Using SQLite on an ephemeral disk - all data is erased whenever '
                               'the server restarts or redeploys. Set DATABASE_URL to a PostgreSQL '
                               'connection string to make data persist.')
        return info, 200

    # Serve frontend files
    @app.route('/')
    def serve_root():
        return send_file(os.path.join(FRONTEND_DIR, 'index.html'))

    @app.route('/login.html')
    def serve_login():
        return send_file(os.path.join(FRONTEND_DIR, 'login.html'))

    @app.route('/index.html')
    def serve_index():
        return send_file(os.path.join(FRONTEND_DIR, 'index.html'))

    @app.route('/<path:path>')
    def serve_static(path):
        try:
            return send_file(os.path.join(FRONTEND_DIR, path))
        except:
            return {'error': 'Not found'}, 404

    return app

# Create app at module level for gunicorn
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("BHARATHASHETRA BACKEND - PHASE 1")
    print("=" * 60)
    # Mask credentials if this is a Postgres URL
    import re as _re
    print(f"Database: {_re.sub(r'//[^@]+@', '//***:***@', DATABASE_URI)}")
    print(f"Frontend: {FRONTEND_DIR}")
    print(f"Port: 8000")
    print("=" * 60)

    app.run(debug=True, port=8000, host='0.0.0.0')
