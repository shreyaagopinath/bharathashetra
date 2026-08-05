from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Student, User, Parent
from datetime import datetime

students_bp = Blueprint('students', __name__)

@students_bp.route('', methods=['GET'])
@jwt_required()
def get_students():
    """Get all students (admin) or student's own info, with optional filtering"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Get filter parameters
    class_day = request.args.get('class_day')
    class_time = request.args.get('class_time')
    search_name = request.args.get('search')

    if user.role == 'admin':
        query = Student.query

        # Apply filters
        if class_day:
            query = query.filter_by(class_day=class_day)
        if class_time:
            query = query.filter_by(class_time=class_time)
        if search_name:
            query = query.filter(Student.name.ilike(f'%{search_name}%'))

        students = query.all()
    elif user.role == 'parent':
        # Try parent_id first (for traditional enrollment)
        parent = Parent.query.filter_by(user_id=user_id).first()
        if parent:
            students = Student.query.filter_by(parent_id=parent.id).all()
        else:
            # If no Parent record, look up by parent_email (for CSV import)
            students = Student.query.filter_by(parent_email=user.email).all()
    else:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify([{
        'id': s.id,
        'name': s.name,
        'first_name': s.first_name,
        'last_name': s.last_name,
        'email': s.email,
        'phone': s.phone,
        'parent_email': s.parent_email,
        'class_day': s.class_day,
        'class_time': s.class_time,
        'status': s.status,
        'date_of_birth': s.date_of_birth.isoformat() if s.date_of_birth else None,
        'registration_date': s.registration_date.isoformat()
    } for s in students]), 200

@students_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    """Get specific student info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Check authorization
    if user.role != 'admin':
        parent = Parent.query.filter_by(user_id=user_id).first()
        if not parent or student.parent_id != parent.id:
            return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'id': student.id,
        'name': student.name,
        'email': student.email,
        'phone': student.phone,
        'status': student.status,
        'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
        'registration_date': student.registration_date.isoformat()
    }), 200

@students_bp.route('', methods=['POST'])
@jwt_required()
def create_student():
    """Register a new student"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ['admin', 'parent']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    try:
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Student name is required'}), 400

        # Validate email format if provided
        if data.get('email'):
            email = data.get('email').strip()
            if '@' not in email or '.' not in email:
                return jsonify({'error': 'Invalid email format'}), 400
        else:
            email = None

        parent_id = None
        if user.role == 'parent':
            parent = Parent.query.filter_by(user_id=user_id).first()
            parent_id = parent.id if parent else None

        # Convert date string to Python date object
        dob = data.get('date_of_birth')
        if dob and isinstance(dob, str):
            try:
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400
        else:
            dob = None

        student = Student(
            name=data.get('name').strip(),
            email=email,
            phone=data.get('phone', '').strip() or None,
            date_of_birth=dob,
            parent_id=parent_id,
            status='active'
        )
        db.session.add(student)
        db.session.commit()

        return jsonify({
            'message': 'Student registered',
            'student_id': student.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/classes', methods=['GET'])
@jwt_required()
def get_classes():
    """Get all unique class day/time combinations"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    # Get unique class day/time combinations
    classes = db.session.query(
        Student.class_day,
        Student.class_time
    ).distinct().filter(
        Student.class_day.isnot(None),
        Student.class_time.isnot(None)
    ).all()

    return jsonify([{
        'day': c[0],
        'time': c[1]
    } for c in classes]), 200

@students_bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    """Update student info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Authorization check
    if user.role != 'admin':
        parent = Parent.query.filter_by(user_id=user_id).first()
        if not parent or student.parent_id != parent.id:
            return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    try:
        if 'name' in data:
            student.name = data['name']
        if 'email' in data:
            student.email = data['email']
        if 'phone' in data:
            student.phone = data['phone']
        if 'date_of_birth' in data:
            student.date_of_birth = data['date_of_birth']
        if 'class_day' in data:
            student.class_day = data['class_day']
        if 'class_time' in data:
            student.class_time = data['class_time']
        if 'status' in data and user.role == 'admin':
            student.status = data['status']

        db.session.commit()
        return jsonify({'message': 'Student updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    """Delete a student (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
