# Phase 2 Quick Start

## What's New

Phase 2 adds three major features:
1. **Payments** - Track paid/unpaid, late fees, payment history
2. **Attendance** - Mark present/absent for classes
3. **Student Lookup** - Filter students by day/time/name

---

## Backend Setup

### Step 1: Restart Backend

The code is already updated. Just restart:

```bash
# In your backend terminal
Ctrl+C  (stop the old one)

cd ~/Desktop/bharathashetra-app/backend
python3 app_phase1.py
```

You should see the same startup message with all blueprints registered.

### Step 2: Verify Endpoints Work

Open a new terminal and test:

```bash
# Get all students
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/students

# Get students by class day
curl -H "Authorization: Bearer YOUR_TOKEN" "http://localhost:8000/api/students?class_day=Monday"

# Get current month payment status for student 1
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/payments/student/1/current-month

# Get attendance for student 1
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/attendance/student/1
```

---

## Frontend Usage

### For Admins

**Student Lookup Tab:**
- Click by class day (Monday, Tuesday, etc.)
- Click by class time (3:00 PM, 4:00 PM, etc.)
- Search by student name
- See all students organized by class

**Payments Tab:**
- View all students + payment status
- Click "Mark Paid" to record payment
- Choose payment method: Cash, Zelle, Check
- View payment history

**Attendance Tab:**
- Select class by day/time
- See enrolled students
- Click "Present" or "Absent" for each
- Mark attendance for past/future classes

### For Parents

**My Info Tab:**
- See your student's class (day, time)
- Contact information

**Payments Tab:**
- Current month status (Paid/Unpaid/Overdue)
- Days until payment due
- Payment history (all months)
- Amount due including late fees

**Attendance Tab:**
- View your student's attendance record
- See % present vs absent

---

## Backend Endpoints Implemented

### Payments
```
GET /api/payments/student/<id>
    → Get student's payment history

GET /api/payments/student/<id>/current-month
    → Get current month payment status

POST /api/payments
    → Admin records a payment
    → Body: {student_id, amount, payment_method, month_paid_for, notes}

GET /api/payments/overdue
    → Admin sees all overdue payments
```

### Attendance
```
GET /api/attendance/student/<id>
    → Get student's attendance history

POST /api/attendance
    → Admin marks attendance
    → Body: {student_id, session_id, status: "present"|"absent"}

GET /api/attendance/session/<id>
    → Get attendance for a specific class session
```

### Students (Enhanced)
```
GET /api/students
    → Get all students with optional filters
    → Query params: ?class_day=Monday&class_time=3:00%20PM&search=John

GET /api/students/<id>
    → Get single student details

POST /api/students
    → Create new student (admin or parent)

PUT /api/students/<id>
    → Update student info
```

---

## How to Test Phase 2

### Test 1: Student Lookup

1. Login as admin
2. Check browser console (F12)
3. Run:
```javascript
fetch('http://localhost:8000/api/students?class_day=Monday', {
  headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
})
.then(r => r.json())
.then(d => console.log(d))
```

Expected: See all Monday students

### Test 2: Payment Status

```javascript
fetch('http://localhost:8000/api/payments/student/1/current-month', {
  headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
})
.then(r => r.json())
.then(d => console.log(d))
```

Expected: Shows if student paid for current month

### Test 3: Record Payment

```javascript
fetch('http://localhost:8000/api/payments', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('authToken'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    student_id: 1,
    amount: 50,
    payment_method: 'cash',
    month_paid_for: '2025-08',
    notes: 'Paid in person'
  })
})
.then(r => r.json())
.then(d => console.log(d))
```

Expected: Payment recorded successfully

### Test 4: Mark Attendance

```javascript
fetch('http://localhost:8000/api/attendance', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('authToken'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    student_id: 1,
    session_id: 1,
    status: 'present'
  })
})
.then(r => r.json())
.then(d => console.log(d))
```

Expected: Attendance marked successfully

---

## Next Steps

1. **Restart backend** with updated code
2. **Test endpoints** using console commands above
3. **Check for errors** in backend terminal and browser console
4. **Then:** Build frontend UI tabs (Payments, Attendance, Student Lookup)

---

## Database Note

No database migration needed. Phase 2 uses existing Payment and Attendance models.

All data automatically persists in SQLite database at:
```
~/Desktop/bharathashetra-app/backend/bharathashetra.db
```

