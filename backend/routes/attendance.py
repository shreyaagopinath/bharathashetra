from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Attendance, ClassSession, Enrollment, User, DanceClass
from datetime import datetime, date as date_cls

attendance_bp = Blueprint('attendance', __name__)


def resolve_session(class_day=None, class_time=None, session_date=None):
    """Find or create the ClassSession that an attendance record belongs to.

    The frontend used to send a hardcoded session_id of 1, which never existed.
    SQLite doesn't enforce foreign keys by default so the bad reference was
    silently accepted; Postgres does enforce them, producing
    'attendance_session_id_fkey' violations. Attendance is now anchored to a
    real (class, date) session that we create on demand.
    """
    if session_date is None:
        session_date = date_cls.today()
    if isinstance(session_date, str):
        try:
            session_date = datetime.strptime(session_date[:10], '%Y-%m-%d').date()
        except ValueError:
            session_date = date_cls.today()

    label = f"{class_day or 'General'} {class_time or ''}".strip()

    dance_class = DanceClass.query.filter_by(name=label).first()
    if not dance_class:
        dance_class = DanceClass(name=label, schedule=label)
        db.session.add(dance_class)
        db.session.flush()

    day_start = datetime.combine(session_date, datetime.min.time())
    day_end = datetime.combine(session_date, datetime.max.time())

    session = ClassSession.query.filter(
        ClassSession.class_id == dance_class.id,
        ClassSession.session_date >= day_start,
        ClassSession.session_date <= day_end
    ).first()

    if not session:
        session = ClassSession(class_id=dance_class.id, session_date=day_start)
        db.session.add(session)
        db.session.flush()

    return session

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

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Parents can only view their own child's attendance
    if user.role == 'parent':
        if student.parent_email != user.email and student.email != user.email:
            return jsonify({'error': 'Unauthorized'}), 403

    records = (Attendance.query
               .filter_by(student_id=student_id)
               .order_by(Attendance.marked_at.desc())
               .all())

    # Include the session's class date so the parent view can show when the
    # class actually happened, not just when the admin tapped the button.
    session_dates = {}
    session_ids = {a.session_id for a in records if a.session_id}
    if session_ids:
        for s in ClassSession.query.filter(ClassSession.id.in_(session_ids)).all():
            session_dates[s.id] = s.session_date

    return jsonify({
        'student_id': student_id,
        'student_name': student.name,
        'class_day': student.class_day,
        'class_time': student.class_time,
        'attendance': [{
            'id': a.id,
            'session_id': a.session_id,
            'status': a.status,
            'date': (session_dates.get(a.session_id).isoformat()
                     if session_dates.get(a.session_id) else
                     (a.marked_at.isoformat() if a.marked_at else None)),
            'marked_at': a.marked_at.isoformat() if a.marked_at else None
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

        # Resolve a REAL session. Accept an explicit session_id only if it
        # actually exists; otherwise derive one from the class day/time/date.
        session = None
        raw_session_id = data.get('session_id')
        if raw_session_id:
            session = ClassSession.query.get(raw_session_id)

        if session is None:
            session = resolve_session(
                class_day=data.get('class_day') or student.class_day,
                class_time=data.get('class_time') or student.class_time,
                session_date=data.get('date')
            )

        # Check for existing record
        existing = Attendance.query.filter_by(
            student_id=data.get('student_id'),
            session_id=session.id
        ).first()

        if existing:
            existing.status = data.get('status', 'present')
            db.session.commit()
            return jsonify({
                'message': 'Attendance updated',
                'attendance_id': existing.id,
                'session_id': session.id
            }), 200

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
            session_id=session.id,
            status=data.get('status', 'present')
        )
        db.session.add(attendance)
        db.session.commit()

        return jsonify({
            'message': 'Attendance marked',
            'attendance_id': attendance.id,
            'session_id': session.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
