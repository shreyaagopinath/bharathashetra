# Bharathashetra Dance School - Full Application

A modern web application for managing dance school operations with a Flask backend API and a responsive frontend.

## Project Structure

```
bharathashetra-app/
├── backend/               # Flask REST API
│   ├── app.py            # Application factory
│   ├── models.py         # Database models
│   ├── routes/           # API route handlers
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment configuration template
│   └── README.md          # Backend documentation
├── frontend/              # Web application
│   ├── index.html         # Dashboard page
│   ├── login.html         # Login/Signup page
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript modules
│   └── README.md          # Frontend documentation
└── docs/                  # Project documentation
```

## Quick Start

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. **Run development server**
   ```bash
   python app.py
   ```
   API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Serve files locally**
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Or using Node.js http-server
   npx http-server .
   ```

3. **Access application**
   - Open `http://localhost:8000/login.html`
   - API URL should point to your backend (default: `http://localhost:5000/api`)

## Features

### Authentication
- User registration and login
- JWT-based authentication
- Role-based access control (admin, parent, student)

### Student Management
- Register students
- View and manage student profiles
- Track enrollment history

### Classes
- Create and manage dance classes
- Track class levels (beginner, intermediate, advanced)
- Manage student enrollments

### Attendance
- Mark attendance for class sessions
- Track attendance history per student
- Generate attendance reports

### Payments
- Record payment transactions
- Track payment history
- Filter by status and date

### Forms
- Create custom forms for surveys/feedback
- Collect form responses
- Export response data

### Videos
- Upload and manage class videos
- Control video visibility (public/private/members-only)
- Link videos to classes

## Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: SQLAlchemy ORM (supports SQLite, PostgreSQL, MySQL)
- **Authentication**: Flask-JWT-Extended
- **CORS**: Flask-CORS

### Frontend
- **Language**: Vanilla JavaScript (ES6+)
- **Styling**: CSS3 with CSS variables
- **Icons/Fonts**: Google Fonts (Cinzel Decorative, Cormorant Garamond, Raleway)
- **Storage**: LocalStorage for auth tokens

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user (requires auth)

### Student Endpoints
- `GET /students` - List all students (auth required)
- `GET /students/<id>` - Get specific student
- `POST /students` - Create student (auth required)
- `PUT /students/<id>` - Update student (auth required)

### Class Endpoints
- `GET /classes` - List all classes
- `GET /classes/<id>` - Get specific class
- `POST /classes` - Create class (admin only)
- `POST /classes/<id>/enroll` - Enroll student (auth required)

### Attendance Endpoints
- `GET /attendance/student/<id>` - Get student attendance
- `GET /attendance/session/<id>` - Get session attendance (admin only)
- `POST /attendance` - Mark attendance (admin only)

### Payment Endpoints
- `GET /payments/student/<id>` - Get student payments (auth required)
- `GET /payments/<id>` - Get payment details (auth required)
- `POST /payments` - Record payment (auth required)

### Form Endpoints
- `GET /forms` - List all forms
- `GET /forms/<id>` - Get form with fields
- `POST /forms/<id>/submit` - Submit form response
- `POST /forms` - Create form (admin only)
- `GET /forms/<id>/responses` - Get responses (admin only)

### Video Endpoints
- `GET /videos` - List public videos
- `GET /videos/<id>` - Get video details
- `POST /videos` - Upload video (admin only)
- `PUT /videos/<id>` - Update video (admin only)

## Database Schema

### Core Models
- **User** - Authentication and role management
- **Parent** - Parent/guardian information
- **Student** - Student profiles and enrollment
- **DanceClass** - Class information and metadata
- **Enrollment** - Student-class relationships
- **ClassSession** - Individual class instances
- **Attendance** - Attendance records
- **Payment** - Payment transactions
- **Form** - Form definitions
- **FormResponse** - Form submissions
- **Video** - Video content library

## Configuration

### Environment Variables
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
DATABASE_URL=sqlite:///bharathashetra.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Database Options
- **SQLite** (default): `sqlite:///bharathashetra.db`
- **PostgreSQL**: `postgresql://user:password@localhost/bharathashetra`
- **MySQL**: `mysql+pymysql://user:password@localhost/bharathashetra`

## Deployment

### Using Gunicorn (Production)
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Using Docker
```bash
# Build
docker build -t bharathashetra-api .

# Run
docker run -p 5000:5000 -e DATABASE_URL=postgresql://... bharathashetra-api
```

### Static Hosting (Frontend)
Deploy frontend files to:
- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront
- Traditional web server (nginx, Apache)

## Development

### Running Tests
```bash
cd backend
pytest tests/ -v
```

### Code Style
- Python: Follow PEP 8
- JavaScript: Follow Airbnb style guide

### Linting
```bash
# Backend
pylint backend/
flake8 backend/

# Frontend
eslint frontend/js/
```

## Troubleshooting

### CORS Issues
- Check `CORS_ORIGINS` in `.env` matches your frontend URL
- Ensure credentials are included in requests

### Database Connection Errors
- Verify `DATABASE_URL` is correct
- Ensure database service is running
- Check user permissions

### Authentication Failures
- Verify JWT secret keys are set
- Check token expiration in localStorage
- Clear browser cache and try again

## Support & Contributing

For issues, questions, or contributions:
1. Create an issue with detailed description
2. Follow code style guidelines
3. Test changes thoroughly
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Next Steps

1. **Customize branding** - Update colors, logos, school name
2. **Add more features** - Email notifications, SMS alerts, financial reporting
3. **Optimize database** - Add indexes for frequently queried fields
4. **Implement caching** - Redis for session management
5. **Add mobile app** - React Native/Flutter for native mobile experience
6. **Setup monitoring** - Error tracking, performance metrics
7. **Enable payment processing** - Stripe/PayPal integration
8. **Add video streaming** - HLS/DASH support for efficient video delivery
