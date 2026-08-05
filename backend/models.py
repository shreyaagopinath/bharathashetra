from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='parent')  # admin, parent, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = db.relationship('Parent', backref='user', uselist=False, cascade='all, delete-orphan')
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Parent(db.Model):
    """Parent information"""
    __tablename__ = 'parents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

    # Relationships
    students = db.relationship('Student', backref='parent', lazy=True, cascade='all, delete-orphan')

class Student(db.Model):
    """Student information"""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    parent_email = db.Column(db.String(120))  # For CSV import
    parent_pin = db.Column(db.String(4))  # 4-digit PIN for parent login
    class_day = db.Column(db.String(20))  # Monday, Tuesday, etc.
    class_time = db.Column(db.String(20))  # HH:MM format
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended

    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='student', lazy=True, cascade='all, delete-orphan')

class DanceClass(db.Model):
    """Dance class information"""
    __tablename__ = 'dance_classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    style = db.Column(db.String(80))  # Bharatanatyam, Kathak, etc.
    level = db.Column(db.String(20))  # Beginner, Intermediate, Advanced
    instructor = db.Column(db.String(120))
    schedule = db.Column(db.String(200))  # Days and times
    capacity = db.Column(db.Integer)
    fees = db.Column(db.Float)
    description = db.Column(db.Text)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='dance_class', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('ClassSession', backref='dance_class', lazy=True, cascade='all, delete-orphan')

class Enrollment(db.Model):
    """Student enrollment in classes"""
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('dance_classes.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, dropped

    # Relationships
    attendance = db.relationship('Attendance', backref='enrollment', lazy=True, cascade='all, delete-orphan')

class ClassSession(db.Model):
    """Individual class sessions"""
    __tablename__ = 'class_sessions'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('dance_classes.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)

    # Relationships
    attendance_records = db.relationship('Attendance', backref='session', lazy=True, cascade='all, delete-orphan')

class Attendance(db.Model):
    """Attendance records"""
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('class_sessions.id'), nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent, late
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    """Payment records"""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))  # zelle, cash, card
    transaction_id = db.Column(db.String(100), unique=True, index=True)
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    month_paid_for = db.Column(db.String(7))  # e.g., "2024-10" (year-month format)
    late_fee_applied = db.Column(db.Float, default=0)  # e.g., 10.00
    notes = db.Column(db.Text)

class Form(db.Model):
    """Forms/applications"""
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    form_type = db.Column(db.String(50))  # registration, feedback, etc.

    # Relationships
    responses = db.relationship('FormResponse', backref='form', lazy=True, cascade='all, delete-orphan')
    fields = db.relationship('FormField', backref='form', lazy=True, cascade='all, delete-orphan')

class FormField(db.Model):
    """Form fields"""
    __tablename__ = 'form_fields'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    field_name = db.Column(db.String(120), nullable=False)
    field_type = db.Column(db.String(50))  # text, email, phone, select, etc.
    required = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer)

class FormResponse(db.Model):
    """Form responses from users"""
    __tablename__ = 'form_responses'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    response_data = db.Column(db.JSON)  # Store form responses as JSON
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Video(db.Model):
    """Video content"""
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # e.g., "Stage Ready", "Theermanam", etc.
    class_id = db.Column(db.Integer, db.ForeignKey('dance_classes.id'))
    video_url = db.Column(db.String(500))  # YouTube URL or hosted video
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    instructor = db.Column(db.String(120))
    duration = db.Column(db.Integer)  # in seconds
    visibility = db.Column(db.String(20), default='private')  # public, private, members-only

class Announcement(db.Model):
    """Admin announcements for parents"""
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # Higher = shows first

class Setting(db.Model):
    """Customizable app settings"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, index=True)  # e.g., "tab_payments", "late_fee_amount"
    value = db.Column(db.Text)  # Store as JSON for complex values
    category = db.Column(db.String(50))  # e.g., "tabs", "payments", "appearance"
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BackupLog(db.Model):
    """Track database backups"""
    __tablename__ = 'backup_logs'

    id = db.Column(db.Integer, primary_key=True)
    backup_date = db.Column(db.DateTime, default=datetime.utcnow)
    backup_size = db.Column(db.String(50))  # e.g., "2.5 MB"
    status = db.Column(db.String(20), default='success')  # success, failed
    backup_file = db.Column(db.String(255))  # Path to backup file
    notes = db.Column(db.Text)

class PhotoAlbum(db.Model):
    """Photo albums"""
    __tablename__ = 'photo_albums'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cover_photo_url = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)

    # Relationships
    photos = db.relationship('Photo', backref='album', lazy=True, cascade='all, delete-orphan')

class Photo(db.Model):
    """Photos in albums"""
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('photo_albums.id'), nullable=False)
    photo_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.Column(db.Integer, default=0)

class ContactMessage(db.Model):
    """Parent contact messages to admin"""
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    parent_name = db.Column(db.String(120), nullable=False)
    parent_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    response = db.Column(db.Text)
    responded_at = db.Column(db.DateTime)
