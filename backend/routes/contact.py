from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import ContactMessage, User
from datetime import datetime

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/public-inquiry', methods=['POST'])
def public_inquiry():
    """Inquiry from the public website - no login required.

    Lands in the same admin Messages tab as parent messages, prefixed so it's
    obvious it came from a stranger rather than an enrolled family.
    """
    data = request.get_json() or {}

    # Honeypot: a hidden field real users never see or fill. Bots fill every
    # input, so anything here is spam. Return 201 so the bot thinks it worked.
    if (data.get('website') or '').strip():
        return jsonify({'message': 'Thank you for your message'}), 201

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()
    phone = (data.get('phone') or '').strip()
    location = (data.get('location') or '').strip()

    if not name or not email or not message:
        return jsonify({'error': 'Name, email, and message are required'}), 400
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Please enter a valid email address'}), 400

    # Bound the sizes so a bad actor can't write huge rows
    if len(name) > 120 or len(email) > 120 or len(message) > 5000:
        return jsonify({'error': 'Submission is too long'}), 400

    header = []
    if phone:
        header.append(f"Phone: {phone}")
    if location:
        header.append(f"Preferred studio: {location}")
    body = ("\n".join(header) + "\n\n" + message) if header else message

    subject = f'Website inquiry — {location}' if location else 'Website inquiry'

    try:
        db.session.add(ContactMessage(
            parent_name=name,
            parent_email=email,
            subject=subject[:200],
            message=body
        ))
        db.session.commit()
        return jsonify({'message': 'Thank you - we will be in touch soon.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Could not send message. Please try again.'}), 500


@contact_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    """Parent sends a message to admin"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.get_json()

    try:
        message = ContactMessage(
            parent_name=data.get('parent_name'),
            parent_email=data.get('parent_email'),
            subject=data.get('subject'),
            message=data.get('message')
        )
        db.session.add(message)
        db.session.commit()

        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    """Get all messages (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify([{
        'id': m.id,
        'parent_name': m.parent_name,
        'parent_email': m.parent_email,
        'subject': m.subject,
        'message': m.message,
        'created_at': m.created_at.isoformat(),
        'is_read': m.is_read,
        'response': m.response,
        'responded_at': m.responded_at.isoformat() if m.responded_at else None
    } for m in messages]), 200

@contact_bp.route('/messages/<int:message_id>', methods=['PATCH'])
@jwt_required()
def update_message(message_id):
    """Update message read status (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    message = ContactMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    data = request.get_json()

    try:
        if 'is_read' in data:
            message.is_read = data.get('is_read')
        db.session.commit()
        return jsonify({'message': 'Message updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(message_id):
    """Mark message as read (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    message = ContactMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    try:
        message.is_read = True
        db.session.commit()
        return jsonify({'message': 'Marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/messages/<int:message_id>/respond', methods=['PUT'])
@jwt_required()
def respond_message(message_id):
    """Admin responds to a message"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    message = ContactMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    data = request.get_json()

    try:
        message.response = data.get('response')
        message.responded_at = datetime.utcnow()
        message.is_read = True
        db.session.commit()
        return jsonify({'message': 'Response saved'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete a message (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    message = ContactMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    try:
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': 'Message deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
