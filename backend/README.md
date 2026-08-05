# Bharathashetra Dance School - Backend API

A Flask-based REST API for managing dance school operations including registration, attendance, payments, forms, and video content.

## Features

- **Authentication**: User registration and JWT-based login
- **Student Management**: Register and manage student profiles
- **Class Management**: Create classes and manage enrollments
- **Attendance Tracking**: Mark and track attendance
- **Payments**: Record and track payment history
- **Forms**: Create and collect form responses
- **Videos**: Manage and serve video content

## Setup

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 5. Run Development Server
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info (requires auth)
- `POST /api/auth/logout` - Logout (requires auth)

### Students
- `GET /api/students` - Get all students (requires auth)
- `GET /api/students/<id>` - Get specific student
- `POST /api/students` - Register new student (requires auth)
- `PUT /api/students/<id>` - Update student (requires auth)

### Classes
- `GET /api/classes` - Get all classes
- `GET /api/classes/<id>` - Get specific class
- `POST /api/classes` - Create class (admin only)
- `POST /api/classes/<id>/enroll` - Enroll student (requires auth)

### Attendance
- `GET /api/attendance/session/<id>` - Get session attendance (admin only)
- `GET /api/attendance/student/<id>` - Get student attendance (requires auth)
- `POST /api/attendance` - Mark attendance (admin only)

### Payments
- `GET /api/payments/student/<id>` - Get student payment history (requires auth)
- `GET /api/payments/<id>` - Get payment details (requires auth)
- `POST /api/payments` - Record payment (requires auth)

### Forms
- `GET /api/forms` - Get all forms
- `GET /api/forms/<id>` - Get form with fields
- `POST /api/forms` - Create form (admin only)
- `POST /api/forms/<id>/submit` - Submit form response
- `GET /api/forms/<id>/responses` - Get form responses (admin only)

### Videos
- `GET /api/videos` - Get all public videos
- `GET /api/videos/<id>` - Get video details
- `POST /api/videos` - Upload video (admin only)
- `PUT /api/videos/<id>` - Update video (admin only)

## Database Schema

See `models.py` for complete schema. Key entities:
- Users (with roles: admin, parent, student)
- Parents and Students
- Dance Classes
- Enrollments
- Attendance Records
- Payments
- Forms and Form Responses
- Videos

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in request headers:

```
Authorization: Bearer <your_token>
```

## Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

### Using Docker
```bash
docker build -t bharathashetra-api .
docker run -p 5000:5000 bharathashetra-api
```

### Environment Variables
- `FLASK_ENV` - development or production
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed CORS origins

## Testing

Run tests with:
```bash
pytest tests/
```

## License

MIT
