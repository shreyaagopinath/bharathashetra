"""
Bharathashetra Backend - Phase 1
Database + CSV Import + Parent PIN Login + Admin Password Login
"""
from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import os
from extensions import db, jwt
from datetime import timedelta

# Get absolute paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), 'frontend')

# Use /tmp for Render, local for development
if os.getenv('RENDER'):
    DATABASE_PATH = '/tmp/bharathashetra.db'
else:
    DB_FILE = os.getenv('DATABASE_PATH', 'bharathashetra.db')
    DATABASE_PATH = DB_FILE if DB_FILE.startswith('/') or DB_FILE.startswith('sqlite:') else os.path.join(BACKEND_DIR, DB_FILE)

# Ensure database directory exists
os.makedirs(os.path.dirname(DATABASE_PATH) or '.', exist_ok=True)

def create_app():
    """Application factory"""
    app = Flask(__name__)

    # Configuration
    # Ensure proper SQLite URI format
    if DATABASE_PATH.startswith('sqlite:'):
        db_uri = DATABASE_PATH
    else:
        db_uri = f'sqlite:///{DATABASE_PATH}'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'bharathashetra-secret-key-dev-2024')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'bharathashetra-jwt-secret-key-dev-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)  # 30 days for persistent login

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

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

    # API Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'phase': 'phase-1'}, 200

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
    db_display = DATABASE_PATH if DATABASE_PATH.startswith('sqlite:') else f'sqlite:///{DATABASE_PATH}'
    print(f"Database: {db_display}")
    print(f"Frontend: {FRONTEND_DIR}")
    print(f"Port: 8000")
    print("=" * 60)

    app.run(debug=True, port=8000, host='0.0.0.0')
