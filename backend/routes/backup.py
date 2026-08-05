from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import BackupLog, User
from datetime import datetime
import os
import shutil

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_backup_logs():
    """Get backup history (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    logs = BackupLog.query.order_by(BackupLog.backup_date.desc()).limit(20).all()

    return jsonify([{
        'id': log.id,
        'backup_date': log.backup_date.isoformat(),
        'backup_size': log.backup_size,
        'status': log.status,
        'notes': log.notes
    } for log in logs]), 200

@backup_bp.route('/create', methods=['POST'])
@jwt_required()
def create_backup():
    """Create manual backup (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        # Create backups directory if it doesn't exist
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Create backup filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.db')

        # Copy database file
        db_file = 'bharathashetra.db'
        if os.path.exists(db_file):
            shutil.copy2(db_file, backup_file)
            backup_size = os.path.getsize(backup_file)
            backup_size_mb = f"{backup_size / (1024*1024):.2f} MB"
        else:
            backup_size_mb = "Unknown"

        # Log backup
        log = BackupLog(
            backup_file=backup_file,
            backup_size=backup_size_mb,
            status='success',
            notes='Manual backup created'
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'message': 'Backup created successfully',
            'backup_file': backup_file,
            'backup_size': backup_size_mb
        }), 201
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500

@backup_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_backup_stats():
    """Get backup statistics (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    total_backups = BackupLog.query.count()
    successful_backups = BackupLog.query.filter_by(status='success').count()
    last_backup = BackupLog.query.order_by(BackupLog.backup_date.desc()).first()

    return jsonify({
        'total_backups': total_backups,
        'successful_backups': successful_backups,
        'last_backup_date': last_backup.backup_date.isoformat() if last_backup else None,
        'last_backup_size': last_backup.backup_size if last_backup else None
    }), 200
