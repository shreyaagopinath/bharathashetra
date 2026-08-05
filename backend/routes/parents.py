from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Parent, User

parents_bp = Blueprint('parents', __name__)

@parents_bp.route('/<int:parent_id>', methods=['GET'])
@jwt_required()
def get_parent(parent_id):
    """Get parent info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    if user.role != 'admin' and parent.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'id': parent.id,
        'name': parent.name,
        'phone': parent.phone,
        'address': parent.address,
        'students': [{'id': s.id, 'name': s.name} for s in parent.students]
    }), 200

@parents_bp.route('/<int:parent_id>', methods=['PUT'])
@jwt_required()
def update_parent(parent_id):
    """Update parent info"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    parent = Parent.query.get(parent_id)
    if not parent:
        return jsonify({'error': 'Parent not found'}), 404

    if user.role != 'admin' and parent.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    try:
        if 'name' in data:
            parent.name = data['name']
        if 'phone' in data:
            parent.phone = data['phone']
        if 'address' in data:
            parent.address = data['address']

        db.session.commit()
        return jsonify({'message': 'Parent updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
