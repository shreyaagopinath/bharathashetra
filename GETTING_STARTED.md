# Getting Started with Bharathashetra App

## Overview

This guide walks you through setting up and running the complete Bharathashetra dance school application with both backend API and frontend.

## Prerequisites

- Python 3.8+ (for backend)
- Modern web browser (for frontend)
- A code editor (VS Code, PyCharm, etc.)
- Terminal/Command Prompt access

## Step 1: Initial Setup

### Clone/Download the Project
```bash
# Navigate to your Desktop
cd ~/Desktop/bharathashetra-app
```

## Step 2: Backend Setup

### 1. Create Python Virtual Environment
```bash
cd backend
python -m venv venv

# Activate it:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and customize:
- `SECRET_KEY` - Change to a random string
- `JWT_SECRET_KEY` - Change to a random string
- `DATABASE_URL` - Keep as-is for SQLite, or configure PostgreSQL
- `CORS_ORIGINS` - Set to your frontend URL (e.g., `http://localhost:8000`)

### 4. Initialize Database
```bash
python << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
EOF
```

### 5. Start Backend Server
```bash
python app.py
```

You should see:
```
* Running on http://localhost:5000
```

Keep this terminal open. The API is now ready!

## Step 3: Frontend Setup

### 1. In a New Terminal, Navigate to Frontend
```bash
cd ~/Desktop/bharathashetra-app/frontend
```

### 2. Start Web Server

**Option A: Using Python**
```bash
python -m http.server 8000
```

**Option B: Using Node.js**
```bash
npx http-server . -p 8000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8000
```

### 3. Open Application
Open your browser and navigate to:
```
http://localhost:8000/login.html
```

## Step 4: First Login

### Create Admin Account

Unfortunately, we need to create the first admin account manually. Use this script:

```bash
# In the backend directory, in a Python shell:
python << EOF
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    # Create admin user
    admin = User(email='admin@bharathashetra.local', role='admin')
    admin.set_password('Admin123!')  # Change this!
    db.session.add(admin)
    db.session.commit()
    print(f"Admin created! Email: {admin.email}")
EOF
```

### Login to Application
1. Go to `http://localhost:8000/login.html`
2. Enter email: `admin@bharathashetra.local`
3. Enter password: `Admin123!` (or whatever you set)
4. Click "Login"

## Step 5: Create Sample Data

### Create a Dance Class
Once logged in as admin:
1. The dashboard loads automatically
2. Use the API or create a simple script:

```python
python << EOF
from app import create_app, db
from models import DanceClass

app = create_app()
with app.app_context():
    # Create sample class
    bharatanatyam = DanceClass(
        name='Bharatanatyam Basics',
        style='Bharatanatyam',
        level='Beginner',
        instructor='Guru Jayaraman',
        schedule='Mon, Wed, Fri - 4:00 PM',
        capacity=20,
        fees=100.0,
        description='Learn the fundamentals of Bharatanatyam dance'
    )
    db.session.add(bharatanatyam)
    db.session.commit()
    print(f"Class created: {bharatanatyam.name}")
EOF
```

### Create a Student/Parent Account
1. Click "Sign Up" on the login page
2. Fill in details (name, email, phone)
3. Create account
4. Now you have a parent account you can test with

## Project Structure

```
backend/
├── app.py              # Main Flask app
├── models.py           # Database models
├── routes/             # API endpoints
│   ├── auth.py        # Login/Register
│   ├── students.py    # Student management
│   ├── classes.py     # Class management
│   ├── attendance.py  # Attendance tracking
│   ├── payments.py    # Payment tracking
│   ├── forms.py       # Form management
│   └── videos.py      # Video management
├── requirements.txt    # Python packages
└── .env               # Configuration (create from .env.example)

frontend/
├── index.html         # Main dashboard
├── login.html         # Login/Signup page
├── css/
│   └── styles.css     # Main stylesheet
└── js/
    ├── config.js      # Configuration
    ├── auth.js        # Authentication logic
    ├── api.js         # API calls
    ├── ui.js          # UI helpers
    └── app.js         # Main app logic
```

## API Testing

### Using cURL
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bharathashetra.local","password":"Admin123!"}'

# Get current user (replace TOKEN with actual token)
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### Using Frontend
The frontend automatically handles API calls when you:
- Log in/Register
- View classes
- Track attendance
- Record payments
- Submit forms

## Troubleshooting

### Backend Won't Start
**Error: "Address already in use"**
- Port 5000 is being used by another app
- Solution: Edit `.env` and change port, or kill the process using port 5000

**Error: "ModuleNotFoundError"**
- Virtual environment not activated
- Solution: Run `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)

### Frontend Won't Load
**Error: "Cannot connect to server"**
- Backend is not running
- Solution: Make sure backend is running on `http://localhost:5000`

**Error: API URL not recognized**
- Check API URL in login page
- Default should be `http://localhost:5000/api`
- Can be changed on login page

### Database Errors
**Error: "no such table"**
- Database not initialized
- Solution: Run the initialization script from Step 2.4

**Error: "database is locked"**
- SQLite is locked by another process
- Solution: Delete `bharathashetra.db` and reinitialize

## Next Steps

1. **Customize Branding** - Update colors in `frontend/css/styles.css`
2. **Add School Logo** - Replace icon in `frontend/login.html`
3. **Create More Classes** - Use the API or database scripts
4. **Import Data** - Migrate from Google Sheets to the database
5. **Setup Email** - Add Flask-Mail for notifications
6. **Configure Database** - Switch to PostgreSQL for production
7. **Deploy** - See main README.md for deployment options

## Common Workflows

### Add a New Student via API
```bash
# First, get auth token (see API Testing)
curl -X POST http://localhost:5000/api/students \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Kumar",
    "email": "priya@example.com",
    "phone": "555-1234",
    "date_of_birth": "2010-05-15"
  }'
```

### Enroll Student in Class
```bash
# CLASS_ID and STUDENT_ID from previous calls
curl -X POST http://localhost:5000/api/classes/CLASS_ID/enroll \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"student_id": STUDENT_ID}'
```

### Record Attendance
```bash
curl -X POST http://localhost:5000/api/attendance \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "session_id": 1,
    "status": "present"
  }'
```

## Getting Help

- **Backend Issues**: Check `backend/README.md`
- **Frontend Issues**: Check browser console (F12 → Console tab)
- **Database Issues**: Check `bharathashetra.db` file exists
- **API Issues**: Review API docs in main `README.md`

## Stopping the Application

1. Backend: Press `Ctrl+C` in the backend terminal
2. Frontend: Press `Ctrl+C` in the frontend terminal
3. Both servers will shut down

To restart later, just run the startup commands again!

---

**You're all set!** The application is now running locally. Start exploring the features and customize as needed for your dance school.
