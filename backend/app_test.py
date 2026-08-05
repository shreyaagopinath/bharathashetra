"""
Bharathashetra Backend - Test Version with Fresh Database
"""
from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import os
from extensions import db, jwt
from datetime import timedelta

# Use temp database for testing
DATABASE_PATH = '/tmp/test_bharatha.db'

def create_app():
    """Application factory"""
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

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

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(import_bp, url_prefix='/api')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(photos_bp, url_prefix='/api/photos')
    app.register_blueprint(contact_bp, url_prefix='/api/contact')

    # Create tables and setup
    with app.app_context():
        db.create_all()

    # API Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'ok', 'phase': 'test'}, 200

    return app

if __name__ == '__main__':
    print("=" * 60)
    print("BHARATHASHETRA BACKEND - TEST VERSION")
    print("=" * 60)
    print(f"Database: {DATABASE_PATH}")
    print(f"Port: 8000")
    print("=" * 60)

    app = create_app()
    app.run(debug=False, port=8000, host='127.0.0.1', use_reloader=False)
