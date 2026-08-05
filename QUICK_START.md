# Quick Start Guide - 5 Minutes

## Step 1: Open Two Terminal Windows

You'll need **two separate terminals** - one for backend, one for frontend.

---

## Step 2: Start Backend (Terminal 1)

```bash
# Navigate to backend folder
cd ~/Desktop/bharathashetra-app/backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python app.py
```

**You should see:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

✅ **Backend is running!** Keep this terminal open.

---

## Step 3: Start Frontend (Terminal 2)

```bash
# Navigate to frontend folder
cd ~/Desktop/bharathashetra-app/frontend

# Start web server
# Using Python (any version):
python -m http.server 8000

# OR using Node.js:
npx http-server . -p 8000
```

**You should see:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/)
```

✅ **Frontend is running!** Keep this terminal open.

---

## Step 4: Open in Browser

Open your browser and go to:
```
http://localhost:8000/login.html
```

---

## Step 5: Create Admin Account (First Time Only)

Run this **once** to create an admin user:

```bash
# In the backend terminal, press Ctrl+C to stop the server
# Then run:

python3 << EOF
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    admin = User(email='admin@dance.local', role='admin')
    admin.set_password('Admin123!')
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin created!")
    print("Email: admin@dance.local")
    print("Password: Admin123!")
EOF

# Then restart: python app.py
```

---

## Step 6: Login

**Login with:**
- Email: `admin@dance.local`
- Password: `Admin123!`

You'll see the admin dashboard!

---

## Troubleshooting

### Backend won't start
```
Error: Address already in use
```
→ Kill the process: `lsof -i :5000` then `kill -9 <PID>`

### Backend missing modules
```
Error: ModuleNotFoundError
```
→ Make sure you activated virtual env: `source venv/bin/activate`

### Frontend shows blank page
```
API not connecting
```
→ Make sure backend is running on `http://localhost:5000`
→ Check API URL in login page (should be `http://localhost:5000/api`)

### Can't access http://localhost:8000
```
Connection refused
```
→ Make sure you ran `python -m http.server 8000` in frontend folder
→ Check it's running in the second terminal

---

## Normal Workflow (After Setup)

Every time you want to use the app:

**Terminal 1 (Backend):**
```bash
cd ~/Desktop/bharathashetra-app/backend
source venv/bin/activate
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd ~/Desktop/bharathashetra-app/frontend
python -m http.server 8000
```

**Browser:**
```
http://localhost:8000/login.html
```

---

## To Stop Everything

Press `Ctrl+C` in each terminal to stop the servers.

---

## Next Steps

1. **Create test data** - Register students, add classes, record payments
2. **Explore features** - Try all admin sections (Payments, Attendance, etc.)
3. **Test parent portal** - Create a parent account via Sign Up
4. **Customize** - Change school name, colors, add your own data

**Have fun! 🎉**
