// API Configuration
//
// The Flask service serves both this frontend and the API, so the API always
// lives at /api on whatever host the page was loaded from. Deriving it from
// the current origin means a custom domain works with no code change and no
// cross-origin request. The onrender.com value is only a fallback for opening
// the file directly off disk.
function resolveApiBase() {
  const override = localStorage.getItem('apiUrl');
  if (override) return override.replace(/\/+$/, '');

  if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
    return window.location.origin + '/api';
  }
  return 'https://bharathashetra.onrender.com/api';
}

const API_CONFIG = {
  baseURL: resolveApiBase(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// Auth token from localStorage
function getAuthToken() {
  return localStorage.getItem('authToken');
}

function setAuthToken(token) {
  localStorage.setItem('authToken', token);
}

function clearAuthToken() {
  localStorage.removeItem('authToken');
}

// Helper to make API calls with auth
function getAuthHeaders() {
  const token = getAuthToken();
  return {
    ...API_CONFIG.headers,
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
}
