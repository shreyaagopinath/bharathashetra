"""
CSV Import Route - Import students from CSV
Supports both formats:
1. New format: First Name, Last Name, Parent Email, Class Day, Class Time, Parent PIN
2. Existing format: Student Name, Parent Email, Class Day, Phone Number (PIN = last 4 digits of phone)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import User, Student, Parent
import csv
import io
import re

import_bp = Blueprint('import', __name__)

def extract_phone_digits(phone):
    """Extract last 4 digits from phone number"""
    digits = re.sub(r'\D', '', phone)  # Remove all non-digits
    return digits[-4:] if len(digits) >= 4 else None

def split_name(full_name):
    """Split 'First Last' into separate parts"""
    parts = full_name.strip().split(None, 1)  # Split on first space
    first_name = parts[0] if len(parts) > 0 else ''
    last_name = parts[1] if len(parts) > 1 else ''
    return first_name, last_name

@import_bp.route('/students/import-csv', methods=['POST'])
@jwt_required()
def import_students_csv():
    """
    Import students from CSV file
    Admin only

    Supports two formats:

    Format 1 (New):
    First Name, Last Name, Parent Email, Class Day, Class Time, Parent PIN, Phone Number (optional)

    Format 2 (Existing):
    Student Name, Parent Email, Class Day, Phone Number
    (Phone number last 4 digits used as PIN)
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return {'error': 'Admin access required'}, 403

    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']
    if not file or file.filename == '':
        return {'error': 'No file selected'}, 400

    if not file.filename.endswith('.csv'):
        return {'error': 'File must be CSV format'}, 400

    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
        csv_reader = csv.DictReader(stream)

        # Detect which format
        headers = csv_reader.fieldnames
        is_new_format = 'First Name' in headers
        is_existing_format = 'Student Name' in headers

        imported_count = 0
        errors = []
        created_pins = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                if is_new_format:
                    # ===== NEW FORMAT =====
                    first_name = row.get('First Name', '').strip()
                    last_name = row.get('Last Name', '').strip()
                    parent_email = row.get('Parent Email', '').strip()
                    class_day = row.get('Class Day', '').strip()
                    class_time = row.get('Class Time', '').strip()
                    parent_pin = row.get('Parent PIN', '').strip()
                    phone = row.get('Phone Number', '').strip()  # Optional

                    if not all([first_name, last_name, parent_email, parent_pin]):
                        errors.append(f"Row {row_num}: Missing required fields (First Name, Last Name, Parent Email, Parent PIN)")
                        continue

                    if len(parent_pin) != 4 or not parent_pin.isdigit():
                        errors.append(f"Row {row_num}: PIN must be 4 digits")
                        continue

                elif is_existing_format:
                    # ===== EXISTING FORMAT =====
                    student_name = row.get('Student Name', '').strip()
                    parent_email = row.get('Parent Email', '').strip()
                    class_day = row.get('Class Day', '').strip()
                    phone = row.get('Phone Number', '').strip()
                    class_time = row.get('Class Time', '').strip()  # Optional

                    if not all([student_name, parent_email, class_day, phone]):
                        errors.append(f"Row {row_num}: Missing required fields (Student Name, Parent Email, Class Day, Phone Number)")
                        continue

                    # Extract last 4 digits of phone as PIN
                    parent_pin = extract_phone_digits(phone)
                    if not parent_pin or len(parent_pin) != 4:
                        errors.append(f"Row {row_num}: Phone number must have at least 4 digits")
                        continue

                    # Split student name into first and last
                    first_name, last_name = split_name(student_name)
                    if not first_name:
                        errors.append(f"Row {row_num}: Could not parse student name")
                        continue

                    created_pins.append({
                        'student': student_name,
                        'email': parent_email,
                        'pin': parent_pin
                    })
                else:
                    errors.append(f"Row {row_num}: CSV format not recognized. Use either 'First Name' or 'Student Name' columns.")
                    continue

                # ===== COMMON LOGIC FOR BOTH FORMATS =====
                # Validate email format
                if '@' not in parent_email:
                    errors.append(f"Row {row_num}: Invalid email format")
                    continue

                # Check if student already exists
                existing = db.session.query(Student).filter_by(
                    parent_email=parent_email,
                    first_name=first_name
                ).first()

                if existing:
                    # Update existing student
                    existing.last_name = last_name
                    existing.class_day = class_day
                    if class_time:
                        existing.class_time = class_time
                    existing.parent_pin = parent_pin
                    existing.name = f"{first_name} {last_name}"
                    if phone:
                        existing.phone = phone
                else:
                    # Create new student
                    student = Student(
                        first_name=first_name,
                        last_name=last_name,
                        name=f"{first_name} {last_name}",
                        parent_email=parent_email,
                        class_day=class_day,
                        class_time=class_time if class_time else None,
                        parent_pin=parent_pin,
                        phone=phone if phone else None
                    )
                    db.session.add(student)

                imported_count += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

        # Commit all changes
        db.session.commit()

        response = {
            'message': f'Imported {imported_count} students',
            'imported_count': imported_count,
            'errors': errors if errors else None
        }

        # If using existing format, include PIN mapping so admin can share with parents
        if created_pins and imported_count > 0:
            response['pin_assignments'] = created_pins
            response['note'] = 'PINs generated from phone numbers. Share with parents.'

        return response, 200

    except Exception as e:
        db.session.rollback()
        return {'error': f'CSV import failed: {str(e)}'}, 500
