// Main application logic
class App {
  constructor() {
    this.init();
  }

  async init() {
    // Check authentication
    if (!Auth.isAuthenticated()) {
      window.location.href = '/login.html';
      return;
    }

    this.setupEventListeners();
    await this.loadDashboard();
  }

  setupEventListeners() {
    // View switcher
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.switchView(e.target.dataset.view));
    });

    // Section switcher
    document.querySelectorAll('.anav-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.switchSection(e.target.dataset.section));
    });

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', () => {
      if (confirm('Are you sure you want to logout?')) {
        Auth.logout();
      }
    });

    // Search and filter
    document.getElementById('classSearch')?.addEventListener('input', (e) => {
      this.filterClasses(e.target.value);
    });

    document.getElementById('levelFilter')?.addEventListener('change', (e) => {
      this.filterClasses('', e.target.value);
    });
  }

  switchView(viewName) {
    // Hide all sections
    document.querySelectorAll('.sec').forEach(sec => sec.classList.remove('active'));

    // Show selected section
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

    // Update button states
    document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-view="${viewName}"]`).parentElement
      ?.querySelector('.view-btn[data-view]')?.classList.add('active');

    // Load data for view
    if (viewName === 'classes') this.loadClasses();
    if (viewName === 'attendance') this.loadAttendance();
    if (viewName === 'payments') this.loadPayments();
  }

  switchSection(sectionName) {
    document.querySelectorAll('.anav-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    // Load section data
    if (sectionName === 'registrations') this.loadRegistrations();
    if (sectionName === 'forms') this.loadForms();
    if (sectionName === 'videos') this.loadVideos();
  }

  async loadDashboard() {
    try {
      const cards = document.getElementById('dashboardCards');
      if (!cards) return;

      const students = await API.getStudents().catch(() => []);
      const classes = await API.getClasses().catch(() => []);

      cards.innerHTML = `
        ${UI.renderCard({ number: students.length, label: 'Students' })}
        ${UI.renderCard({ number: classes.length, label: 'Classes' })}
        ${UI.renderCard({ number: '0', label: 'Payments' })}
        ${UI.renderCard({ number: '0', label: 'Pending' })}
      `;
    } catch (error) {
      console.error('Dashboard load error:', error);
      UI.showNotification('Failed to load dashboard', 'error');
    }
  }

  async loadClasses() {
    try {
      const classesGrid = document.getElementById('classesGrid');
      const classes = await API.getClasses();

      classesGrid.innerHTML = classes
        .map(c => UI.renderClassCard(c))
        .join('');
    } catch (error) {
      console.error('Classes load error:', error);
      UI.showNotification('Failed to load classes', 'error');
    }
  }

  async loadAttendance() {
    try {
      const studentSelect = document.getElementById('studentSelect');
      const students = await API.getStudents();

      studentSelect.innerHTML = '<option value="">Select Student</option>' +
        students.map(s => `<option value="${s.id}">${s.name}</option>`).join('');

      studentSelect.addEventListener('change', async (e) => {
        if (e.target.value) {
          const attendance = await API.getAttendance(e.target.value);
          const list = document.getElementById('attendanceList');
          list.innerHTML = attendance.attendance
            .map(a => UI.renderAttendanceRow(a))
            .join('');
        }
      });
    } catch (error) {
      console.error('Attendance load error:', error);
      UI.showNotification('Failed to load attendance', 'error');
    }
  }

  async loadPayments() {
    try {
      const paymentsList = document.getElementById('paymentsList');
      const students = await API.getStudents();

      let allPayments = [];
      for (const student of students) {
        const payments = await API.getPayments(student.id).catch(() => ({ payments: [] }));
        allPayments = allPayments.concat(
          (payments.payments || []).map(p => ({
            ...p,
            student_name: student.name
          }))
        );
      }

      paymentsList.innerHTML = allPayments
        .map(p => UI.renderPaymentRow(p))
        .join('') || '<div class="tr"><div class="ctm">No payments found</div></div>';
    } catch (error) {
      console.error('Payments load error:', error);
      UI.showNotification('Failed to load payments', 'error');
    }
  }

  filterClasses(searchTerm = '', level = '') {
    // Filter implementation
  }

  async loadRegistrations() {
    // Load registration data
  }

  async loadForms() {
    try {
      const forms = await API.getForms();
      console.log('Forms:', forms);
    } catch (error) {
      console.error('Forms load error:', error);
    }
  }

  async loadVideos() {
    try {
      const videos = await API.getVideos();
      console.log('Videos:', videos);
    } catch (error) {
      console.error('Videos load error:', error);
    }
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new App();
});
