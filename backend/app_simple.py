"""Minimal working Flask backend"""
from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

app = Flask(__name__)
CORS(app)

# Simple in-memory database
users = {
    'admin@dance.local': {
        'password_hash': generate_password_hash('Admin123!'),
        'role': 'admin',
        'id': 1
    }
}

SECRET_KEY = 'dev-secret-key'

# Serve frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route('/')
@app.route('/index.html')
def serve_index():
    return send_file(os.path.join(FRONTEND_DIR, 'index.html'))

@app.route('/login.html')
def serve_login():
    return send_file(os.path.join(FRONTEND_DIR, 'login.html'))

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_file(os.path.join(FRONTEND_DIR, path))
    except:
        return {'error': 'Not found'}, 404

# API Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'error': 'Email and password required'}, 400

    user = users.get(email)
    if not user or not check_password_hash(user['password_hash'], password):
        return {'error': 'Invalid email or password'}, 401

    # Create simple JWT token
    token = jwt.encode(
        {'id': user['id'], 'email': email, 'exp': datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY,
        algorithm='HS256'
    )

    return {
        'access_token': token,
        'user_id': user['id'],
        'role': user['role']
    }, 200

@app.route('/api/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    print("Starting minimal backend...")
    print(f"Frontend dir: {FRONTEND_DIR}")
    print(f"Frontend exists: {os.path.isdir(FRONTEND_DIR)}")
    print("Running on http://localhost:8000")
    app.run(debug=True, port=8000, host='0.0.0.0')
