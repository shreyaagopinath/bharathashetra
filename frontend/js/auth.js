// Authentication functions
class Auth {
  static async login(email, password) {
    try {
      const url = `${API_CONFIG.baseURL}/auth/login`;
      console.log('Attempting login to:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: API_CONFIG.headers,
        body: JSON.stringify({ email, password })
      });

      console.log('Response status:', response.status);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      setAuthToken(data.access_token);
      localStorage.setItem('userId', data.user_id);
      localStorage.setItem('userRole', data.role);

      return data;
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        apiUrl: API_CONFIG.baseURL
      });
      throw error;
    }
  }

  static async register(email, password, name, phone, address) {
    try {
      const response = await fetch(`${API_CONFIG.baseURL}/auth/register`, {
        method: 'POST',
        headers: API_CONFIG.headers,
        body: JSON.stringify({
          email,
          password,
          name,
          phone,
          address
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      setAuthToken(data.access_token);
      localStorage.setItem('userId', data.user_id);
      localStorage.setItem('userRole', 'parent');

      return data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  static async getCurrentUser() {
    try {
      const response = await fetch(`${API_CONFIG.baseURL}/auth/me`, {
        method: 'GET',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }

      return await response.json();
    } catch (error) {
      console.error('Get user error:', error);
      throw error;
    }
  }

  static logout() {
    clearAuthToken();
    localStorage.removeItem('userId');
    localStorage.removeItem('userRole');
    window.location.href = '/login.html';
  }

  static isAuthenticated() {
    return !!getAuthToken();
  }

  static getUserId() {
    return localStorage.getItem('userId');
  }

  static getUserRole() {
    return localStorage.getItem('userRole');
  }
}
