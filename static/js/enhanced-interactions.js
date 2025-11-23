/**
 * ENHANCED INTERACTIONS - Modern UX Patterns
 * Forms, validation, tooltips, modals, and user feedback
 */

class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (!this.form) return;
        
        this.init();
    }
    
    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.form.addEventListener('change', (e) => this.validateField(e.target));
        this.form.addEventListener('blur', (e) => this.validateField(e.target), true);
    }
    
    validateField(field) {
        if (!field.value) {
            this.setError(field, 'This field is required');
            return false;
        }
        
        if (field.type === 'email' && !this.isValidEmail(field.value)) {
            this.setError(field, 'Please enter a valid email');
            return false;
        }
        
        if (field.type === 'number' && isNaN(field.value)) {
            this.setError(field, 'Please enter a valid number');
            return false;
        }
        
        this.clearError(field);
        return true;
    }
    
    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
    
    setError(field, message) {
        field.classList.add('error');
        field.classList.remove('success');
        
        let errorEl = field.nextElementSibling;
        if (!errorEl || !errorEl.classList.contains('form-error')) {
            errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            field.parentNode.insertBefore(errorEl, field.nextSibling);
        }
        errorEl.textContent = message;
    }
    
    clearError(field) {
        field.classList.remove('error');
        field.classList.add('success');
        
        const errorEl = field.nextElementSibling;
        if (errorEl && errorEl.classList.contains('form-error')) {
            errorEl.remove();
        }
    }
    
    handleSubmit(e) {
        const fields = this.form.querySelectorAll('input, textarea, select');
        let isValid = true;
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            this.showNotification('Please fix the errors below', 'error');
        }
    }
    
    showNotification(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

class TooltipManager {
    constructor() {
        this.tooltips = new Map();
        this.init();
    }
    
    init() {
        document.querySelectorAll('[data-tooltip]').forEach(el => {
            const message = el.getAttribute('data-tooltip');
            this.create(el, message);
        });
    }
    
    create(element, message) {
        const wrapper = document.createElement('div');
        wrapper.className = 'tooltip';
        
        const tooltipText = document.createElement('div');
        tooltipText.className = 'tooltip-text';
        tooltipText.textContent = message;
        
        element.parentNode.insertBefore(wrapper, element);
        wrapper.appendChild(element);
        wrapper.appendChild(tooltipText);
    }
}

class ModalManager {
    constructor() {
        this.modals = new Map();
        this.init();
    }
    
    init() {
        document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
            trigger.addEventListener('click', (e) => this.open(e.target.dataset.modalTrigger));
        });
        
        document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => this.closeAll());
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeAll();
        });
    }
    
    open(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }
    
    close(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    closeAll() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
}

class NotificationSystem {
    static success(message, duration = 3000) {
        this.show(message, 'success', duration);
    }
    
    static error(message, duration = 4000) {
        this.show(message, 'error', duration);
    }
    
    static warning(message, duration = 3500) {
        this.show(message, 'warning', duration);
    }
    
    static info(message, duration = 3000) {
        this.show(message, 'info', duration);
    }
    
    static show(message, type, duration) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toast.setAttribute('role', 'status');
        toast.setAttribute('aria-live', 'polite');
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// LoadingManager is defined in ux-enhancements.js, using from there

class KeyboardNavigation {
    constructor() {
        this.init();
    }
    
    init() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                const submitBtn = document.activeElement?.form?.querySelector('[type="submit"]');
                if (submitBtn) submitBtn.click();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TooltipManager();
    new ModalManager();
    new KeyboardNavigation();
    
    document.querySelectorAll('form').forEach(form => {
        new FormValidator(form);
    });
});

window.Notification = NotificationSystem;
// LoadingManager available from ux-enhancements.js
