/**
 * SMART INVOICE - Unified Application JavaScript
 * Modern, performant, accessible interactions
 * Version: 2.0
 */

(function() {
    'use strict';

    // ========== PAGE LOADER ==========
    class PageLoader {
        constructor() {
            this.loader = document.querySelector('.page-loader');
            this.init();
        }

        init() {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    if (this.loader) {
                        this.loader.classList.add('hidden');
                    }
                }, 300);
            });
        }
    }

    // ========== TOAST NOTIFICATION SYSTEM ==========
    class ToastManager {
        constructor() {
            this.container = this.createContainer();
        }

        createContainer() {
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.className = 'fixed top-4 right-4 z-50 space-y-2 pointer-events-none';
                container.style.zIndex = '1700';
                document.body.appendChild(container);
            }
            return container;
        }

        show(message, type = 'info', duration = 5000) {
            const toast = document.createElement('div');
            
            const icons = {
                success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
                error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
                warning: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
                info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>'
            };

            const colors = {
                success: 'bg-green-500',
                error: 'bg-red-500',
                warning: 'bg-yellow-500',
                info: 'bg-blue-500'
            };

            toast.className = `${colors[type]} text-white px-6 py-4 rounded-lg shadow-xl flex items-center space-x-3 transform transition-all duration-300 translate-x-full opacity-0 max-w-md pointer-events-auto`;
            toast.innerHTML = `
                <div class="flex-shrink-0">${icons[type]}</div>
                <div class="flex-1 font-medium">${message}</div>
                <button class="flex-shrink-0 hover:bg-white/20 rounded p-1 transition" onclick="this.parentElement.remove()" aria-label="Close notification">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
                </button>
            `;

            this.container.appendChild(toast);

            requestAnimationFrame(() => {
                toast.classList.remove('translate-x-full', 'opacity-0');
            });

            if (duration > 0) {
                setTimeout(() => {
                    toast.classList.add('translate-x-full', 'opacity-0');
                    setTimeout(() => toast.remove(), 300);
                }, duration);
            }
        }
    }

    // ========== FORM VALIDATION & ENHANCEMENT ==========
    class FormEnhancer {
        constructor() {
            this.forms = document.querySelectorAll('form[data-validate]');
            this.init();
        }

        init() {
            this.forms.forEach(form => {
                form.addEventListener('submit', (e) => this.handleSubmit(e, form));
                
                const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
                inputs.forEach(input => {
                    input.addEventListener('blur', () => this.validateField(input));
                    input.addEventListener('input', () => this.clearError(input));
                });
            });
        }

        validateField(field) {
            const value = field.value.trim();
            const type = field.type;
            let error = null;

            if (field.hasAttribute('required') && !value) {
                error = 'This field is required';
            } else if (type === 'email' && value && !this.isValidEmail(value)) {
                error = 'Please enter a valid email address';
            } else if (type === 'url' && value && !this.isValidUrl(value)) {
                error = 'Please enter a valid URL';
            } else if (field.hasAttribute('minlength')) {
                const min = parseInt(field.getAttribute('minlength'));
                if (value.length < min) {
                    error = `Minimum length is ${min} characters`;
                }
            }

            if (error) {
                this.showError(field, error);
                return false;
            } else {
                this.clearError(field);
                return true;
            }
        }

        showError(field, message) {
            this.clearError(field);
            field.classList.add('border-red-500');
            field.setAttribute('aria-invalid', 'true');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = message;
            errorDiv.setAttribute('role', 'alert');
            field.parentNode.appendChild(errorDiv);
        }

        clearError(field) {
            field.classList.remove('border-red-500');
            field.removeAttribute('aria-invalid');
            const errorDiv = field.parentNode.querySelector('.form-error');
            if (errorDiv) {
                errorDiv.remove();
            }
        }

        handleSubmit(e, form) {
            let isValid = true;
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            
            inputs.forEach(input => {
                if (!this.validateField(input)) {
                    isValid = false;
                }
            });

            if (!isValid) {
                e.preventDefault();
                window.toast.show('Please fix the errors in the form', 'error');
            }
        }

        isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        }

        isValidUrl(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        }
    }

    // ========== MODAL MANAGER ==========
    class ModalManager {
        constructor() {
            this.init();
        }

        init() {
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-modal-trigger]')) {
                    const modalId = e.target.getAttribute('data-modal-trigger');
                    this.open(modalId);
                } else if (e.target.matches('[data-modal-close]') || e.target.classList.contains('modal-backdrop')) {
                    this.close(e.target.closest('.modal-backdrop'));
                }
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    const openModal = document.querySelector('.modal-backdrop');
                    if (openModal) {
                        this.close(openModal);
                    }
                }
            });
        }

        open(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
                modal.classList.add('animate-fade-in');
                document.body.style.overflow = 'hidden';
                
                const firstFocusable = modal.querySelector('button, input, select, textarea, a[href]');
                if (firstFocusable) {
                    setTimeout(() => firstFocusable.focus(), 100);
                }
            }
        }

        close(backdrop) {
            if (backdrop) {
                backdrop.classList.add('opacity-0');
                setTimeout(() => {
                    backdrop.classList.add('hidden');
                    backdrop.classList.remove('opacity-0', 'animate-fade-in');
                    document.body.style.overflow = '';
                }, 200);
            }
        }
    }

    // ========== INTERSECTION OBSERVER FOR ANIMATIONS ==========
    class AnimationObserver {
        constructor() {
            this.init();
        }

        init() {
            const fadeElements = document.querySelectorAll('.fade-up, .fade-in-view');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('opacity-100', 'translate-y-0', 'animate-fade-in');
                        entry.target.classList.remove('opacity-0', 'translate-y-8');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            fadeElements.forEach(el => {
                el.classList.add('opacity-0', 'translate-y-8', 'transition-all', 'duration-700');
                observer.observe(el);
            });

            const counters = document.querySelectorAll('.counter');
            const counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            counters.forEach(counter => counterObserver.observe(counter));
        }

        animateCounter(element) {
            const target = parseInt(element.getAttribute('data-target') || element.textContent);
            const suffix = element.getAttribute('data-suffix') || '';
            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    element.textContent = Math.floor(current).toLocaleString() + suffix;
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = target.toLocaleString() + suffix;
                }
            };

            updateCounter();
        }
    }

    // ========== SMOOTH SCROLL ==========
    class SmoothScroll {
        constructor() {
            this.init();
        }

        init() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => {
                    const href = anchor.getAttribute('href');
                    if (href !== '#' && href !== '') {
                        e.preventDefault();
                        const target = document.querySelector(href);
                        if (target) {
                            const offset = 80;
                            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                            window.scrollTo({
                                top: targetPosition,
                                behavior: 'smooth'
                            });
                        }
                    }
                });
            });
        }
    }

    // ========== CONFIRMATION DIALOGS ==========
    class ConfirmDialog {
        constructor() {
            this.init();
        }

        init() {
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-confirm]')) {
                    const message = e.target.getAttribute('data-confirm');
                    if (!confirm(message)) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }
            });
        }
    }

    // ========== TOOLTIPS ==========
    class TooltipManager {
        constructor() {
            this.init();
        }

        init() {
            const tooltips = document.querySelectorAll('[data-tooltip]');
            tooltips.forEach(el => {
                el.addEventListener('mouseenter', () => this.show(el));
                el.addEventListener('mouseleave', () => this.hide(el));
                el.addEventListener('focus', () => this.show(el));
                el.addEventListener('blur', () => this.hide(el));
            });
        }

        show(element) {
            const text = element.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip fixed bg-gray-900 text-white text-sm px-3 py-2 rounded shadow-lg z-50 pointer-events-none';
            tooltip.style.zIndex = '1600';
            tooltip.textContent = text;
            tooltip.id = `tooltip-${Date.now()}`;
            document.body.appendChild(tooltip);

            const rect = element.getBoundingClientRect();
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;

            element.setAttribute('data-tooltip-id', tooltip.id);
        }

        hide(element) {
            const tooltipId = element.getAttribute('data-tooltip-id');
            if (tooltipId) {
                const tooltip = document.getElementById(tooltipId);
                if (tooltip) {
                    tooltip.remove();
                }
                element.removeAttribute('data-tooltip-id');
            }
        }
    }

    // ========== AUTO-DISMISS ALERTS ==========
    class AlertManager {
        constructor() {
            this.init();
        }

        init() {
            const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
            alerts.forEach(alert => {
                const duration = parseInt(alert.getAttribute('data-auto-dismiss')) || 5000;
                setTimeout(() => {
                    alert.style.transition = 'opacity 300ms ease, transform 300ms ease';
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-10px)';
                    setTimeout(() => alert.remove(), 300);
                }, duration);
            });
        }
    }

    // ========== KEYBOARD NAVIGATION ==========
    class KeyboardNav {
        constructor() {
            this.init();
        }

        init() {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    document.body.classList.add('keyboard-nav');
                }
            });

            document.addEventListener('mousedown', () => {
                document.body.classList.remove('keyboard-nav');
            });
        }
    }

    // ========== COPY TO CLIPBOARD ==========
    class ClipboardManager {
        constructor() {
            this.init();
        }

        init() {
            document.addEventListener('click', async (e) => {
                if (e.target.matches('[data-copy]')) {
                    const text = e.target.getAttribute('data-copy');
                    try {
                        await navigator.clipboard.writeText(text);
                        window.toast.show('Copied to clipboard!', 'success', 2000);
                    } catch (err) {
                        window.toast.show('Failed to copy', 'error');
                    }
                }
            });
        }
    }

    // ========== INITIALIZE ALL MODULES ==========
    function init() {
        new PageLoader();
        window.toast = new ToastManager();
        new FormEnhancer();
        new ModalManager();
        new AnimationObserver();
        new SmoothScroll();
        new ConfirmDialog();
        new TooltipManager();
        new AlertManager();
        new KeyboardNav();
        new ClipboardManager();

        const djangoMessages = document.querySelectorAll('.alert[role="alert"]');
        djangoMessages.forEach(msg => {
            msg.setAttribute('data-auto-dismiss', '5000');
        });

        document.body.classList.remove('no-js');
        document.body.classList.add('js-enabled');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
