# Bharathashetra Phase 1 - Testing & Setup Guide

## Overview
Phase 1 implements:
1. SQLite database with SQLAlchemy ORM
2. Parent login via email + 4-digit PIN
3. Admin login via email + password
4. CSV bulk import of students
5. Persistent login (30-day JWT tokens)
6. Role-based access control

## Code Architecture Review

### Backend Files
- `extensions.py` - SQLAlchemy & JWT initialization (prevents circular imports)
- `models.py` - Database models (User, Student, Parent, etc.)
- `app_phase1.py` - Flask app factory with all configurations
- `routes/auth_v2.py` - Parent PIN login + Admin password login endpoints
- `routes/import_csv.py` - CSV import endpoint for bulk student creation

### Frontend Files
- `login_phase1.html` - New login page with Parent/Admin mode toggle
  - Parents log in with email + 4-digit PIN
  - Admins log in with email + password
  - Both store JWT in localStorage for persistent login
- `index.html` - Main portal (already checks `Auth.isAuthenticated()` on load)
- `js/auth.js` - Contains Auth class with login/logout/isAuthenticated methods

### Key Logic Points to Verify

#### 1. Database Initialization (app_phase1.py)
```python
✓ SQLite database created at: /backend/bharathashetra.db
✓ Tables created: users, students, parents, etc.
✓ Default admin created: admin@dance.local / Admin123!
✓ Flask runs on port 8000
✓ CORS enabled for all origins
✓ JWT configured for 30-day expiration
```

#### 2. Parent Login (auth_v2.py)
```
Flow:
1. Parent enters email + 4-digit PIN on login_phase1.html
2. POST /api/auth/parent-login with {email, pin}
3. Backend finds Student by parent_email AND parent_pin
4. Creates/updates User record with role='parent'
5. Returns JWT token + user_id + role
6. Frontend stores token in localStorage
7. Token automatically sent in headers for all API requests
```

**Critical Logic:**
- PIN must be exactly 4 digits
- Student lookup: `parent_email` + `parent_pin` must match
- User created on first login if doesn't exist
- Returns error if email/PIN invalid

#### 3. Admin Login (auth_v2.py)
```
Flow:
1. Admin enters email + password on login_phase1.html
2. POST /api/auth/admin-login with {email, password}
3. Backend finds User by email AND role='admin'
4. Validates password hash
5. Returns JWT token + user_id + role
6. Frontend stores token in localStorage
```

**Critical Logic:**
- Password validation via `check_password()` (werkzeug)
- User must have role='admin'
- Returns error if email/password invalid

#### 4. CSV Import (import_csv.py)
```
Flow:
1. Admin selects CSV file on admin dashboard
2. POST /api/students/import-csv with file
3. Backend validates JWT (admin only)
4. Parses CSV with columns:
   - First Name, Last Name, Parent Email, Class Day, Class Time, Parent PIN
5. For each row:
   - PIN must be exactly 4 digits
   - Check if student exists (by parent_email + first_name)
   - If exists: UPDATE
   - If new: INSERT
6. Return success count + error list
```

**Critical Logic:**
- Admin-only endpoint (checks JWT claims['role'] == 'admin')
- CSV headers must match exactly (case-sensitive)
- PIN validation: must be 4 digits
- Upsert logic: update if exists, create if new
- All errors caught and reported, not blocking

#### 5. Persistent Login
```
Flow:
1. User logs in → JWT stored in localStorage via login_phase1.html
2. JWT expiration: 30 days
3. User closes browser/refreshes page
4. index.html loads → calls Auth.isAuthenticated()
5. Auth.isAuthenticated() checks localStorage for token
6. If token exists → redirects to portal (index.html)
7. If no token → redirects to login (login.html)
```

**Critical Logic:**
- Token persists across browser refresh
- Token persists across browser close/reopen
- All API requests include JWT in Authorization header
- If token expires (30 days), user must login again

## Pre-Flight Checklist

Before testing, verify these files exist and are correct:

### Backend
- [ ] `/backend/extensions.py` - Has `db = SQLAlchemy()` and `jwt = JWTManager()`
- [ ] `/backend/models.py` - Student model has: first_name, last_name, parent_email, parent_pin, class_day, class_time
- [ ] `/backend/app_phase1.py` - Imports from extensions, creates default admin, runs on port 8000
- [ ] `/backend/routes/auth_v2.py` - Has parent-login & admin-login endpoints
- [ ] `/backend/routes/import_csv.py` - Has students/import-csv endpoint

### Frontend
- [ ] `/frontend/login_phase1.html` - Has parent form (email + PIN) and admin form (email + password)
- [ ] `/frontend/index.html` - Line 661 checks `Auth.isAuthenticated()`
- [ ] `/frontend/js/auth.js` - Has `isAuthenticated()`, `login()`, `logout()` methods

## Testing Steps

### Step 1: Start Backend
```bash
cd /backend
python3 app_phase1.py
```
Expected output:
```
============================================================
BHARATHASHETRA BACKEND - PHASE 1
============================================================
Database: /backend/bharathashetra.db
Frontend: /frontend
Port: 8000
============================================================
```

Check that:
- [ ] No errors during startup
- [ ] Database file created: `ls -la /backend/bharathashetra.db`
- [ ] Tables created: Check with SQLite browser or Python

### Step 2: Test Admin Login
1. Open browser: `http://localhost:8000/login_phase1.html`
2. Click "Admin" tab
3. Enter:
   - Email: `admin@dance.local`
   - Password: `Admin123!`
4. Click "Admin Sign In"

Expected:
- [ ] No errors in browser console
- [ ] Redirects to index.html
- [ ] Admin portal appears (student management section visible)
- [ ] localStorage has: authToken, userId, userRole='admin'

### Step 3: Test Persistent Login
1. Refresh the page (F5)
   Expected: [ ] Still logged in, portal still visible
2. Close browser tab and reopen
   Expected: [ ] Still logged in (token in localStorage)
3. Open browser DevTools > Application > localStorage
   Expected: [ ] See `authToken` with JWT value

### Step 4: Test Parent Login
1. First, create test student data via CSV import (Step 5)
2. Logout from admin account (button in header)
3. Go to `http://localhost:8000/login_phase1.html`
4. Click "Parent Login" tab
5. Enter:
   - Email: (from CSV import)
   - PIN: (from CSV import, e.g., "1234")
6. Click "Sign In"

Expected:
- [ ] Redirects to index.html
- [ ] Parent portal appears (different from admin)
- [ ] localStorage has: authToken, userId, userRole='parent'

### Step 5: Test CSV Import
1. Login as admin
2. Create test CSV file with content:
```
First Name,Last Name,Parent Email,Class Day,Class Time,Parent PIN
Arjun,Sharma,arjun.parent@email.com,Monday,3:00 PM,1234
Priya,Patel,priya.parent@email.com,Wednesday,4:00 PM,5678
```
3. Save as `test_students.csv`
4. In admin dashboard, find "Import Students" section
5. Upload the CSV file
6. Click Import

Expected:
- [ ] Success message: "Imported 2 students"
- [ ] No errors shown
- [ ] Students appear in student list
- [ ] Each student has correct class_day, class_time, parent_pin

### Step 6: Test Login Errors
1. Try parent login with wrong PIN
   Expected: [ ] Error message: "Invalid email or PIN"
2. Try admin login with wrong password
   Expected: [ ] Error message: "Invalid email or password"
3. Try parent login with non-existent email
   Expected: [ ] Error message: "Invalid email or PIN"

## Troubleshooting

### "Database tables not created"
Check:
- [ ] extensions.py imported correctly
- [ ] models.py imported in app_phase1.py
- [ ] db.create_all() called in app context
- [ ] No circular imports

Fix: Delete `bharathashetra.db` and restart backend

### "Login endpoint not found / 404"
Check:
- [ ] auth_v2.py in `/routes/` directory
- [ ] Blueprint registered in app_phase1.py: `register_blueprint(auth_bp, url_prefix='/api/auth')`
- [ ] Route decorators correct: `@auth_bp.route('/parent-login', methods=['POST'])`

### "CORS error when calling API"
Check:
- [ ] app_phase1.py has: `CORS(app, resources={r"/*": {"origins": "*"}})`
- [ ] Backend running on port 8000
- [ ] Frontend accessing: `http://localhost:8000/api/...`

### "Token not persisting across refresh"
Check:
- [ ] localStorage has `authToken` key after login
- [ ] login_phase1.html calls: `localStorage.setItem('authToken', data.access_token)`
- [ ] auth.js getAuthToken() reads from localStorage

### "Admin setup creates duplicate admins"
Fix in app_phase1.py - should only create admin if none exists:
```python
admin_exists = db.session.query(User).filter_by(role='admin').first()
if not admin_exists:
    # create admin
```

## Success Criteria

Phase 1 is complete when ALL of these pass:
- [ ] Backend starts without errors
- [ ] Default admin can login
- [ ] Admin can import CSV with students
- [ ] Parent can login with email + PIN from CSV
- [ ] Persistent login works (refresh & close/reopen)
- [ ] Wrong credentials show appropriate error
- [ ] Admin panel visible for admins only
- [ ] Parent panel visible for parents only
- [ ] No CORS errors
- [ ] No "Unauthorized" errors
- [ ] localStorage has authToken, userId, userRole after login
- [ ] All routes return proper JSON responses

## Next Steps (Phase 2+)

Once Phase 1 passes all tests:
1. Update google sheets integration
2. Add attendance tracking
3. Add payment management
4. Add photos/albums
5. Add video content (Stage Ready, etc.)
6. Add forms & auto-population
7. Add FAQ section
8. Add email reminders
