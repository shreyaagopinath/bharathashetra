from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Announcement, User
from datetime import datetime

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('', methods=['GET'])
def get_announcements():
    """Get all active announcements (sorted by priority and date)"""
    announcements = Announcement.query.filter_by(is_active=True)\
        .order_by(Announcement.priority.desc(), Announcement.created_at.desc()).all()

    return jsonify([{
        'id': a.id,
        'title': a.title,
        'content': a.content,
        'created_at': a.created_at.isoformat(),
        'priority': a.priority
    } for a in announcements]), 200

@announcements_bp.route('/<int:announcement_id>', methods=['GET'])
def get_announcement(announcement_id):
    """Get specific announcement"""
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404

    return jsonify({
        'id': announcement.id,
        'title': announcement.title,
        'content': announcement.content,
        'created_at': announcement.created_at.isoformat(),
        'priority': announcement.priority,
        'is_active': announcement.is_active
    }), 200

@announcements_bp.route('', methods=['POST'])
@jwt_required()
def create_announcement():
    """Create new announcement (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()

    try:
        announcement = Announcement(
            title=data.get('title'),
            content=data.get('content'),
            created_by=user_id,
            priority=data.get('priority', 0),
            is_active=True
        )
        db.session.add(announcement)
        db.session.commit()

        return jsonify({
            'message': 'Announcement created',
            'announcement_id': announcement.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@announcements_bp.route('/<int:announcement_id>', methods=['PUT'])
@jwt_required()
def update_announcement(announcement_id):
    """Update announcement (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404

    data = request.get_json()

    try:
        if 'title' in data:
            announcement.title = data['title']
        if 'content' in data:
            announcement.content = data['content']
        if 'priority' in data:
            announcement.priority = data['priority']
        if 'is_active' in data:
            announcement.is_active = data['is_active']

        announcement.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Announcement updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@announcements_bp.route('/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(announcement_id):
    """Delete announcement (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404

    try:
        db.session.delete(announcement)
        db.session.commit()
        return jsonify({'message': 'Announcement deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
