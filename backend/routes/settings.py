from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Setting, User
import json

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('', methods=['GET'])
def get_settings():
    """Get all settings (public - no auth needed)"""
    settings = Setting.query.all()

    result = {}
    for setting in settings:
        try:
            result[setting.key] = json.loads(setting.value)
        except:
            result[setting.key] = setting.value

    return jsonify(result), 200

@settings_bp.route('/<key>', methods=['GET'])
def get_setting(key):
    """Get specific setting"""
    setting = Setting.query.filter_by(key=key).first()

    if not setting:
        return jsonify({'error': 'Setting not found'}), 404

    try:
        value = json.loads(setting.value)
    except:
        value = setting.value

    return jsonify({'key': setting.key, 'value': value}), 200

@settings_bp.route('/<key>', methods=['POST', 'PUT'])
@jwt_required()
def update_setting(key):
    """Update or create setting (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    value = data.get('value')

    try:
        setting = Setting.query.filter_by(key=key).first()

        if setting:
            setting.value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            setting.category = data.get('category', setting.category)
        else:
            setting = Setting(
                key=key,
                value=json.dumps(value) if isinstance(value, (dict, list)) else str(value),
                category=data.get('category', 'general')
            )
            db.session.add(setting)

        db.session.commit()
        return jsonify({'message': 'Setting updated', 'key': key}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('', methods=['POST'])
@settings_bp.route('', methods=['PUT'])
@jwt_required()
def update_multiple_settings():
    """Update multiple settings at once (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()  # Should be dict of {key: value}

    try:
        for key, value in data.items():
            setting = Setting.query.filter_by(key=key).first()

            if setting:
                setting.value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            else:
                setting = Setting(
                    key=key,
                    value=json.dumps(value) if isinstance(value, (dict, list)) else str(value),
                    category='general'
                )
                db.session.add(setting)

        db.session.commit()
        return jsonify({'message': 'Settings updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
