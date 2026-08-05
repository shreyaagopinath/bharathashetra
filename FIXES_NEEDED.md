# Bharathashetra - Remaining Issues & Fixes

## CRITICAL ISSUES

### 1. Logout Not Working
**File:** `frontend/index.html`
**Issue:** Logout button doesn't clear localStorage or redirect
**Fix needed:** 
```javascript
function logout() {
  localStorage.removeItem('authToken');
  localStorage.removeItem('userId');
  localStorage.removeItem('userRole');
  window.location.href = '/login.html';
}
```

### 2. Register Button Not Working
**File:** `frontend/index.html` (registrations tab)
**Issue:** Registration form doesn't submit to backend
**Fix needed:** Add proper form submission to POST /api/students endpoint

### 3. Photo Upload Too Slow
**Issue:** Base64 encoding large images
**Fix needed:** Use multipart/form-data instead of base64 data URLs

### 4. Global Font Sizes Too Small
**File:** `frontend/index.html`
**Current sizes:**
- body: 16px
- .pgt: 20px
- .fl: 12px
- .fi: 16px

**Fix needed:** Increase all by 20-30%:
- body: 18px
- .pgt: 24px
- .fl: 14px
- .fi: 18px

---

## CODE AUDIT - POTENTIAL ERRORS

### Backend Issues

1. **Date Parsing** ✓ FIXED
   - Students endpoint now converts date strings to Python date objects

2. **SQLAlchemy Query Syntax** ✓ FIXED  
   - All routes use .query() instead of select()

3. **Missing Error Handling**
   - Many routes missing try/except blocks
   - Need error logging for debugging

4. **No Input Validation**
   - Email validation missing
   - Phone number format not checked
   - Student name required but not enforced

5. **Database Migrations**
   - No migration system
   - Schema changes require manual database reset

### Frontend Issues

1. **Service Worker Errors**
   - Clone errors (partially fixed)
   - Some API calls still uncached

2. **Missing Null Checks**
   - payments.map assumes array (partially fixed)
   - students.find could return undefined

3. **Hardcoded URLs**
   - API URLs hardcoded as https://bharathashetra.onrender.com
   - Should use config variable for flexibility

4. **No Loading States**
   - Users don't know when API calls are pending
   - No spinners or "Loading..." text

5. **Error Messages**
   - Generic error toast, not specific to issue
   - Users don't know what went wrong

---

## RECOMMENDED FIXES (Priority Order)

1. **Logout function** - 5 minutes
2. **Global font sizes** - 5 minutes  
3. **Register endpoint** - 10 minutes
4. **Input validation** - 15 minutes
5. **Loading states** - 20 minutes
6. **Error handling refactor** - 30 minutes
7. **Photo upload optimization** - 20 minutes

Total estimated time: 1.5 hours for all remaining issues
