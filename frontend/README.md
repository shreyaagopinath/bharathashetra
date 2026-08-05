# Bharathashetra Frontend Application

A modern, responsive web application for managing dance school operations built with vanilla JavaScript and CSS3.

## Overview

This is the user-facing interface for the Bharathashetra dance school management system. It provides dashboards and tools for parents, students, and administrators to:

- Register and manage student profiles
- Track class enrollments
- View attendance records
- Manage payments
- Submit and track forms
- Access instructional videos

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS variables and flexbox
- **JavaScript (ES6+)** - Vanilla JS with no frameworks
- **Local Storage** - Client-side data persistence
- **Fetch API** - HTTP requests to backend

## File Structure

```
frontend/
├── index.html              # Main application dashboard
├── login.html              # Login/registration page
├── css/
│   └── styles.css          # Main stylesheet (1200+ lines)
├── js/
│   ├── config.js           # API configuration
│   ├── auth.js             # Authentication methods
│   ├── api.js              # API service methods
│   ├── ui.js               # UI helper functions
│   └── app.js              # Main application logic
└── README.md               # This file
```

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Access to the backend API (running on `http://localhost:5000`)

### Running Locally

**Option 1: Python HTTP Server**
```bash
cd frontend
python -m http.server 8000
# Open http://localhost:8000/login.html
```

**Option 2: Node.js HTTP Server**
```bash
cd frontend
npx http-server . -p 8000
# Open http://localhost:8000/login.html
```

**Option 3: Live Server (VS Code Extension)**
- Install "Live Server" extension
- Right-click `login.html` → "Open with Live Server"

## Configuration

### API Base URL
The API base URL can be configured on the login page or programmatically:

```javascript
// Set API URL
localStorage.setItem('apiUrl', 'http://localhost:5000/api');

// Or in login.html, use the API URL input field
```

Default: `http://localhost:5000/api`

## Features

### Authentication
- User registration (parents)
- Login with email and password
- JWT token storage in localStorage
- Automatic logout on token expiration
- Role-based access (admin, parent, student)

### Dashboard
- Quick statistics (students, classes, payments, pending)
- Navigation between different sections
- View switcher for different modules

### Classes
- Browse all available dance classes
- Filter by level and style
- View class details and instructor info
- Enroll students in classes
- Search functionality

### Attendance
- View attendance records by student
- Track attendance status (present, absent, late)
- Historical attendance data
- Attendance summary

### Payments
- View payment history
- Filter by status (completed, pending, failed)
- See transaction details
- Track payment dates and amounts

### Forms
- Browse available forms
- Submit form responses
- Track submission history

### Videos
- Access video library
- Watch instructional videos
- Filter videos by class

## Code Organization

### config.js
Handles API configuration and authentication token management.

```javascript
API_CONFIG.baseURL  // Base URL for API calls
getAuthToken()      // Retrieve stored auth token
setAuthToken()      // Store auth token
getAuthHeaders()    // Get headers with auth token
```

### auth.js
Provides authentication methods through the `Auth` class.

```javascript
Auth.login(email, password)           // Login user
Auth.register(email, password, ...)   // Register new user
Auth.getCurrentUser()                 // Get current user info
Auth.logout()                         // Logout and clear token
Auth.isAuthenticated()                // Check if logged in
Auth.getUserId()                      // Get current user ID
Auth.getUserRole()                    // Get user's role
```

### api.js
Service class for making API calls.

```javascript
API.request(endpoint, options)    // Generic request method
API.getStudents()                 // Get all students
API.getClasses()                  // Get all classes
API.getAttendance(studentId)      // Get attendance records
API.getPayments(studentId)        // Get payment history
API.submitForm(formId, data)      // Submit a form
API.getVideos()                   // Get video library
// ... and many more
```

### ui.js
Helper functions for UI operations.

```javascript
UI.showNotification(message, type)     // Show toast notification
UI.formatDate(date)                    // Format date string
UI.formatCurrency(amount)              // Format currency
UI.getStatusBadgeClass(status)         // Get CSS class for status
UI.renderCard(data)                    // Render stat card
UI.renderClassCard(classData)          // Render class card
UI.renderPaymentRow(payment)           // Render payment row
UI.renderAttendanceRow(record)         // Render attendance row
```

### app.js
Main application logic and event handling.

```javascript
App.init()              // Initialize application
App.setupEventListeners() // Setup all event handlers
App.switchView(name)    // Switch between views
App.switchSection(name) // Switch between sections
App.loadDashboard()     // Load dashboard data
App.loadClasses()       // Load classes data
App.loadAttendance()    // Load attendance data
App.loadPayments()      // Load payments data
```

## Styling

### Design System
- **Color Scheme**: Dark theme with gold/burgundy accents
- **Typography**: Serif (Cormorant Garamond) for body, Decorative (Cinzel) for headings
- **Spacing**: 4px base unit system
- **Responsive**: Mobile-first approach

### CSS Variables
```css
--cr: #8B1A1A           /* Crimson red */
--go: #C9993A           /* Gold */
--bgo: #E8B84B          /* Bright gold */
--pg: #F5E6C0           /* Light beige */
--dk: #1A0A0A           /* Dark background */
--gn: #4CAF8A           /* Green (success) */
--rd: #D46060           /* Red (danger) */
```

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Optimizations

- Lazy loading of images
- Minimal CSS (single stylesheet)
- Efficient DOM manipulation
- LocalStorage for auth tokens
- Request caching via API methods

## Security Considerations

- JWT tokens stored in localStorage (consider moving to httpOnly cookies for production)
- CORS headers validated by backend
- Password handling delegated to backend
- No sensitive data stored in localStorage
- CSRF protection via CORS and content-type validation

## Common Workflows

### Login as Parent
1. Go to `/login.html`
2. Enter parent email and password
3. Dashboa rd loads automatically

### Register as Parent
1. Go to `/login.html`
2. Click "Sign Up"
3. Fill in details and submit
4. Automatically logged in

### View Student Attendance
1. Navigate to "Attendance" section
2. Select student from dropdown
3. View attendance history table

### Record Payment
1. Navigate to "Payments" section
2. Click "Add Payment" (if available)
3. Enter payment details
4. Submit

## Error Handling

Errors are handled gracefully with:
- User-friendly error messages
- Console logging for debugging
- Automatic logout on auth errors
- Fallback to empty states when data unavailable

## Extending the Application

### Adding a New Page
1. Create new HTML file (e.g., `reports.html`)
2. Include all required JS files
3. Create corresponding section in main app
4. Add navigation link

### Adding a New API Call
1. Add method to `API` class in `api.js`
2. Use `this.request()` method
3. Call from app logic

### Styling Changes
Edit `css/styles.css` and modify:
- CSS variables for colors
- Component classes for layout
- Media queries for responsiveness

## Debugging

### Browser Console
Open browser DevTools (F12 or Cmd+Option+I) to see:
- Console errors
- API request/response
- Stored data in localStorage

### Common Issues

**Blank login page**
- Check browser console for JavaScript errors
- Verify all JS files are loaded
- Clear browser cache

**API connection errors**
- Verify backend is running
- Check API URL in login page
- Check CORS settings in backend

**Authentication not working**
- Check auth token in localStorage
- Verify credentials are correct
- Try logging out and in again

## Building for Production

1. **Optimize assets**
   - Minify CSS and JavaScript
   - Optimize images
   - Remove console.logs

2. **Environment configuration**
   - Update API_CONFIG.baseURL
   - Set production API URL

3. **Deploy to hosting**
   - GitHub Pages (free)
   - Netlify (free tier available)
   - Vercel
   - AWS S3 + CloudFront
   - Traditional web server

4. **Security checklist**
   - Update API endpoint URLs
   - Enable HTTPS everywhere
   - Configure CORS properly
   - Set secure cookies

## License

MIT

## Support

For issues or questions, refer to the main project README.md or contact the development team.
