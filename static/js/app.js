/**
 * INVOICEFLOW - Unified Application JavaScript v3.0
 * Modern, performant, accessible interactions with zero duplication
 * All features consolidated from app.js + ui-enhancements.js
 */

(function() {
    'use strict';

    // ========== CONFIGURATION ==========
    const CONFIG = {
        toast: {
            defaultDuration: 5000,
            zIndex: 1700
        },
        animations: {
            observerThreshold: 0.1,
            observerMargin: '0px 0px -100px 0px',
            staggerDelay: 100,
            counterDuration: 2000
        },
        navbar: {
            scrollThreshold: 10
        }
    };

    // ========== UTILITIES ==========
    const Utils = {
        isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },

        isValidUrl(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        },

        debounce(func, wait) {
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
    };

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
                    document.body.classList.add('animate-page-enter');
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
                container.style.zIndex = CONFIG.toast.zIndex;
                document.body.appendChild(container);
            }
            return container;
        }

        show(message, type = 'info', duration = CONFIG.toast.defaultDuration) {
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

            this.setupFormInteractions();
        }

        setupFormInteractions() {
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.closest('.form-group')?.classList.add('focused');
                });
                input.addEventListener('blur', function() {
                    if (!this.value) {
                        this.closest('.form-group')?.classList.remove('focused');
                    }
                });
            });
        }

        validateField(field) {
            const value = field.value.trim();
            const type = field.type;
            let error = null;

            if (field.hasAttribute('required') && !value) {
                error = 'This field is required';
            } else if (type === 'email' && value && !Utils.isValidEmail(value)) {
                error = 'Please enter a valid email address';
            } else if (type === 'url' && value && !Utils.isValidUrl(value)) {
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
            field.classList.add('border-red-500', 'form-input-error');
            field.setAttribute('aria-invalid', 'true');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = message;
            errorDiv.setAttribute('role', 'alert');
            field.parentNode.appendChild(errorDiv);
        }

        clearError(field) {
            field.classList.remove('border-red-500', 'form-input-error');
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

    // ========== UNIFIED ANIMATION OBSERVER ==========
    class AnimationObserver {
        constructor() {
            this.init();
        }

        init() {
            this.setupScrollAnimations();
            this.setupStaggerAnimations();
            this.setupCounterAnimations();
            this.setupLazyLoadImages();
        }

        setupScrollAnimations() {
            const fadeElements = document.querySelectorAll('.fade-up, .fade-in-view, [data-animate]');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('opacity-100', 'translate-y-0', 'animate-slide-in-up');
                        entry.target.classList.remove('opacity-0', 'translate-y-8');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: CONFIG.animations.observerThreshold,
                rootMargin: CONFIG.animations.observerMargin
            });

            fadeElements.forEach(el => {
                el.classList.add('opacity-0', 'translate-y-8', 'transition-all', 'duration-700');
                observer.observe(el);
            });
        }

        setupStaggerAnimations() {
            const staggerElements = document.querySelectorAll('[data-stagger]');
            staggerElements.forEach((el, index) => {
                el.style.animationDelay = `${index * CONFIG.animations.staggerDelay}ms`;
            });
        }

        setupCounterAnimations() {
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

        setupLazyLoadImages() {
            if (!('IntersectionObserver' in window)) return;

            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.add('fade-in');
                        }
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }

        animateCounter(element) {
            const target = parseInt(element.getAttribute('data-target') || element.textContent);
            const prefix = element.getAttribute('data-prefix') || '';
            const suffix = element.getAttribute('data-suffix') || '';
            const duration = CONFIG.animations.counterDuration;
            const increment = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    element.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = prefix + target.toLocaleString() + suffix;
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
                        const target = document.querySelector(href);
                        if (target) {
                            e.preventDefault();
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

    // ========== NAVBAR SCROLL EFFECTS ==========
    class NavbarEffects {
        constructor() {
            this.navbar = document.querySelector('nav');
            if (this.navbar) {
                this.init();
            }
        }

        init() {
            const handleScroll = Utils.debounce(() => {
                if (window.scrollY > CONFIG.navbar.scrollThreshold) {
                    this.navbar.classList.add('shadow-md', 'backdrop-blur-sm');
                } else {
                    this.navbar.classList.remove('shadow-md', 'backdrop-blur-sm');
                }
            }, 10);

            window.addEventListener('scroll', handleScroll, { passive: true });
        }
    }

    // ========== BUTTON RIPPLE EFFECT ==========
    class RippleEffect {
        constructor() {
            this.init();
        }

        init() {
            document.addEventListener('click', (e) => {
                const button = e.target.closest('button, a.btn');
                if (button && !button.hasAttribute('data-no-ripple')) {
                    this.createRipple(e, button);
                }
            });
        }

        createRipple(e, element) {
            const ripple = document.createElement('span');
            const rect = element.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');

            element.style.position = element.style.position || 'relative';
            element.style.overflow = 'hidden';
            element.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        }
    }

    // ========== TOOLTIP MANAGER ==========
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
            tooltip.className = 'tooltip fixed bg-gray-900 text-white text-sm px-3 py-2 rounded shadow-lg z-50 pointer-events-none animate-fade-in';
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

    // ========== ALERT MANAGER ==========
    class AlertManager {
        constructor() {
            this.init();
        }

        init() {
            const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
            alerts.forEach(alert => {
                const duration = parseInt(alert.getAttribute('data-auto-dismiss')) || CONFIG.toast.defaultDuration;
                setTimeout(() => {
                    alert.style.transition = 'opacity 300ms ease, transform 300ms ease';
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-10px)';
                    setTimeout(() => alert.remove(), 300);
                }, duration);
            });

            const djangoMessages = document.querySelectorAll('.alert[role="alert"]:not([data-auto-dismiss])');
            djangoMessages.forEach(msg => {
                msg.setAttribute('data-auto-dismiss', CONFIG.toast.defaultDuration.toString());
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

    // ========== ANALYTICS & EVENT TRACKING ==========
    class AnalyticsTracker {
        constructor() {
            this.sessionId = this.generateSessionId();
            this.init();
        }

        generateSessionId() {
            return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }

        init() {
            // Only initialize tracking if consent is given
            if (!this.hasConsent()) {
                console.log('[Analytics] Tracking disabled - no consent');
                return;
            }
            
            this.trackPageView();
            this.trackButtonClicks();
            this.trackFormSubmissions();
            this.trackScrollDepth();
            this.trackTimeOnPage();
        }

        track(eventName, properties = {}) {
            const event = {
                event: eventName,
                timestamp: new Date().toISOString(),
                sessionId: this.sessionId,
                url: window.location.href,
                referrer: document.referrer,
                userAgent: navigator.userAgent,
                ...properties
            };

            console.log('[Analytics]', event);
            
            // Send to backend if consent given (check for consent cookie)
            if (this.hasConsent()) {
                this.sendToBackend(event);
            }
        }

        hasConsent() {
            // Check for analytics consent cookie - default to FALSE for GDPR compliance
            return document.cookie.includes('analytics_consent=true');
        }

        sendToBackend(event) {
            // Send event to backend for processing
            if (navigator.sendBeacon) {
                navigator.sendBeacon('/api/analytics/', JSON.stringify(event));
            } else {
                fetch('/api/analytics/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(event),
                    keepalive: true
                }).catch(err => console.warn('Analytics send failed:', err));
            }
        }

        trackPageView() {
            this.track('page_view', {
                title: document.title,
                path: window.location.pathname
            });
        }

        trackButtonClicks() {
            document.addEventListener('click', (e) => {
                const button = e.target.closest('button, a.btn, [role="button"]');
                if (button) {
                    this.track('button_click', {
                        label: button.textContent.trim().substring(0, 50),
                        href: button.href || null,
                        type: button.tagName.toLowerCase()
                    });
                }

                // Track CTA clicks specifically
                if (e.target.closest('[href*="signup"]')) {
                    this.track('cta_click', {
                        location: this.getElementLocation(e.target),
                        text: e.target.textContent.trim()
                    });
                }
            });
        }

        trackFormSubmissions() {
            document.addEventListener('submit', (e) => {
                if (e.target.tagName === 'FORM') {
                    const formId = e.target.id || 'unnamed-form';
                    const formAction = e.target.action || window.location.href;
                    
                    this.track('form_submit', {
                        formId: formId,
                        action: formAction,
                        method: e.target.method || 'GET'
                    });
                }
            });
        }

        trackScrollDepth() {
            let maxScroll = 0;
            const updateMaxScroll = Utils.debounce(() => {
                const scrolled = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
                if (scrolled > maxScroll) {
                    maxScroll = scrolled;
                    if (maxScroll >= 25 && maxScroll < 50) {
                        this.track('scroll_depth', {depth: '25%'});
                    } else if (maxScroll >= 50 && maxScroll < 75) {
                        this.track('scroll_depth', {depth: '50%'});
                    } else if (maxScroll >= 75 && maxScroll < 90) {
                        this.track('scroll_depth', {depth: '75%'});
                    } else if (maxScroll >= 90) {
                        this.track('scroll_depth', {depth: '90%+'});
                    }
                }
            }, 500);

            window.addEventListener('scroll', updateMaxScroll);
        }

        trackTimeOnPage() {
            const startTime = Date.now();
            
            window.addEventListener('beforeunload', () => {
                const timeOnPage = Math.round((Date.now() - startTime) / 1000);
                this.track('time_on_page', {
                    seconds: timeOnPage,
                    minutes: Math.round(timeOnPage / 60)
                });
            });
        }

        getElementLocation(element) {
            let location = 'unknown';
            const closestSection = element.closest('section');
            if (closestSection) {
                location = closestSection.className.split(' ')[0] || 'section';
            }
            return location;
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
        new NavbarEffects();
        new RippleEffect();
        new TooltipManager();
        new AlertManager();
        new ConfirmDialog();
        new KeyboardNav();
        new ClipboardManager();
        window.analytics = new AnalyticsTracker();

        document.body.classList.remove('no-js');
        document.body.classList.add('js-enabled');

        console.log('InvoiceFlow v3.0 initialized successfully');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
