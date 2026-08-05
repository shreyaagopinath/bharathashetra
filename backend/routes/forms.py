from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Form, FormField, FormResponse, User
from datetime import datetime

forms_bp = Blueprint('forms', __name__)

@forms_bp.route('', methods=['GET'])
def get_forms():
    """Get all forms"""
    forms = Form.query.all()
    return jsonify([{
        'id': f.id,
        'title': f.title,
        'description': f.description,
        'form_type': f.form_type,
        'field_count': len(f.fields)
    } for f in forms]), 200

@forms_bp.route('/<int:form_id>', methods=['GET'])
def get_form(form_id):
    """Get form with all fields"""
    form = Form.query.get(form_id)
    if not form:
        return jsonify({'error': 'Form not found'}), 404

    return jsonify({
        'id': form.id,
        'title': form.title,
        'description': form.description,
        'form_type': form.form_type,
        'fields': [{
            'id': f.id,
            'field_name': f.field_name,
            'field_type': f.field_type,
            'required': f.required,
            'order': f.order
        } for f in sorted(form.fields, key=lambda x: x.order or 0)]
    }), 200

@forms_bp.route('', methods=['POST'])
@jwt_required()
def create_form():
    """Create a new form (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()

    try:
        form = Form(
            title=data.get('title'),
            description=data.get('description'),
            form_type=data.get('form_type')
        )
        db.session.add(form)
        db.session.flush()

        # Add fields
        for idx, field_data in enumerate(data.get('fields', [])):
            field = FormField(
                form_id=form.id,
                field_name=field_data.get('field_name'),
                field_type=field_data.get('field_type'),
                required=field_data.get('required', False),
                order=idx
            )
            db.session.add(field)

        db.session.commit()
        return jsonify({
            'message': 'Form created',
            'form_id': form.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms_bp.route('/<int:form_id>/submit', methods=['POST'])
def submit_form(form_id):
    """Submit a form response"""
    data = request.get_json()

    form = Form.query.get(form_id)
    if not form:
        return jsonify({'error': 'Form not found'}), 404

    try:
        response = FormResponse(
            form_id=form_id,
            student_id=data.get('student_id'),
            parent_id=data.get('parent_id'),
            response_data=data.get('response_data', {})
        )
        db.session.add(response)
        db.session.commit()

        return jsonify({
            'message': 'Form submitted',
            'response_id': response.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms_bp.route('/<int:form_id>/responses', methods=['GET'])
@jwt_required()
def get_form_responses(form_id):
    """Get all responses for a form (admin only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    form = Form.query.get(form_id)
    if not form:
        return jsonify({'error': 'Form not found'}), 404

    responses = FormResponse.query.filter_by(form_id=form_id).all()
    return jsonify({
        'form_id': form_id,
        'total_responses': len(responses),
        'responses': [{
            'id': r.id,
            'student_id': r.student_id,
            'parent_id': r.parent_id,
            'response_data': r.response_data,
            'submitted_at': r.submitted_at.isoformat()
        } for r in responses]
    }), 200
