from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import DanceClass, User, Enrollment

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('', methods=['GET'])
def get_classes():
    """Get all available classes"""
    classes = DanceClass.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'style': c.style,
        'level': c.level,
        'instructor': c.instructor,
        'schedule': c.schedule,
        'capacity': c.capacity,
        'fees': c.fees,
        'description': c.description
    } for c in classes]), 200

@classes_bp.route('/<int:class_id>', methods=['GET'])
def get_class(class_id):
    """Get specific class info"""
    dance_class = DanceClass.query.get(class_id)
    if not dance_class:
        return jsonify({'error': 'Class not found'}), 404

    return jsonify({
        'id': dance_class.id,
        'name': dance_class.name,
        'style': dance_class.style,
        'level': dance_class.level,
        'instructor': dance_class.instructor,
        'schedule': dance_class.schedule,
        'capacity': dance_class.capacity,
        'fees': dance_class.fees,
        'description': dance_class.description,
        'enrolled_students': len(dance_class.enrollments)
    }), 200

@classes_bp.route('', methods=['POST'])
@jwt_required()
def create_class():
    """Create a new class (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()

    try:
        dance_class = DanceClass(
            name=data.get('name'),
            style=data.get('style'),
            level=data.get('level'),
            instructor=data.get('instructor'),
            schedule=data.get('schedule'),
            capacity=data.get('capacity'),
            fees=data.get('fees'),
            description=data.get('description')
        )
        db.session.add(dance_class)
        db.session.commit()

        return jsonify({
            'message': 'Class created',
            'class_id': dance_class.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@classes_bp.route('/<int:class_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_student(class_id):
    """Enroll a student in a class"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ['admin', 'parent']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'Student ID required'}), 400

    dance_class = DanceClass.query.get(class_id)
    if not dance_class:
        return jsonify({'error': 'Class not found'}), 404

    existing_enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        class_id=class_id,
        status='active'
    ).first()

    if existing_enrollment:
        return jsonify({'error': 'Student already enrolled'}), 409

    try:
        enrollment = Enrollment(
            student_id=student_id,
            class_id=class_id,
            status='active'
        )
        db.session.add(enrollment)
        db.session.commit()

        return jsonify({
            'message': 'Student enrolled',
            'enrollment_id': enrollment.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
