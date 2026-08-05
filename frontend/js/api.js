// API Service class
class API {
  static async request(endpoint, options = {}) {
    const url = `${API_CONFIG.baseURL}${endpoint}`;
    const headers = getAuthHeaders();

    try {
      const response = await fetch(url, {
        headers,
        ...options
      });

      if (response.status === 401) {
        Auth.logout();
        throw new Error('Unauthorized');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error: ${endpoint}`, error);
      throw error;
    }
  }

  // Students API
  static getStudents() {
    return this.request('/students');
  }

  static getStudent(id) {
    return this.request(`/students/${id}`);
  }

  static createStudent(data) {
    return this.request('/students', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static updateStudent(id, data) {
    return this.request(`/students/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // Classes API
  static getClasses() {
    return this.request('/classes');
  }

  static getClass(id) {
    return this.request(`/classes/${id}`);
  }

  static createClass(data) {
    return this.request('/classes', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static enrollStudent(classId, studentId) {
    return this.request(`/classes/${classId}/enroll`, {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId })
    });
  }

  // Attendance API
  static getAttendance(studentId) {
    return this.request(`/attendance/student/${studentId}`);
  }

  static markAttendance(data) {
    return this.request('/attendance', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Payments API
  static getPayments(studentId) {
    return this.request(`/payments/student/${studentId}`);
  }

  static recordPayment(data) {
    return this.request('/payments', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Forms API
  static getForms() {
    return this.request('/forms');
  }

  static getForm(id) {
    return this.request(`/forms/${id}`);
  }

  static submitForm(formId, data) {
    return this.request(`/forms/${formId}/submit`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Videos API
  static getVideos() {
    return this.request('/videos');
  }

  static getVideo(id) {
    return this.request(`/videos/${id}`);
  }

  // Announcements API
  static getAnnouncements() {
    return this.request('/announcements');
  }

  static createAnnouncement(data) {
    return this.request('/announcements', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static deleteAnnouncement(id) {
    return this.request(`/announcements/${id}`, {
      method: 'DELETE'
    });
  }

  // Settings API
  static getSettings() {
    return this.request('/settings');
  }

  static updateSettings(data) {
    return this.request('/settings', {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // Backup API
  static createBackup() {
    return this.request('/backup/create', {
      method: 'POST'
    });
  }

  static getBackupLogs() {
    return this.request('/backup/logs');
  }

  static getBackupStats() {
    return this.request('/backup/stats');
  }

  // Payment record with late fee calculation
  static recordPayment(data) {
    return this.request('/payments', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  static getCurrentMonthPayment(studentId) {
    return this.request(`/payments/student/${studentId}/current-month`);
  }
}
