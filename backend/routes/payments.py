from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Payment, Student, User, Setting
from datetime import datetime
import uuid
import json

payments_bp = Blueprint('payments', __name__)

DEFAULT_MONTHLY_RATE = 80.0
DEFAULT_RECITAL_FEE = 100.0

# Recital fees are stored as Payment rows with month_paid_for set to
# "recital-<year>" instead of "YYYY-MM". Everything parent-facing filters on a
# real calendar month, so recital records are invisible there and never affect
# a family's balance. RECITAL_PREFIX is the single source of truth for that.
RECITAL_PREFIX = 'recital-'


def recital_season(year=None):
    from datetime import date
    return f"{RECITAL_PREFIX}{year or date.today().year}"


def is_recital_key(month_paid_for):
    return bool(month_paid_for) and str(month_paid_for).startswith(RECITAL_PREFIX)


def get_recital_fee():
    """Recital fee per student. Editable in admin Settings."""
    setting = Setting.query.filter_by(key='recital_fee').first()
    if setting:
        try:
            return float(setting.value)
        except (TypeError, ValueError):
            pass
    return DEFAULT_RECITAL_FEE


def get_monthly_rate():
    """Monthly tuition per child. Editable in admin Settings."""
    setting = Setting.query.filter_by(key='monthly_rate').first()
    if setting:
        try:
            return float(setting.value)
        except (TypeError, ValueError):
            pass
    return DEFAULT_MONTHLY_RATE


@payments_bp.route('/rate', methods=['GET'])
@jwt_required()
def get_rate():
    """Current monthly rate per child (any signed-in user)."""
    return jsonify({'monthly_rate': get_monthly_rate()}), 200


@payments_bp.route('/rate', methods=['PUT'])
@jwt_required()
def set_rate():
    """Admin updates the monthly rate per child."""
    user = User.query.get(get_jwt_identity())
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json() or {}
    try:
        rate = float(data.get('monthly_rate'))
        if rate < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({'error': 'monthly_rate must be a non-negative number'}), 400

    setting = Setting.query.filter_by(key='monthly_rate').first()
    if setting:
        setting.value = str(rate)
    else:
        db.session.add(Setting(key='monthly_rate', value=str(rate)))

    db.session.commit()
    return jsonify({'message': 'Rate updated', 'monthly_rate': rate}), 200

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

@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_all_payments():
    """Payment roster: every student + their payment status for a given month (admin only).

    Returns one row per student so 'unpaid' students appear even with no Payment record.
    Optional query params: month (YYYY-MM), class_day, class_time, status (paid|unpaid).
    """
    from datetime import date

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    today = date.today()
    month = request.args.get('month') or f"{today.year}-{today.month:02d}"

    students = Student.query.order_by(Student.name).all()
    payments = Payment.query.filter_by(month_paid_for=month).all()
    by_student = {p.student_id: p for p in payments}

    PAID_STATES = ('paid', 'completed', 'success', 'succeeded')

    rows = []
    for s in students:
        p = by_student.get(s.id)
        is_paid = bool(p and (p.status or '').lower() in PAID_STATES)
        rows.append({
            'payment_id': p.id if p else None,
            'student_id': s.id,
            'student_name': s.name,
            'parent_email': s.parent_email or s.email,
            'class_day': s.class_day,
            'class_time': s.class_time,
            'month_paid_for': month,
            'amount': (p.amount if p else 0) or 0,
            'late_fee_applied': (p.late_fee_applied if p else 0) or 0,
            'payment_method': p.payment_method if p else None,
            'payment_date': p.payment_date.isoformat() if (p and p.payment_date) else None,
            'raw_status': p.status if p else None,
            'status': 'paid' if is_paid else 'unpaid'
        })

    # Server-side filters (frontend also filters client-side)
    class_day = request.args.get('class_day')
    class_time = request.args.get('class_time')
    status = request.args.get('status')
    if class_day:
        rows = [r for r in rows if r['class_day'] == class_day]
    if class_time:
        rows = [r for r in rows if (r['class_time'] or '').lower() == class_time.lower()]
    if status in ('paid', 'unpaid'):
        rows = [r for r in rows if r['status'] == status]

    return jsonify(rows), 200

@payments_bp.route('/recital/fee', methods=['GET'])
@jwt_required()
def get_recital_fee_route():
    user = User.query.get(get_jwt_identity())
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return jsonify({'recital_fee': get_recital_fee()}), 200


@payments_bp.route('/recital/fee', methods=['PUT'])
@jwt_required()
def set_recital_fee():
    user = User.query.get(get_jwt_identity())
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json() or {}
    try:
        fee = float(data.get('recital_fee'))
        if fee < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({'error': 'recital_fee must be a non-negative number'}), 400

    setting = Setting.query.filter_by(key='recital_fee').first()
    if setting:
        setting.value = str(fee)
    else:
        db.session.add(Setting(key='recital_fee', value=str(fee)))
    db.session.commit()
    return jsonify({'message': 'Recital fee updated', 'recital_fee': fee}), 200


@payments_bp.route('/recital/roster', methods=['GET'])
@jwt_required()
def recital_roster():
    """Every student + recital payment status. Admin only.

    Mirrors the monthly payment roster: one row per student so unpaid students
    appear even with no payment record.
    """
    user = User.query.get(get_jwt_identity())
    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    season = request.args.get('season') or recital_season()
    fee = get_recital_fee()

    students = Student.query.order_by(Student.name).all()
    payments = Payment.query.filter_by(month_paid_for=season).all()
    by_student = {p.student_id: p for p in payments}

    PAID_STATES = ('paid', 'completed', 'success', 'succeeded')

    rows = []
    for s in students:
        p = by_student.get(s.id)
        is_paid = bool(p and (p.status or '').lower() in PAID_STATES)
        rows.append({
            'payment_id': p.id if p else None,
            'student_id': s.id,
            'student_name': s.name,
            'parent_email': s.parent_email or s.email,
            'class_day': s.class_day,
            'class_time': s.class_time,
            'season': season,
            'amount': (p.amount if p else 0) or 0,
            'payment_method': p.payment_method if p else None,
            'payment_date': p.payment_date.isoformat() if (p and p.payment_date) else None,
            'notes': p.notes if p else None,
            'status': 'paid' if is_paid else 'unpaid'
        })

    class_day = request.args.get('class_day')
    class_time = request.args.get('class_time')
    status = request.args.get('status')
    if class_day:
        rows = [r for r in rows if r['class_day'] == class_day]
    if class_time:
        rows = [r for r in rows if (r['class_time'] or '').lower() == class_time.lower()]
    if status in ('paid', 'unpaid'):
        rows = [r for r in rows if r['status'] == status]

    return jsonify({
        'season': season,
        'recital_fee': fee,
        'students': rows
    }), 200


@payments_bp.route('/recital/mark-paid', methods=['POST'])
@jwt_required()
def recital_mark_paid():
    """Record a recital payment. Kept entirely out of monthly tuition."""
    from datetime import datetime as dt

    user = User.query.get(get_jwt_identity())
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json() or {}
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({'error': 'student_id required'}), 400

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    season = data.get('season') or recital_season()
    amount = data.get('amount')
    try:
        amount = float(amount) if amount is not None else get_recital_fee()
    except (TypeError, ValueError):
        return jsonify({'error': 'amount must be a number'}), 400

    try:
        existing = Payment.query.filter_by(student_id=student_id, month_paid_for=season).first()
        if existing:
            existing.amount = amount
            existing.payment_date = dt.utcnow()
            existing.payment_method = data.get('payment_method', 'cash')
            existing.status = 'completed'
            existing.late_fee_applied = 0
            existing.notes = data.get('notes', 'Recital fee')
        else:
            db.session.add(Payment(
                student_id=student_id,
                amount=amount,
                payment_date=dt.utcnow(),
                payment_method=data.get('payment_method', 'cash'),
                month_paid_for=season,
                status='completed',
                late_fee_applied=0,
                notes=data.get('notes', 'Recital fee')
            ))
        db.session.commit()
        return jsonify({
            'message': f'Recital payment recorded for {student.name}',
            'student_id': student_id,
            'season': season,
            'amount': amount
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/recital/<int:student_id>', methods=['DELETE'])
@jwt_required()
def recital_unmark(student_id):
    """Undo a recital payment (admin only)."""
    user = User.query.get(get_jwt_identity())
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    season = request.args.get('season') or recital_season()
    payment = Payment.query.filter_by(student_id=student_id, month_paid_for=season).first()
    if not payment:
        return jsonify({'error': 'No recital payment found'}), 404

    try:
        db.session.delete(payment)
        db.session.commit()
        return jsonify({'message': 'Recital payment removed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/family-summary', methods=['GET'])
@jwt_required()
def family_summary():
    """Every child under the signed-in parent, plus the combined monthly total.

    One parent email can cover several siblings, so the amount owed is
    rate x number of active children.
    """
    from datetime import date
    from flask_jwt_extended import get_jwt

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    claims = get_jwt()
    email = claims.get('email') or user.email

    if user.role == 'admin' and request.args.get('email'):
        email = request.args.get('email')   # admin can preview a family

    students = Student.query.filter_by(parent_email=email).order_by(Student.name).all()
    if not students:
        students = Student.query.filter_by(email=email).order_by(Student.name).all()

    today = date.today()
    month = f"{today.year}-{today.month:02d}"
    rate = get_monthly_rate()
    PAID_STATES = ('paid', 'completed', 'success', 'succeeded')

    children = []
    unpaid_count = 0
    for s in students:
        p = Payment.query.filter_by(student_id=s.id, month_paid_for=month).first()
        is_paid = bool(p and (p.status or '').lower() in PAID_STATES)
        if not is_paid and (s.status or 'active') == 'active':
            unpaid_count += 1
        children.append({
            'id': s.id,
            'name': s.name,
            'class_day': s.class_day,
            'class_time': s.class_time,
            'status': s.status or 'active',
            'paid': is_paid,
            'amount_due': 0 if is_paid else rate,
            'amount_paid': (p.amount if p else 0) or 0,
            'late_fee': (p.late_fee_applied if p else 0) or 0,
            'payment_date': p.payment_date.isoformat() if (p and p.payment_date) else None,
        })

    active = [c for c in children if c['status'] == 'active']
    return jsonify({
        'parent_email': email,
        'month': month,
        'monthly_rate': rate,
        'child_count': len(active),
        'children': children,
        'total_due': round(rate * unpaid_count, 2),
        'total_monthly': round(rate * len(active), 2),
        'all_paid': unpaid_count == 0,
        'days_until_due': max(0, 10 - today.day),
        'is_overdue': today.day > 10 and unpaid_count > 0,
    }), 200


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

    # Exclude recital fees - this feeds the parent's payment history and
    # 12-month tuition grid, where a recital charge would be confusing and
    # would misrepresent what they owe.
    payments = [p for p in Payment.query
                .filter_by(student_id=student_id)
                .order_by(Payment.payment_date.desc())
                .all()
                if not is_recital_key(p.month_paid_for)]

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
