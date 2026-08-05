from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
from extensions import db, jwt

# Load environment variables
load_dotenv()

# Get absolute paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), 'frontend')
DATABASE_PATH = os.path.join(BACKEND_DIR, 'bharathashetra.db')

def create_app():
    """Application factory"""
    # Disable Flask's built-in static file serving - we handle it manually
    app = Flask(__name__, static_folder=None)

    # Configuration - use absolute database path
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Import models BEFORE creating tables
    from models import User, Parent, Student, DanceClass, Enrollment, ClassSession, Attendance, Payment, Form, FormField, FormResponse, Video, Announcement, Setting, BackupLog

    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["*"]}})

    # Register blueprints FIRST (before static routes)
    from routes import (
        auth_bp, students_bp, parents_bp, classes_bp,
        attendance_bp, payments_bp, forms_bp, videos_bp,
        announcements_bp, settings_bp, backup_bp
    )

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(parents_bp, url_prefix='/api/parents')
    app.register_blueprint(classes_bp, url_prefix='/api/classes')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(forms_bp, url_prefix='/api/forms')
    app.register_blueprint(videos_bp, url_prefix='/api/videos')
    app.register_blueprint(announcements_bp, url_prefix='/api/announcements')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')

    # Create tables and default admin user
    with app.app_context():
        db.create_all()

        # Create default admin if it doesn't exist
        from sqlalchemy import select

        try:
            admin = db.session.execute(select(User).filter_by(email='admin@dance.local')).scalar()
            if not admin:
                admin = User(email='admin@dance.local', role='admin')
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                print("✓ Created default admin: admin@dance.local / Admin123!")
        except Exception as e:
            print(f"Note: Could not create default admin: {e}")

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok'}, 200

    # Test endpoint to verify backend is working
    @app.route('/api/test-login', methods=['POST', 'GET'])
    def test_login():
        """Simple test endpoint"""
        if request.method == 'GET':
            return {'message': 'Backend is working! POST email and password as JSON'}, 200

        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')

        from models import User
        from sqlalchemy import select

        if not email or not password:
            return {'error': 'Email and password required'}, 400

        user = db.session.execute(select(User).filter_by(email=email)).scalar()
        if not user or not user.check_password(password):
            return {'error': f'Invalid login. User exists: {user is not None}'}, 401

        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=user.id)
        return {'access_token': token, 'user_id': user.id, 'role': user.role}, 200

    # Debug: Print frontend path info
    print(f"\n📁 Frontend Directory: {FRONTEND_DIR}")
    print(f"📁 Frontend exists: {os.path.isdir(FRONTEND_DIR)}")
    if os.path.isdir(FRONTEND_DIR):
        files = os.listdir(FRONTEND_DIR)
        print(f"📁 Files in frontend: {files}\n")

    # Serve frontend files - MUST BE AFTER API ROUTES
    @app.route('/')
    def serve_root():
        print(f"[Route /] Serving index.html from {FRONTEND_DIR}")
        try:
            return send_from_directory(FRONTEND_DIR, 'index.html')
        except Exception as e:
            print(f"[Route /] Error: {e}")
            return {'error': str(e)}, 500

    @app.route('/login.html')
    def serve_login():
        print(f"[Route /login.html] Serving from {FRONTEND_DIR}")
        try:
            return send_from_directory(FRONTEND_DIR, 'login.html')
        except Exception as e:
            print(f"[Route /login.html] Error: {e}")
            return {'error': str(e)}, 500

    @app.route('/index.html')
    def serve_index():
        print(f"[Route /index.html] Serving from {FRONTEND_DIR}")
        try:
            return send_from_directory(FRONTEND_DIR, 'index.html')
        except Exception as e:
            print(f"[Route /index.html] Error: {e}")
            return {'error': str(e)}, 500

    @app.route('/<path:filepath>')
    def serve_static(filepath):
        """Serve any static file (js, css, etc)"""
        print(f"[Route /<path>] Requesting {filepath} from {FRONTEND_DIR}")
        try:
            return send_from_directory(FRONTEND_DIR, filepath)
        except Exception as e:
            print(f"[Route /<path>] Error for {filepath}: {e}")
            return {'error': f'File not found: {filepath}'}, 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
