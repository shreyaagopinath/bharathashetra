// UI Helper functions
class UI {
  static showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 20px;
      background: ${type === 'success' ? '#4CAF8A' : type === 'error' ? '#E8A838' : '#C9993A'};
      color: white;
      border-radius: 4px;
      z-index: 1000;
      font-family: 'Raleway', sans-serif;
      font-size: 14px;
      animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  static formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  static formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }

  static getStatusBadgeClass(status) {
    const statusMap = {
      'present': 'bdg bp',
      'absent': 'bdg bu',
      'late': 'bdg bl',
      'completed': 'bdg bp',
      'pending': 'bdg bpnd',
      'failed': 'bdg bu',
      'active': 'bdg bp',
      'inactive': 'bdg bu'
    };
    return statusMap[status] || 'bdg';
  }

  static renderCard(data) {
    return `
      <div class="sc">
        <span class="sn">${data.number}</span>
        <span class="sl">${data.label}</span>
      </div>
    `;
  }

  static renderClassCard(classData) {
    return `
      <div class="sc">
        <span class="sn">${classData.style}</span>
        <span class="sl">${classData.level}</span>
        <div style="margin-top: 8px; font-size: 11px; color: rgba(245,230,192,.5);">
          ${classData.instructor}
        </div>
      </div>
    `;
  }

  static renderPaymentRow(payment) {
    return `
      <div class="tr">
        <div class="snm">${payment.student_name}</div>
        <div class="ctm">${UI.formatCurrency(payment.amount)}</div>
        <div class="ctm">${UI.formatDate(payment.payment_date)}</div>
        <div><span class="${UI.getStatusBadgeClass(payment.status)}">${payment.status}</span></div>
      </div>
    `;
  }

  static renderAttendanceRow(record) {
    return `
      <div class="tr">
        <div class="ctm">${UI.formatDate(record.session_id)}</div>
        <div class="snm">Class</div>
        <div><span class="${UI.getStatusBadgeClass(record.status)}">${record.status}</span></div>
        <div class="spr">-</div>
      </div>
    `;
  }
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
