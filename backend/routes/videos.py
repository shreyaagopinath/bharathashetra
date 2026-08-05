from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Video, User

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('', methods=['GET'])
@jwt_required()
def get_videos():
    """Get all public videos"""
    videos = Video.query.filter_by(visibility='public').all()
    return jsonify([{
        'id': v.id,
        'title': v.title,
        'description': v.description,
        'class_id': v.class_id,
        'instructor': v.instructor,
        'duration': v.duration,
        'uploaded_at': v.uploaded_at.isoformat()
    } for v in videos]), 200

@videos_bp.route('/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Get video details"""
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404

    # Check visibility
    if video.visibility == 'private':
        return jsonify({'error': 'Video is private'}), 403

    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'class_id': video.class_id,
        'video_url': video.video_url,
        'instructor': video.instructor,
        'duration': video.duration,
        'visibility': video.visibility,
        'uploaded_at': video.uploaded_at.isoformat()
    }), 200

@videos_bp.route('', methods=['POST'])
@jwt_required()
def upload_video():
    """Upload a new video (admin/instructor only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()

    try:
        video = Video(
            title=data.get('title'),
            description=data.get('description'),
            class_id=data.get('class_id'),
            video_url=data.get('video_url'),
            instructor=data.get('instructor'),
            duration=data.get('duration'),
            visibility=data.get('visibility', 'members-only')
        )
        db.session.add(video)
        db.session.commit()

        return jsonify({
            'message': 'Video uploaded',
            'video_id': video.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/<int:video_id>', methods=['PUT'])
@jwt_required()
def update_video(video_id):
    """Update video info (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404

    data = request.get_json()

    try:
        if 'title' in data:
            video.title = data['title']
        if 'description' in data:
            video.description = data['description']
        if 'visibility' in data:
            video.visibility = data['visibility']
        if 'video_url' in data:
            video.video_url = data['video_url']

        db.session.commit()
        return jsonify({'message': 'Video updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
