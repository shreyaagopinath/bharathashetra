# Phase 2 Implementation Plan
## Payments + Attendance + Student Lookup

---

## Feature 1: Payments Management

### Admin Features
- View all students and their payment status for current month
- Mark student as "Paid" (Zelle/Cash/Check)
- View payment history for each student
- Set late fee amount (admin settings)
- See which students are overdue

### Parent Features
- See current month payment status (Paid/Not Paid/Overdue)
- View full payment history
- See if late fee applies

### Data Model
```
Payment
  - student_id (foreign key)
  - amount (e.g., $50)
  - payment_date
  - payment_method (Zelle, Cash, Check)
  - month_paid_for (2025-01 format)
  - late_fee_applied
  - status (completed, pending)
  - notes (optional admin notes)
```

### Backend Endpoints Needed
1. `GET /api/payments/student/<id>` - Get student's payment history
2. `GET /api/payments/student/<id>/current-month` - Get current month status
3. `POST /api/payments/mark-paid` - Admin marks payment as received
4. `GET /api/payments/overdue` - Admin sees all overdue payments
5. `GET /api/settings/late-fee` - Get late fee amount

### Key Logic
- Current month = today's month
- Payment due date = 10th of month
- If today > 10th and not paid → overdue
- Late fee applies if overdue
- Admin can manually override dates/amounts

---

## Feature 2: Attendance Tracking

### Admin Features
- Select a class (by day/time)
- See list of enrolled students
- Click "Present" or "Absent" for each student
- Mark attendance for past or future sessions
- View attendance history/reports

### Parent Features
- View their student's attendance record
- See % present vs absent
- See recent class attendance

### Data Model
```
ClassSession
  - class_id (dance class)
  - session_date
  - notes (optional)

Attendance
  - student_id (foreign key)
  - enrollment_id (foreign key)
  - session_id (foreign key to ClassSession)
  - status (present, absent, late)
  - marked_at (when admin marked it)
```

### Backend Endpoints Needed
1. `GET /api/classes` - List all dance classes
2. `GET /api/classes/<id>/sessions` - Get sessions for a class
3. `POST /api/attendance/mark` - Admin marks attendance
4. `GET /api/attendance/student/<id>` - Get student's attendance history
5. `GET /api/attendance/class/<id>/current` - Get current session attendance

### Key Logic
- Each class has multiple sessions (one per class time per week)
- Students marked present/absent per session
- Attendance persists in database
- Admin can edit past attendance records

---

## Feature 3: Student Lookup

### Admin Features
- Filter students by:
  - Class day (Monday, Tuesday, etc.)
  - Class time (3:00 PM, 4:00 PM, etc.)
- Quick view: student name, parent email, payment status
- Click to see full details

### Parent Features
- See their own student's class info
- See other students in same class (optional)

### Data Model
Uses existing Student model:
```
Student
  - first_name
  - last_name
  - class_day (Monday, Tuesday, etc.)
  - class_time (3:00 PM, 4:00 PM, etc.)
  - parent_email
  - phone
  - status (active, inactive)
```

### Backend Endpoints Needed
1. `GET /api/students` - List all students (with filters)
2. `GET /api/students/by-day/<day>` - Filter by class day
3. `GET /api/students/by-time/<time>` - Filter by class time
4. `GET /api/students/<id>` - Get single student details
5. `GET /api/students/search?name=<name>` - Search by name

### Key Logic
- Filter by day and time together
- Quick lookup from admin dashboard
- Show payment status inline
- Show attendance % inline

---

## Database Changes

### New Tables
None needed - Payment and Attendance models already exist in models.py

### Updates to Existing Models
May need to add:
- `Enrollment` model if not tracking which class each student takes
- Or use `class_day` + `class_time` to infer enrollment

### No Migrations Needed
Since this is Phase 1→2 and using SQLite, just restart backend.

---

## Frontend Changes

### New Tabs (in index.html)
1. **Payments Tab** - Admin: mark payments; Parent: view status
2. **Attendance Tab** - Admin: mark attendance; Parent: view record
3. **Student Lookup Tab** - Admin: filter/search students

### Existing Tabs to Keep
- Announcements
- Videos (Phase 3)
- Settings
- Admin/Parent toggle

### Frontend Structure
```
Admin Dashboard:
  - Payments → Mark paid, view history, see overdue
  - Attendance → Select class, mark present/absent
  - Student Lookup → Filter by day/time
  - Announcements
  - Settings

Parent Portal:
  - My Info → Student details, class info
  - Payments → See status, payment history
  - Attendance → View record
  - Announcements
```

---

## Implementation Order

### Step 1: Backend Setup (30 min)
- Add payment endpoints
- Add attendance endpoints
- Add student lookup endpoints
- Add settings endpoint for late fee

### Step 2: Admin Frontend (45 min)
- Payments tab (mark paid, view history)
- Attendance tab (mark attendance)
- Student Lookup tab (filter/search)

### Step 3: Parent Frontend (30 min)
- Display payment status
- Display attendance record
- Display student info

### Step 4: Testing (30 min)
- Test all endpoints
- Test admin workflows
- Test parent views
- Test data persistence

### Step 5: Documentation (15 min)
- Create testing guide
- Create setup instructions

---

## API Endpoint Summary

### Payments
```
GET /api/payments/student/<id>
GET /api/payments/student/<id>/current-month
POST /api/payments/mark-paid
GET /api/payments/overdue
GET /api/settings/late-fee
PUT /api/settings/late-fee
```

### Attendance
```
GET /api/classes
GET /api/classes/<id>/sessions
POST /api/attendance/mark
GET /api/attendance/student/<id>
GET /api/attendance/class/<id>/current
```

### Student Lookup
```
GET /api/students
GET /api/students/<id>
GET /api/students/by-day/<day>
GET /api/students/by-time/<time>
GET /api/students/search?name=<name>
```

---

## Testing Checklist

- [ ] Admin can see all students
- [ ] Admin can filter students by day
- [ ] Admin can filter students by time
- [ ] Admin can mark student as paid
- [ ] Payment status shows correctly to parent
- [ ] Payment history displays correctly
- [ ] Admin can select class and mark attendance
- [ ] Attendance marks persist in database
- [ ] Parent can see their attendance record
- [ ] Overdue payments show for admin
- [ ] Late fees calculate correctly
- [ ] No CORS errors
- [ ] No 404 errors for endpoints
- [ ] Persistent login still works
- [ ] Admin/parent toggle works

---

## Success Criteria

Phase 2 is complete when:
- ✓ Admin can manage payments for all students
- ✓ Admin can track attendance
- ✓ Admin can quickly find students by class
- ✓ Parents see their payment status
- ✓ Parents see their attendance record
- ✓ All data persists in database
- ✓ No errors in browser console
- ✓ All workflows tested end-to-end

---

## Notes

- Late fee default: $10 (configurable by admin)
- Payment due date: 10th of each month (configurable)
- Attendance sessions created on-demand (admin creates when marking)
- Phone numbers stored but not required for Phase 2
- Email reminders for unpaid (Phase 3)
