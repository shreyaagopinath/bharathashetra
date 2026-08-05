#!/usr/bin/env python3
"""Test script to verify backend setup"""
import sys
import json

print("=" * 60)
print("TESTING BHARATHASHETRA BACKEND")
print("=" * 60)

# Test 1: Check imports
print("\n[1] Testing imports...")
try:
    from extensions import db, jwt
    print("  ✓ extensions imported")
    from models import User
    print("  ✓ models imported")
    from app import create_app
    print("  ✓ app imported")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create app and initialize database
print("\n[2] Creating app and database...")
try:
    app = create_app()
    print("  ✓ App created successfully")
    print(f"  ✓ Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    sys.exit(1)

# Test 3: Check if admin user exists
print("\n[3] Checking admin user...")
try:
    with app.app_context():
        from sqlalchemy import select
        admin = db.session.execute(select(User).filter_by(email='admin@dance.local')).scalar()
        if admin:
            print("  ✓ Admin user exists")
            print(f"    Email: {admin.email}")
            print(f"    Role: {admin.role}")
        else:
            print("  ✗ Admin user NOT FOUND")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test login endpoint
print("\n[4] Testing login endpoint...")
try:
    with app.test_client() as client:
        # Test GET
        resp = client.get('/test-login')
        print(f"  GET /test-login: {resp.status_code}")
        print(f"    Response: {resp.get_json()}")

        # Test POST with valid credentials
        resp = client.post('/test-login',
            json={'email': 'admin@dance.local', 'password': 'Admin123!'},
            content_type='application/json'
        )
        print(f"  POST /test-login (valid): {resp.status_code}")
        data = resp.get_json()
        if resp.status_code == 200:
            print(f"    ✓ Login successful")
            print(f"    Token: {data.get('access_token')[:20]}...")
            print(f"    User ID: {data.get('user_id')}")
            print(f"    Role: {data.get('role')}")
        else:
            print(f"    ✗ Error: {data}")

        # Test POST with invalid credentials
        resp = client.post('/test-login',
            json={'email': 'admin@dance.local', 'password': 'wrongpassword'},
            content_type='application/json'
        )
        print(f"  POST /test-login (invalid): {resp.status_code}")
        data = resp.get_json()
        print(f"    {data}")

except Exception as e:
    print(f"  ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test CORS headers
print("\n[5] Testing CORS headers...")
try:
    with app.test_client() as client:
        # Test preflight
        resp = client.options('/api/auth/login')
        print(f"  OPTIONS /api/auth/login: {resp.status_code}")
        cors_header = resp.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"    ✓ CORS header present: {cors_header}")
        else:
            print(f"    ✗ CORS header MISSING")
            print(f"    Headers: {dict(resp.headers)}")

        # Test regular request
        resp = client.get('/api/health')
        print(f"  GET /api/health: {resp.status_code}")
        cors_header = resp.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"    ✓ CORS header present: {cors_header}")
        else:
            print(f"    ✗ CORS header MISSING")

except Exception as e:
    print(f"  ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
