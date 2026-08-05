"""
Authentication routes - Parent (PIN) and Admin (Password)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db
from models import User, Student, Parent
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

# ============= PARENT LOGIN =============
@auth_bp.route('/parent-login', methods=['POST'])
def parent_login():
    """Parent login with email + 4-digit PIN"""
    data = request.get_json()
    email = data.get('email')
    pin = data.get('pin')

    if not email or not pin:
        return {'error': 'Email and PIN required'}, 400

    if len(pin) != 4 or not pin.isdigit():
        return {'error': 'PIN must be 4 digits'}, 400

    # Find student by parent email and PIN
    student = Student.query.filter_by(parent_email=email, parent_pin=pin).first()

    if not student:
        return {'error': 'Invalid email or PIN'}, 401

    # Get or create parent user
    user = User.query.filter_by(email=email, role='parent').first()

    if not user:
        # Create parent user if doesn't exist
        user = User(email=email, role='parent')
        user.set_password(pin)  # Store PIN as password hash
        db.session.add(user)
        db.session.commit()

    # Create JWT token (expires in 30 days for persistent login)
    token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30),
        additional_claims={'role': 'parent', 'email': email}
    )

    return {
        'access_token': token,
        'user_id': user.id,
        'role': 'parent',
        'email': email,
        'student_name': student.name
    }, 200

# ============= CHANGE PIN =============
@auth_bp.route('/change-pin', methods=['POST'])
def change_pin():
    """Parent changes their own 4-digit login PIN."""
    from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt

    try:
        verify_jwt_in_request()
    except Exception:
        return {'error': 'Not signed in'}, 401

    claims = get_jwt()
    if claims.get('role') != 'parent':
        return {'error': 'Only parents can change a PIN here'}, 403

    email = claims.get('email')
    if not email:
        return {'error': 'Could not identify account'}, 400

    data = request.get_json() or {}
    current_pin = (data.get('current_pin') or '').strip()
    new_pin = (data.get('new_pin') or '').strip()

    if not current_pin or not new_pin:
        return {'error': 'Current and new PIN are both required'}, 400
    if len(new_pin) != 4 or not new_pin.isdigit():
        return {'error': 'New PIN must be exactly 4 digits'}, 400
    if new_pin == current_pin:
        return {'error': 'New PIN must be different from the current one'}, 400

    # One parent email can cover several siblings - all must stay in sync,
    # otherwise login would still succeed with the old PIN via another student.
    students = Student.query.filter_by(parent_email=email).all()
    if not students:
        return {'error': 'No students found for this account'}, 404

    if not any(s.parent_pin == current_pin for s in students):
        return {'error': 'Current PIN is incorrect'}, 401

    try:
        for s in students:
            s.parent_pin = new_pin

        # parent_login also stores the PIN as the User password hash
        user = User.query.filter_by(email=email, role='parent').first()
        if user:
            user.set_password(new_pin)

        db.session.commit()
        return {
            'message': 'PIN updated',
            'students_updated': len(students)
        }, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

# ============= ADMIN LOGIN =============
@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """Admin login with email + password"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Email and password required'}, 400

        user = User.query.filter_by(email=email, role='admin').first()

        if not user or not user.check_password(password):
            return {'error': 'Invalid email or password'}, 401

        # Create JWT token (expires in 30 days for persistent login)
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30),
            additional_claims={'role': 'admin', 'email': email}
        )

        return {
            'access_token': token,
            'user_id': user.id,
            'role': 'admin',
            'email': email
        }, 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}, 500

# ============= GET CURRENT USER =============
@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user (from JWT token)"""
    from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

    try:
        jwt_required()(lambda: None)  # Verify token exists
    except:
        return {'error': 'Unauthorized'}, 401

    user_id = get_jwt_identity()
    claims = get_jwt()

    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'User not found'}, 404

    return {
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'claims': claims
    }, 200

# ============= LOGOUT =============
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout (client-side: delete token from localStorage)"""
    return {'message': 'Logged out successfully'}, 200

# ============= ADMIN SETUP (First Time Only) =============
@auth_bp.route('/setup-admin', methods=['POST'])
def setup_admin():
    """Setup first admin user - only works if no admin exists"""
    # Check if admin already exists
    admin_exists = db.session.execute(
        select(User).filter_by(role='admin')
    ).scalar()

    if admin_exists:
        return {'error': 'Admin already exists'}, 403

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'error': 'Email and password required'}, 400

    # Create first admin user
    admin = User(email=email, role='admin')
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    token = create_access_token(
        identity=str(admin.id),
        expires_delta=timedelta(days=30),
        additional_claims={'role': 'admin', 'email': email}
    )

    return {
        'message': 'Admin account created',
        'access_token': token,
        'user_id': admin.id,
        'role': 'admin'
    }, 201
