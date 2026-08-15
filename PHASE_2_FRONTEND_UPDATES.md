# Phase 2 Frontend Implementation Guide

## Changes Needed

### 1. Add Student Lookup Tab to Admin Nav (Line 483)

Replace:
```html
<nav class="anav" id="adminNav">
  <button class="active" onclick="showSec('pay',this)">💰 Payments</button>
  <button onclick="showSec('att',this)">✓ Attendance</button>
  <button onclick="showSec('reg',this)">📝 Registrations</button>
  <button onclick="showSec('vid',this)">▶ Videos</button>
  <button onclick="showSec('ann',this)">📢 Announcements</button>
  <button onclick="showSec('imp',this)">📥 Import</button>
  <button onclick="showSec('settings',this)">⚙ Settings</button>
</nav>
```

With:
```html
<nav class="anav" id="adminNav">
  <button class="active" onclick="showSec('pay',this)">💰 Payments</button>
  <button onclick="showSec('att',this)">✓ Attendance</button>
  <button onclick="showSec('lookup',this)">🔍 Student Lookup</button>
  <button onclick="showSec('reg',this)">📝 Registrations</button>
  <button onclick="showSec('vid',this)">▶ Videos</button>
  <button onclick="showSec('ann',this)">📢 Announcements</button>
  <button onclick="showSec('imp',this)">📥 Import</button>
  <button onclick="showSec('settings',this)">⚙ Settings</button>
</nav>
```

---

### 2. Update Payments Section (Line 511-529)

Replace the entire `sec-pay` section with:

```html
  <div class="sec active" id="sec-pay">
    <div class="pgh"><div><div class="pgt">Payments</div><div class="pgs">Record and manage student payments</div></div></div>
    <div class="af">
      <div class="aft">+ Record Payment</div>
      <div class="frow">
        <div class="fg"><label class="fl">Student</label><select class="fs" id="payStudent" onchange="updatePaymentStatus()"></select></div>
        <div class="fg"><label class="fl">Amount ($)</label><input class="fi" id="payAmount" type="number" step="0.01" value="50"></div>
      </div>
      <div class="frow">
        <div class="fg"><label class="fl">Method</label><select class="fs" id="payMethod"><option>cash</option><option>zelle</option><option>check</option></select></div>
        <div class="fg"><label class="fl">Notes</label><input class="fi" id="payNotes" placeholder="Optional notes"></div>
      </div>
      <button class="bgld" onclick="markPaymentPaid()">Record Payment</button>
      <div id="paymentStatus" style="margin-top:10px;font-size:13px"></div>
    </div>
    <div class="af" style="margin-top:20px">
      <div class="aft">Overdue Payments</div>
      <div id="overdueList"></div>
    </div>
    <div class="tw">
      <div class="th-row"><div class="th">Student</div><div class="th">Class</div><div class="th">Amount</div><div class="th">Date</div><div class="th">Method</div><div class="th">Status</div></div>
      <div id="payBody"><div class="lds"><div class="spin"></div></div></div>
    </div>
  </div>
```

---

### 3. Add Student Lookup Section (After Registrations, around line 551)

Add this new section:

```html
  <!-- STUDENT LOOKUP -->
  <div class="sec" id="sec-lookup">
    <div class="pgh"><div><div class="pgt">Student Lookup</div><div class="pgs">Find students by class or name</div></div></div>
    <div class="af">
      <div class="aft">Filter Students</div>
      <div class="frow">
        <div class="fg"><label class="fl">Class Day</label>
          <select class="fs" id="filterDay" onchange="filterStudents()">
            <option value="">All Days</option>
            <option>Monday</option>
            <option>Tuesday</option>
            <option>Wednesday</option>
            <option>Thursday</option>
            <option>Friday</option>
            <option>Saturday</option>
          </select>
        </div>
        <div class="fg"><label class="fl">Class Time</label>
          <input class="fi" id="filterTime" placeholder="e.g. 3:00 PM" onchange="filterStudents()">
        </div>
        <div class="fg"><label class="fl">Search Name</label>
          <input class="fi" id="filterName" placeholder="Student name" onchange="filterStudents()">
        </div>
      </div>
    </div>
    <div class="tw">
      <div class="th-row"><div class="th">Name</div><div class="th">Email</div><div class="th">Phone</div><div class="th">Class</div><div class="th">Status</div></div>
      <div id="lookupBody"><div class="lds"><div class="spin"></div></div></div>
    </div>
  </div>
```

---

### 4. Update Attendance Section (Line 570-576)

Replace with:

```html
  <!-- ATTENDANCE -->
  <div class="sec" id="sec-att">
    <div class="pgh"><div><div class="pgt">Attendance</div><div class="pgs">Mark class attendance</div></div></div>
    <div class="af">
      <div class="aft">Select Class to Mark Attendance</div>
      <div class="frow">
        <div class="fg"><label class="fl">Class Day</label>
          <select class="fs" id="attDay" onchange="loadClassStudents()">
            <option value="">Select Day</option>
            <option>Monday</option>
            <option>Tuesday</option>
            <option>Wednesday</option>
            <option>Thursday</option>
            <option>Friday</option>
            <option>Saturday</option>
          </select>
        </div>
        <div class="fg"><label class="fl">Class Time</label>
          <input class="fi" id="attTime" placeholder="e.g. 3:00 PM" onchange="loadClassStudents()">
        </div>
      </div>
    </div>
    <div class="tw" style="margin-top:20px">
      <div class="th-row"><div class="th">Student</div><div class="th">Status</div><div class="th">Action</div></div>
      <div id="attBody"><div style="padding:20px;text-align:center;color:rgba(245,230,192,.4)">Select a class to see students</div></div>
    </div>
  </div>
```

---

### 5. Add Parent Attendance Tab (After Parent Payments, around line 642)

Add this new section:

```html
    <!-- Attendance -->
    <div class="psec" id="psec-att">
      <div class="pgh"><div class="pgt">Attendance Record</div></div>
      <div class="af">
        <div class="aft">Attendance Summary</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:15px;margin:15px 0">
          <div style="background:rgba(76,175,138,0.1);padding:15px;border-radius:8px;border-left:3px solid var(--gn)">
            <div style="font-size:11px;color:rgba(245,230,192,.6);letter-spacing:1px">CLASSES ATTENDED</div>
            <div id="attClasses" style="font-size:24px;color:var(--gn);margin-top:5px">0</div>
          </div>
          <div style="background:rgba(212,96,96,0.1);padding:15px;border-radius:8px;border-left:3px solid var(--rd)">
            <div style="font-size:11px;color:rgba(245,230,192,.6);letter-spacing:1px">CLASSES MISSED</div>
            <div id="attMissed" style="font-size:24px;color:var(--rd);margin-top:5px">0</div>
          </div>
          <div style="background:rgba(232,184,75,0.1);padding:15px;border-radius:8px;border-left:3px solid var(--bgo)">
            <div style="font-size:11px;color:rgba(245,230,192,.6);letter-spacing:1px">ATTENDANCE %</div>
            <div id="attPercent" style="font-size:24px;color:var(--bgo);margin-top:5px">0%</div>
          </div>
        </div>
      </div>
      <div class="tw">
        <div class="th-row"><div class="th">Date</div><div class="th">Class</div><div class="th">Status</div></div>
        <div id="parentAttendance"></div>
      </div>
    </div>
```

---

### 6. Update Parent Nav (Line 620-624)

Replace:
```html
  <nav class="anav" id="parentNav">
    <button class="active" onclick="showParentSec('dash',this)">Dashboard</button>
    <button onclick="showParentSec('pay',this)">Payments</button>
    <button onclick="showParentSec('stage',this)">Stage Ready</button>
  </nav>
```

With:
```html
  <nav class="anav" id="parentNav">
    <button class="active" onclick="showParentSec('dash',this)">Dashboard</button>
    <button onclick="showParentSec('pay',this)">Payments</button>
    <button onclick="showParentSec('att',this)">Attendance</button>
    <button onclick="showParentSec('stage',this)">Stage Ready</button>
  </nav>
```

---

## JavaScript Functions to Add (At end of script section, before closing tags)

Add these functions to handle Phase 2 functionality:

```javascript
// ========================= PHASE 2: PAYMENTS =========================
async function markPaymentPaid() {
  const studentId = document.getElementById('payStudent').value;
  const amount = document.getElementById('payAmount').value;
  const method = document.getElementById('payMethod').value;
  const notes = document.getElementById('payNotes').value;

  if (!studentId || !amount) {
    alert('Select student and amount');
    return;
  }

  try {
    const response = await fetch('http://localhost:8000/api/payments', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('authToken'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        student_id: studentId,
        amount: parseFloat(amount),
        payment_method: method,
        notes: notes
      })
    });

    const data = await response.json();
    if (response.ok) {
      alert('Payment recorded!');
      document.getElementById('payStudent').value = '';
      document.getElementById('payAmount').value = '50';
      document.getElementById('payNotes').value = '';
      loadPaymentData();
    } else {
      alert('Error: ' + data.error);
    }
  } catch (e) {
    console.error('Error:', e);
  }
}

async function updatePaymentStatus() {
  const studentId = document.getElementById('payStudent').value;
  if (!studentId) return;

  try {
    const response = await fetch(`http://localhost:8000/api/payments/student/${studentId}/current-month`, {
      headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
    });
    const data = await response.json();
    
    let statusHtml = '';
    if (data.paid) {
      statusHtml = `<div style="color:var(--gn)">✓ Paid on ${new Date(data.payment.payment_date).toLocaleDateString()}</div>`;
    } else if (data.is_overdue) {
      statusHtml = `<div style="color:var(--rd)">⚠ OVERDUE (${data.days_until_due} days late)</div>`;
    } else {
      statusHtml = `<div style="color:var(--bgo)">Due in ${data.days_until_due} days</div>`;
    }
    document.getElementById('paymentStatus').innerHTML = statusHtml;
  } catch (e) {
    console.error('Error:', e);
  }
}

async function loadPaymentData() {
  try {
    const response = await fetch('http://localhost:8000/api/students', {
      headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
    });
    const students = await response.json();

    // Populate student dropdown
    const select = document.getElementById('payStudent');
    select.innerHTML = '<option value="">Select Student</option>';
    students.forEach(s => {
      select.innerHTML += `<option value="${s.id}">${s.name}</option>`;
    });

    // Load all payments
    let paymentsHtml = '';
    for (const student of students) {
      const payResp = await fetch(`http://localhost:8000/api/payments/student/${student.id}`, {
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
      });
      const payData = await payResp.json();
      
      if (payData.payments && payData.payments.length > 0) {
        payData.payments.slice(0, 5).forEach(p => {
          paymentsHtml += `
            <div class="tr">
              <div class="ctm">${student.name}</div>
              <div class="ctm">$${p.amount}</div>
              <div class="ctm">${new Date(p.payment_date).toLocaleDateString()}</div>
              <div class="ctm">${p.payment_method}</div>
              <div class="ctm">${p.status}</div>
            </div>
          `;
        });
      }
    }
    document.getElementById('payBody').innerHTML = paymentsHtml || '<div class="tr"><div class="ctm">No payments recorded</div></div>';

    // Load overdue payments
    const overdueResp = await fetch('http://localhost:8000/api/payments/overdue', {
      headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
    });
    const overdueData = await overdueResp.json();
    
    let overdueHtml = '';
    if (overdueData.overdue_students && overdueData.overdue_students.length > 0) {
      overdueData.overdue_students.forEach(s => {
        overdueHtml += `
          <div style="padding:10px;background:rgba(212,96,96,0.1);border-radius:5px;margin:8px 0">
            <strong>${s.student_name}</strong> - ${s.class_day} ${s.class_time} (${s.days_overdue} days overdue)
          </div>
        `;
      });
    } else {
      overdueHtml = '<div style="color:rgba(245,230,192,.4)">No overdue payments</div>';
    }
    document.getElementById('overdueList').innerHTML = overdueHtml;
  } catch (e) {
    console.error('Error loading payments:', e);
  }
}

// ========================= PHASE 2: ATTENDANCE =========================
async function loadClassStudents() {
  const day = document.getElementById('attDay').value;
  const time = document.getElementById('attTime').value;

  if (!day) {
    document.getElementById('attBody').innerHTML = '<div style="padding:20px;text-align:center;color:rgba(245,230,192,.4)">Select a class</div>';
    return;
  }

  try {
    let url = `http://localhost:8000/api/students?class_day=${day}`;
    if (time) url += `&class_time=${encodeURIComponent(time)}`;

    const response = await fetch(url, {
      headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
    });
    const students = await response.json();

    let html = '';
    students.forEach(s => {
      html += `
        <div class="tr">
          <div class="ctm">${s.name}</div>
          <div class="ctm">
            <select class="fs" id="status-${s.id}" style="width:100px">
              <option value="present">Present</option>
              <option value="absent">Absent</option>
            </select>
          </div>
          <div class="ctm">
            <button class="bgld" onclick="markAttendance(${s.id})" style="padding:5px 10px;font-size:10px">Mark</button>
          </div>
        </div>
      `;
    });

    if (html === '') {
      html = '<div class="tr"><div class="ctm">No students in this class</div></div>';
    }

    document.getElementById('attBody').innerHTML = html;
  } catch (e) {
    console.error('Error:', e);
  }
}

async function markAttendance(studentId) {
  const status = document.getElementById(`status-${studentId}`).value;
  const day = document.getElementById('attDay').value;
  const time = document.getElementById('attTime').value;

  if (!day) {
    alert('Select class day');
    return;
  }

  try {
    // Create session ID from day+time (simplified for now)
    const sessionId = Date.now();

    const response = await fetch('http://localhost:8000/api/attendance', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('authToken'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        student_id: studentId,
        session_id: sessionId,
        status: status
      })
    });

    const data = await response.json();
    if (response.ok) {
      alert('Attendance marked!');
    } else {
      alert('Error: ' + data.error);
    }
  } catch (e) {
    console.error('Error:', e);
  }
}

// ========================= PHASE 2: STUDENT LOOKUP =========================
async function filterStudents() {
  const day = document.getElementById('filterDay').value;
  const time = document.getElementById('filterTime').value;
  const name = document.getElementById('filterName').value;

  try {
    let url = 'http://localhost:8000/api/students';
    const params = [];
    if (day) params.push(`class_day=${day}`);
    if (time) params.push(`class_time=${encodeURIComponent(time)}`);
    if (name) params.push(`search=${encodeURIComponent(name)}`);
    if (params.length > 0) url += '?' + params.join('&');

    const response = await fetch(url, {
      headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
    });
    const students = await response.json();

    let html = '';
    students.forEach(s => {
      html += `
        <div class="tr">
          <div class="ctm">${s.name}</div>
          <div class="ctm">${s.parent_email || 'N/A'}</div>
          <div class="ctm">${s.phone || 'N/A'}</div>
          <div class="ctm">${s.class_day} ${s.class_time || ''}</div>
          <div class="ctm"><span class="bdg" style="background:var(--gn)">${s.status}</span></div>
        </div>
      `;
    });

    if (html === '') {
      html = '<div class="tr"><div class="ctm">No students found</div></div>';
    }

    document.getElementById('lookupBody').innerHTML = html;
  } catch (e) {
    console.error('Error:', e);
  }
}

// ========================= PARENT ATTENDANCE =========================
async function loadParentAttendance() {
  try {
    // Get first student (parents only have their own student)
    const studentsResp = await fetch('http://localhost:8000/api/students', {
      headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
    });
    const students = await studentsResp.json();
    if (students.length === 0) return;

    const studentId = students[0].id;
    const response = await fetch(`http://localhost:8000/api/attendance/student/${studentId}`, {
      headers: {'Authorization': 'Bearer ' + localStorage.getItem('authToken')}
    });
    const data = await response.json();

    const records = data.attendance || [];
    const present = records.filter(r => r.status === 'present').length;
    const absent = records.filter(r => r.status === 'absent').length;
    const total = present + absent;
    const percent = total > 0 ? Math.round((present / total) * 100) : 0;

    document.getElementById('attClasses').textContent = present;
    document.getElementById('attMissed').textContent = absent;
    document.getElementById('attPercent').textContent = percent + '%';

    let html = '';
    records.slice(0, 10).forEach(r => {
      const date = new Date(r.marked_at).toLocaleDateString();
      const status = r.status === 'present' ? '✓ Present' : '✗ Absent';
      html += `
        <div class="tr">
          <div class="ctm">${date}</div>
          <div class="ctm">Class</div>
          <div class="ctm" style="color:${r.status === 'present' ? 'var(--gn)' : 'var(--rd)'}">${status}</div>
        </div>
      `;
    });

    document.getElementById('parentAttendance').innerHTML = html || '<div class="tr"><div class="ctm">No attendance records</div></div>';
  } catch (e) {
    console.error('Error:', e);
  }
}

// Load data on admin payment tab open
async function initAdminPayments() {
  await loadPaymentData();
}
```

---

## Add to Page Load (DOMContentLoaded section)

After `await loadParentData();` add:

```javascript
    await loadParentAttendance();
```

And after `await loadAdminData();` add:

```javascript
    await initAdminPayments();
```

---

## Summary of Changes

✓ Add "Student Lookup" tab to admin nav
✓ Update Payments section to record/view payments  
✓ Add Student Lookup section to filter by day/time/name
✓ Update Attendance section to mark attendance
✓ Add Parent Attendance tab to show stats + history
✓ Add JavaScript functions for all Phase 2 features

This completes Phase 2 frontend implementation!
