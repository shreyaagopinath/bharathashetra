from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import PhotoAlbum, Photo, User

photos_bp = Blueprint('photos', __name__)

@photos_bp.route('/albums', methods=['GET'])
@jwt_required()
def get_albums():
    """Get all public albums"""
    try:
        albums = PhotoAlbum.query.filter_by(is_public=True).all()
        result = []
        for a in albums:
            result.append({
                'id': a.id,
                'title': str(a.title) if a.title else '',
                'description': str(a.description) if a.description else '',
                'cover_photo_url': a.cover_photo_url,
                'created_at': str(a.created_at),
                'photo_count': len(a.photos)
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/albums/<int:album_id>/photos', methods=['GET'])
@jwt_required()
def get_album_photos(album_id):
    """Get all photos in an album - METADATA ONLY (not full photo data)"""
    try:
        album = PhotoAlbum.query.get(album_id)
        if not album or not album.is_public:
            return jsonify({'error': 'Album not found'}), 404

        photos = Photo.query.filter_by(album_id=album_id).order_by(Photo.order).all()

        # Return ONLY metadata, not the huge photo_url data
        photo_list = []
        for p in photos:
            photo_list.append({
                'id': p.id,
                'caption': str(p.caption) if p.caption else '',
                'uploaded_at': str(p.uploaded_at)
                # NOTE: NOT including photo_url here - it's too large!
            })

        response = {
            'album': {
                'id': album.id,
                'title': str(album.title),
                'description': str(album.description) if album.description else ''
            },
            'photos': photo_list
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/albums/<int:album_id>/photos/<int:photo_id>', methods=['GET'])
@jwt_required()
def get_photo(album_id, photo_id):
    """Get individual photo with full data"""
    try:
        photo = Photo.query.get(photo_id)
        if not photo or photo.album_id != album_id:
            return jsonify({'error': 'Photo not found'}), 404

        album = PhotoAlbum.query.get(album_id)
        if not album or not album.is_public:
            return jsonify({'error': 'Album not found'}), 404

        return jsonify({
            'id': photo.id,
            'photo_url': str(photo.photo_url) if photo.photo_url else '',
            'caption': str(photo.caption) if photo.caption else '',
            'uploaded_at': str(photo.uploaded_at)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/albums', methods=['POST'])
@jwt_required()
def create_album():
    """Create a new album (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()

        album = PhotoAlbum(
            title=data.get('title'),
            description=data.get('description'),
            created_by=user_id,
            is_public=True
        )
        db.session.add(album)
        db.session.commit()

        return jsonify({
            'message': 'Album created',
            'album_id': album.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/albums/<int:album_id>/photos', methods=['POST'])
@jwt_required()
def add_photo(album_id):
    """Add a photo to album (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        album = PhotoAlbum.query.get(album_id)
        if not album:
            return jsonify({'error': 'Album not found'}), 404

        data = request.get_json()

        photo = Photo(
            album_id=album_id,
            photo_url=data.get('photo_url'),
            caption=data.get('caption'),
            order=len(album.photos)
        )
        db.session.add(photo)
        db.session.commit()

        return jsonify({
            'message': 'Photo added',
            'photo_id': photo.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/albums/<int:album_id>', methods=['DELETE'])
@jwt_required()
def delete_album(album_id):
    """Delete an album (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        album = PhotoAlbum.query.get(album_id)
        if not album:
            return jsonify({'error': 'Album not found'}), 404

        db.session.delete(album)
        db.session.commit()
        return jsonify({'message': 'Album deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@photos_bp.route('/photos/<int:photo_id>', methods=['DELETE'])
@jwt_required()
def delete_photo(photo_id):
    """Delete a photo (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        photo = Photo.query.get(photo_id)
        if not photo:
            return jsonify({'error': 'Photo not found'}), 404

        db.session.delete(photo)
        db.session.commit()
        return jsonify({'message': 'Photo deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
