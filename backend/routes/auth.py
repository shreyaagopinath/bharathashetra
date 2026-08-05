from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import User, Parent
from sqlalchemy import select

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (parent)"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    existing_user = db.session.execute(select(User).filter_by(email=data['email'])).scalar()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409

    try:
        user = User(email=data['email'], role='parent')
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        parent = Parent(
            user_id=user.id,
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            address=data.get('address', '')
        )
        db.session.add(parent)
        db.session.commit()

        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user_id': user.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = db.session.execute(select(User).filter_by(email=data['email'])).scalar()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        'access_token': access_token,
        'user_id': user.id,
        'role': user.role
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = db.session.execute(select(User).filter(User.id == user_id)).scalar()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (token blacklisting can be implemented)"""
    return jsonify({'message': 'Logged out successfully'}), 200
