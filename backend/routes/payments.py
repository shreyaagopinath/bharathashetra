from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Payment, Student, User, Setting
from datetime import datetime
import uuid
import json

payments_bp = Blueprint('payments', __name__)

def calculate_late_fee(payment_date, month_paid_for):
    """Calculate if late fee applies"""
    # Parse month (format: "2024-10")
    year, month = map(int, month_paid_for.split('-'))
    due_day = 10

    # Check if payment date is after the 10th of that month
    if payment_date.day > due_day:
        # Get late fee amount from settings (default $10)
        late_fee_setting = Setting.query.filter_by(key='late_fee_amount').first()
        late_fee = 10.0
        if late_fee_setting:
            try:
                late_fee = float(late_fee_setting.value)
            except:
                late_fee = 10.0
        return late_fee
    return 0.0

@payments_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_payments(student_id):
    """Get payment history for a student"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ['admin', 'parent']:
        return jsonify({'error': 'Unauthorized'}), 403

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.payment_date.desc()).all()
    return jsonify({
        'student_id': student_id,
        'payments': [{
            'id': p.id,
            'amount': p.amount,
            'late_fee_applied': p.late_fee_applied,
            'total_amount': p.amount + p.late_fee_applied,
            'payment_date': p.payment_date.isoformat(),
            'payment_method': p.payment_method,
            'status': p.status,
            'month_paid_for': p.month_paid_for,
            'notes': p.notes
        } for p in payments]
    }), 200

@payments_bp.route('/student/<int:student_id>/current-month', methods=['GET'])
@jwt_required()
def get_current_month_payment(student_id):
    """Check if student has paid for current month"""
    from datetime import date

    current_date = date.today()
    current_month = f"{current_date.year}-{current_date.month:02d}"

    payment = Payment.query.filter_by(
        student_id=student_id,
        month_paid_for=current_month
    ).first()

    days_until_due = 10 - current_date.day
    is_overdue = current_date.day > 10

    return jsonify({
        'student_id': student_id,
        'month': current_month,
        'paid': payment is not None,
        'days_until_due': max(0, days_until_due),
        'is_overdue': is_overdue,
        'payment': {
            'amount': payment.amount,
            'late_fee': payment.late_fee_applied,
            'total': payment.amount + payment.late_fee_applied,
            'payment_date': payment.payment_date.isoformat(),
            'payment_method': payment.payment_method
        } if payment else None
    }), 200

@payments_bp.route('', methods=['POST'])
@jwt_required()
def record_payment():
    """Record a payment with automatic late fee calculation"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    payment_date = datetime.fromisoformat(data.get('payment_date', datetime.utcnow().isoformat()))

    try:
        from datetime import date
        # Default to current month if not specified
        month_paid_for = data.get('month_paid_for', f"{date.today().year}-{date.today().month:02d}")
        late_fee = calculate_late_fee(payment_date, month_paid_for)

        payment = Payment(
            student_id=data.get('student_id'),
            amount=data.get('amount'),
            payment_method=data.get('payment_method'),  # zelle, cash, card
            transaction_id=str(uuid.uuid4()),
            status='completed',
            month_paid_for=month_paid_for,
            late_fee_applied=late_fee,
            notes=data.get('notes', '')
        )
        payment.payment_date = payment_date
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            'message': 'Payment recorded',
            'payment_id': payment.id,
            'amount': payment.amount,
            'late_fee_applied': late_fee,
            'total_amount': payment.amount + late_fee,
            'transaction_id': payment.transaction_id,
            'month_paid_for': month_paid_for
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/overdue', methods=['GET'])
@jwt_required()
def get_overdue_payments():
    """Admin sees all overdue payments"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    from datetime import date
    current_date = date.today()
    current_month = f"{current_date.year}-{current_date.month:02d}"

    all_students = Student.query.all()
    overdue_list = []

    for student in all_students:
        payment = Payment.query.filter_by(
            student_id=student.id,
            month_paid_for=current_month
        ).first()

        if (not payment or payment.status != 'completed') and current_date.day > 10:
            overdue_list.append({
                'student_id': student.id,
                'student_name': student.name,
                'parent_email': student.parent_email,
                'class_day': student.class_day,
                'class_time': student.class_time,
                'days_overdue': current_date.day - 10
            })

    return jsonify({
        'count': len(overdue_list),
        'overdue_students': overdue_list
    }), 200

@payments_bp.route('/mark-paid', methods=['POST'])
@jwt_required()
def mark_payment_paid():
    """Admin marks a student's payment as received"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    student_id = data.get('student_id')
    amount = data.get('amount', 50)
    payment_method = data.get('payment_method', 'cash')
    notes = data.get('notes', '')

    if not student_id:
        return jsonify({'error': 'student_id required'}), 400

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    try:
        from datetime import datetime, date
        current_month = f"{date.today().year}-{date.today().month:02d}"

        existing = Payment.query.filter_by(
            student_id=student_id,
            month_paid_for=current_month
        ).first()

        if existing:
            existing.amount = amount
            existing.payment_date = datetime.utcnow()
            existing.payment_method = payment_method
            existing.status = 'completed'
            existing.late_fee_applied = 0
            existing.notes = notes
        else:
            payment = Payment(
                student_id=student_id,
                amount=amount,
                payment_date=datetime.utcnow(),
                payment_method=payment_method,
                month_paid_for=current_month,
                status='completed',
                late_fee_applied=0,
                notes=notes
            )
            db.session.add(payment)

        db.session.commit()
        return jsonify({
            'message': f'Payment recorded for {student.name}',
            'student_id': student_id,
            'month_paid_for': current_month,
            'paid': True
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    if user.role not in ['admin', 'parent']:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'id': payment.id,
        'student_id': payment.student_id,
        'amount': payment.amount,
        'late_fee_applied': payment.late_fee_applied,
        'total_amount': payment.amount + payment.late_fee_applied,
        'payment_date': payment.payment_date.isoformat(),
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'status': payment.status,
        'month_paid_for': payment.month_paid_for,
        'notes': payment.notes
    }), 200

@payments_bp.route('/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(payment_id):
    """Delete a payment (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    try:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message': 'Payment deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
