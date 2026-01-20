/**
 * Subscription Manager - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();

    // Initialize notification dropdown
    initNotificationDropdown();

    // Initialize form validation
    initFormValidation();

    // Initialize confirmation dialogs
    initConfirmDialogs();

    // Auto-dismiss alerts
    initAlertDismiss();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize notification dropdown with AJAX loading
 */
function initNotificationDropdown() {
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationList = document.getElementById('notificationList');

    if (notificationDropdown && notificationList) {
        notificationDropdown.addEventListener('show.bs.dropdown', function() {
            loadNotifications();
        });
    }
}

/**
 * Load notifications via AJAX
 */
function loadNotifications() {
    const notificationList = document.getElementById('notificationList');

    fetch('/notifications/dropdown')
        .then(response => response.json())
        .then(data => {
            if (data.notifications.length === 0) {
                notificationList.innerHTML = `
                    <div class="text-center py-3 text-muted">
                        <i class="bi bi-check-circle"></i>
                        <p class="small mb-0">No new notifications</p>
                    </div>
                `;
            } else {
                let html = '';
                data.notifications.forEach(function(notif) {
                    html += `
                        <a href="/subscriptions/${notif.subscription_id || ''}" class="dropdown-item d-flex align-items-start py-2">
                            <i class="bi ${notif.icon} text-${notif.color} me-2 mt-1"></i>
                            <div class="flex-grow-1">
                                <p class="mb-0 small">${notif.message}</p>
                                <small class="text-muted">${notif.created_at}</small>
                            </div>
                        </a>
                    `;
                });
                notificationList.innerHTML = html;
            }

            // Update badge
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                if (data.unread_count > 0) {
                    badge.textContent = data.unread_count > 99 ? '99+' : data.unread_count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            notificationList.innerHTML = `
                <div class="text-center py-3 text-danger">
                    <small>Error loading notifications</small>
                </div>
            `;
        });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Initialize confirmation dialogs for delete actions
 */
function initConfirmDialogs() {
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(event) {
            const message = btn.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initAlertDismiss() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        }).catch(function() {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback for clipboard copy
 */
function fallbackCopyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy', 'danger');
    }
    document.body.removeChild(textarea);
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if not exists
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }

    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toast);

    // Show toast
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    // Remove toast element after hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Format currency amount
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Format date
 */
function formatDate(dateString, options = {}) {
    const date = new Date(dateString);
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    return date.toLocaleDateString('en-US', { ...defaultOptions, ...options });
}

/**
 * Calculate days until date
 */
function daysUntil(dateString) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const targetDate = new Date(dateString);
    targetDate.setHours(0, 0, 0, 0);
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

/**
 * Toggle dark mode
 */
function toggleDarkMode() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-bs-theme', newTheme);

    // Save preference
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ dark_mode: newTheme === 'dark' })
    });
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in other scripts
window.SubManager = {
    copyToClipboard,
    showToast,
    formatCurrency,
    formatDate,
    daysUntil,
    toggleDarkMode,
    debounce,
    loadNotifications
};
