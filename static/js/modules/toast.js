/**
 * InvoiceFlow Toast Notification System
 * Modern, accessible, and customizable notifications
 */

import Utils from './utils.js';

const ICONS = {
  success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
  </svg>`,
  error: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
  </svg>`,
  warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>`,
  info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
  </svg>`,
  loading: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="toast-spinner">
    <circle cx="12" cy="12" r="10" stroke-dasharray="30 60"/>
  </svg>`
};

class ToastManager {
  constructor() {
    this.container = null;
    this.toasts = new Map();
    this.queue = [];
    this.maxVisible = 5;
    this.init();
  }

  init() {
    if (this.container) return;

    this.container = document.createElement('div');
    this.container.className = 'toast-container';
    this.container.setAttribute('role', 'region');
    this.container.setAttribute('aria-label', 'Notifications');
    this.container.setAttribute('aria-live', 'polite');
    document.body.appendChild(this.container);
  }

  show(options = {}) {
    const {
      type = 'info',
      title,
      message,
      duration = 5000,
      closable = true,
      action,
      actionText,
      progress = false,
      position = 'bottom-right'
    } = options;

    const id = Utils.generateId('toast');
    const toast = this.createToast({ id, type, title, message, closable, action, actionText, progress });
    
    this.container.setAttribute('data-position', position);
    
    if (this.toasts.size >= this.maxVisible) {
      this.queue.push({ toast, duration, id });
    } else {
      this.displayToast(toast, duration, id);
    }

    return {
      id,
      dismiss: () => this.dismiss(id),
      update: (newOptions) => this.update(id, newOptions)
    };
  }

  createToast({ id, type, title, message, closable, action, actionText, progress }) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.setAttribute('data-toast-id', id);
    
    if (Utils.prefersReducedMotion()) {
      toast.style.animation = 'none';
    }

    const progressHtml = progress 
      ? `<div class="toast-progress"><div class="toast-progress-bar"></div></div>` 
      : '';

    const actionHtml = action && actionText 
      ? `<button class="toast-action" type="button">${Utils.escape(actionText)}</button>` 
      : '';

    const closeHtml = closable 
      ? `<button class="toast-close" type="button" aria-label="Dismiss notification">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>` 
      : '';

    toast.innerHTML = `
      <div class="toast-icon">${ICONS[type]}</div>
      <div class="toast-body">
        <div class="toast-content">
          ${title ? `<div class="toast-title">${Utils.escape(title)}</div>` : ''}
          ${message ? `<div class="toast-message">${Utils.escape(message)}</div>` : ''}
        </div>
        ${actionHtml}
      </div>
      ${closeHtml}
      ${progressHtml}
    `;

    if (action && actionText) {
      toast.querySelector('.toast-action')?.addEventListener('click', () => {
        action();
        this.dismiss(id);
      });
    }

    if (closable) {
      toast.querySelector('.toast-close')?.addEventListener('click', () => this.dismiss(id));
    }

    return toast;
  }

  displayToast(toast, duration, id) {
    this.container.appendChild(toast);
    this.toasts.set(id, { element: toast, timeoutId: null });

    requestAnimationFrame(() => {
      toast.classList.add('toast-visible');
    });

    if (duration > 0) {
      const progressBar = toast.querySelector('.toast-progress-bar');
      if (progressBar) {
        progressBar.style.transition = `width ${duration}ms linear`;
        requestAnimationFrame(() => {
          progressBar.style.width = '0%';
        });
      }

      const timeoutId = setTimeout(() => this.dismiss(id), duration);
      const toastData = this.toasts.get(id);
      if (toastData) {
        toastData.timeoutId = timeoutId;
      }
    }
  }

  dismiss(id) {
    const toastData = this.toasts.get(id);
    if (!toastData) return;

    const { element, timeoutId } = toastData;
    
    if (timeoutId) clearTimeout(timeoutId);

    if (Utils.prefersReducedMotion()) {
      element.remove();
    } else {
      element.classList.add('toast-exiting');
      element.addEventListener('animationend', () => element.remove(), { once: true });
      setTimeout(() => element.remove(), 400);
    }

    this.toasts.delete(id);

    if (this.queue.length > 0) {
      const { toast, duration, id: queuedId } = this.queue.shift();
      this.displayToast(toast, duration, queuedId);
    }
  }

  update(id, options) {
    const toastData = this.toasts.get(id);
    if (!toastData) return;

    const { element } = toastData;
    
    if (options.title !== undefined) {
      const titleEl = element.querySelector('.toast-title');
      if (titleEl) titleEl.textContent = options.title;
    }
    
    if (options.message !== undefined) {
      const messageEl = element.querySelector('.toast-message');
      if (messageEl) messageEl.textContent = options.message;
    }

    if (options.type) {
      element.className = `toast toast-${options.type} toast-visible`;
      const iconEl = element.querySelector('.toast-icon');
      if (iconEl) iconEl.innerHTML = ICONS[options.type];
    }
  }

  dismissAll() {
    this.toasts.forEach((_, id) => this.dismiss(id));
    this.queue = [];
  }

  success(title, message, options = {}) {
    return this.show({ ...options, type: 'success', title, message });
  }

  error(title, message, options = {}) {
    return this.show({ ...options, type: 'error', title, message, duration: 8000 });
  }

  warning(title, message, options = {}) {
    return this.show({ ...options, type: 'warning', title, message });
  }

  info(title, message, options = {}) {
    return this.show({ ...options, type: 'info', title, message });
  }

  loading(title, message, options = {}) {
    return this.show({ ...options, type: 'loading', title, message, duration: 0, closable: false });
  }

  promise(promise, { loading: loadingOpts, success: successOpts, error: errorOpts }) {
    const toast = this.loading(loadingOpts.title, loadingOpts.message);

    promise
      .then((result) => {
        toast.update({ 
          type: 'success', 
          title: successOpts.title, 
          message: typeof successOpts.message === 'function' 
            ? successOpts.message(result) 
            : successOpts.message 
        });
        setTimeout(() => toast.dismiss(), 3000);
      })
      .catch((err) => {
        toast.update({ 
          type: 'error', 
          title: errorOpts.title, 
          message: typeof errorOpts.message === 'function' 
            ? errorOpts.message(err) 
            : errorOpts.message 
        });
        setTimeout(() => toast.dismiss(), 5000);
      });

    return toast;
  }
}

export const Toast = new ToastManager();
export default Toast;
