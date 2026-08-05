from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Attendance, ClassSession, Enrollment, User
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session_attendance(session_id):
    """Get attendance for a specific session"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    session = ClassSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    records = Attendance.query.filter_by(session_id=session_id).all()
    return jsonify({
        'session_id': session_id,
        'session_date': session.session_date.isoformat(),
        'attendance': [{
            'id': a.id,
            'student_id': a.student_id,
            'status': a.status,
            'marked_at': a.marked_at.isoformat()
        } for a in records]
    }), 200

@attendance_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    """Get attendance records for a student"""
    from models import Student
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ['admin', 'parent']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Parents can only view their own child's attendance
    if user.role == 'parent':
        student = Student.query.get(student_id)
        if not student or student.parent_email != user.email:
            return jsonify({'error': 'Unauthorized'}), 403

    records = Attendance.query.filter_by(student_id=student_id).all()

    return jsonify({
        'student_id': student_id,
        'attendance': [{
            'id': a.id,
            'session_id': a.session_id,
            'status': a.status,
            'marked_at': a.marked_at.isoformat()
        } for a in records]
    }), 200

@attendance_bp.route('', methods=['POST'])
@jwt_required()
def mark_attendance():
    """Mark attendance for a student in a session"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()

    try:
        from models import Student

        # Verify student exists
        student = Student.query.get(data.get('student_id'))
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        # Check for existing record
        existing = Attendance.query.filter_by(
            student_id=data.get('student_id'),
            session_id=data.get('session_id')
        ).first()

        if existing:
            existing.status = data.get('status', 'present')
            db.session.commit()
            return jsonify({'message': 'Attendance updated', 'attendance_id': existing.id}), 200

        # Try to get enrollment, but don't require it
        enrollment_id = None
        enrollment = Enrollment.query.filter_by(
            student_id=data.get('student_id')
        ).first()
        if enrollment:
            enrollment_id = enrollment.id

        attendance = Attendance(
            enrollment_id=enrollment_id,
            student_id=data.get('student_id'),
            session_id=data.get('session_id'),
            status=data.get('status', 'present')
        )
        db.session.add(attendance)
        db.session.commit()

        return jsonify({
            'message': 'Attendance marked',
            'attendance_id': attendance.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
