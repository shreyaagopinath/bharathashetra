// API Configuration
const API_CONFIG = {
  baseURL: localStorage.getItem('apiUrl') || 'http://localhost:8000/api',
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
