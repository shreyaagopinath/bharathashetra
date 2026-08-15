# Phase 1 Quick Start

## Backend Setup

### 1. Verify file structure
```
/backend/
  ├── extensions.py      ✓ (created)
  ├── models.py          ✓ (updated with Phase 1 fields)
  ├── app_phase1.py      ✓ (created - NEW)
  ├── routes/
  │   ├── auth_v2.py     ✓ (created - NEW)
  │   └── import_csv.py  ✓ (created - NEW)
  └── app_simple.py      (old version, ignore)
```

### 2. Start backend on port 8000
```bash
# Terminal 1
cd ~/Desktop/bharathashetra-app/backend
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

No errors = backend ready ✓

### 3. Test backend is running
```bash
# Terminal 2 - in a new terminal tab
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "ok", "phase": "phase-1"}
```

## Frontend Setup

### 1. Use new login page
Replace the old login.html with the new one:
```bash
# Option A: Copy the login_phase1.html we created
cp ~/Desktop/bharathashetra-app/frontend/login_phase1.html ~/Desktop/bharathashetra-app/frontend/login.html

# Option B: If you prefer to rename it back:
# In the browser, navigate to: http://localhost:8000/login_phase1.html
```

### 2. Update index.html (if needed)
The current index.html already checks `Auth.isAuthenticated()` on line 661, which is correct.
No changes needed.

### 3. Check auth.js
The existing `js/auth.js` already has `isAuthenticated()` method.
No changes needed.

## Test the System

### Test 1: Admin Login
1. Open browser: `http://localhost:8000/login.html`
2. Click "Admin" tab
3. Enter:
   - Email: `admin@dance.local`
   - Password: `Admin123!`
4. Click "Admin Sign In"
5. Expected: Redirected to portal with admin controls visible

### Test 2: Check localStorage
Open DevTools (F12) → Application → Storage → localStorage
Should see:
- `authToken`: (JWT value, very long string)
- `userId`: (number)
- `userRole`: `admin`

### Test 3: Refresh to test persistent login
Press F5 to refresh the page
Expected: Still logged in (redirects back to index.html, not login.html)

### Test 4: Admin CSV Import
1. Stay logged in as admin
2. Go to "Student Management" section (or equivalent)
3. Create a test CSV file:
```
First Name,Last Name,Parent Email,Class Day,Class Time,Parent PIN
Arjun,Sharma,arjun@example.com,Monday,3:00 PM,1234
Priya,Patel,priya@example.com,Wednesday,4:00 PM,5678
```
4. Upload the CSV
5. Expected: "Imported 2 students" message

### Test 5: Parent Login
1. Logout (click Logout button)
2. Click "Parent Login" tab
3. Enter:
   - Email: `arjun@example.com` (from CSV)
   - PIN: `1234` (from CSV)
4. Click "Sign In"
5. Expected: Redirected to portal with parent view (not admin controls)

### Test 6: Parent Persistent Login
1. Refresh page (F5) - should stay logged in as parent
2. Close browser tab
3. Reopen the URL: `http://localhost:8000`
4. Expected: Auto-redirects to index.html, stays logged in

## Troubleshooting

### "Failed to fetch" error
- [ ] Backend not running on port 8000
- [ ] Check terminal 1: `python3 app_phase1.py` is still running
- [ ] Check firewall/ports: `lsof -i :8000`

### "Invalid email or PIN" for parent login
- [ ] CSV might not have imported correctly
- [ ] Check admin student list to see if students were created
- [ ] Try with default test data first

### "Database tables not created"
- [ ] Stop backend (Ctrl+C)
- [ ] Delete database: `rm ~/Desktop/bharathashetra-app/backend/bharathashetra.db`
- [ ] Restart backend: `python3 app_phase1.py`

### "Unauthorized" error on page load
- [ ] Your localStorage token might be expired
- [ ] Clear localStorage and login again
- [ ] In DevTools: `localStorage.clear()` then refresh

## Key API Endpoints

For reference (you shouldn't need to manually call these):

**Health Check**
```
GET http://localhost:8000/api/health
```

**Parent Login**
```
POST http://localhost:8000/api/auth/parent-login
Content-Type: application/json
{
  "email": "parent@example.com",
  "pin": "1234"
}
```

**Admin Login**
```
POST http://localhost:8000/api/auth/admin-login
Content-Type: application/json
{
  "email": "admin@dance.local",
  "password": "Admin123!"
}
```

**CSV Import (admin only)**
```
POST http://localhost:8000/api/students/import-csv
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
(file: CSV file)
```

## Files Changed/Created This Session

**Created:**
- `app_phase1.py` - Main Flask app (USE THIS, not app_simple.py)
- `routes/auth_v2.py` - Authentication endpoints
- `routes/import_csv.py` - CSV import endpoint
- `frontend/login_phase1.html` - New login page (rename to login.html)
- `extensions.py` - Already existed, verified correct

**Updated:**
- `models.py` - Already has required Phase 1 fields

**Existing (no changes):**
- `index.html` - Already checks Auth.isAuthenticated()
- `js/auth.js` - Already has correct methods
- `js/config.js` - Should have API_CONFIG pointing to localhost:8000/api
- `js/api.js` - Should send JWT in headers

## Important Notes

1. **Always use `app_phase1.py`**, not `app_simple.py`
2. **Backend must run on port 8000** for frontend to reach it
3. **Default admin credentials**: `admin@dance.local` / `Admin123!`
4. **Tokens expire in 30 days** - after that, user must login again
5. **CSV Import upserts** - if student exists (by email + first name), updates; otherwise creates new

## Next: Full Test Checklist

Open `PHASE_1_TESTING_GUIDE.md` and run through the complete testing steps listed there.
