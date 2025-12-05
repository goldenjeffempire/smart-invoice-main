(function() {
  'use strict';

  const InvoiceFlow = {
    init() {
      this.initNavigation();
      this.initMobileMenu();
      this.initAppSidebar();
      this.initScrollReveal();
      this.initMicroInteractions();
      this.initSmoothScroll();
      this.initLazyLoading();
      this.initAccessibility();
      this.initToastSystem();
      this.initCounterAnimations();
      this.initEnhancedForms();
      this.initModalSystem();
      console.log('InvoiceFlow v8.0 - Premium Edition initialized');
    },

    initAppSidebar() {
      const mobileToggle = document.querySelector('.mobile-menu-toggle');
      const sidebar = document.querySelector('.app-sidebar, .dashboard-sidebar');
      
      if (!mobileToggle || !sidebar) return;

      let overlay = document.querySelector('.sidebar-overlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
      }

      const openSidebar = () => {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        mobileToggle.setAttribute('aria-expanded', 'true');
      };

      const closeSidebar = () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        mobileToggle.setAttribute('aria-expanded', 'false');
      };

      mobileToggle.addEventListener('click', () => {
        if (sidebar.classList.contains('open')) {
          closeSidebar();
        } else {
          openSidebar();
        }
      });

      overlay.addEventListener('click', closeSidebar);

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
          closeSidebar();
        }
      });

      sidebar.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', () => {
          if (window.innerWidth <= 1024) {
            closeSidebar();
          }
        });
      });
    },

    initNavigation() {
      const nav = document.querySelector('.nav');
      if (!nav) return;

      let lastScroll = 0;
      const scrollThreshold = 50;

      const handleScroll = () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > scrollThreshold) {
          nav.classList.add('scrolled');
        } else {
          nav.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
      };

      window.addEventListener('scroll', this.throttle(handleScroll, 16), { passive: true });
      handleScroll();
    },

    initMobileMenu() {
      const toggle = document.querySelector('.nav-mobile-toggle');
      const menu = document.querySelector('.nav-mobile-menu');
      
      if (!toggle || !menu) return;

      toggle.addEventListener('click', () => {
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', !isExpanded);
        menu.setAttribute('aria-hidden', isExpanded);
        document.body.style.overflow = isExpanded ? '' : 'hidden';
      });

      menu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          toggle.setAttribute('aria-expanded', 'false');
          menu.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
        });
      });

      document.addEventListener('click', (e) => {
        if (!menu.contains(e.target) && !toggle.contains(e.target)) {
          toggle.setAttribute('aria-expanded', 'false');
          menu.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
        }
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
          toggle.setAttribute('aria-expanded', 'false');
          menu.setAttribute('aria-hidden', 'true');
          document.body.style.overflow = '';
          toggle.focus();
        }
      });
    },

    initScrollReveal() {
      const revealElements = document.querySelectorAll('[data-reveal]');
      if (!revealElements.length) return;

      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        revealElements.forEach(el => el.classList.add('revealed'));
        return;
      }

      const observerOptions = {
        root: null,
        rootMargin: '0px 0px -80px 0px',
        threshold: 0.1
      };

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const delay = el.dataset.revealDelay || 0;

            setTimeout(() => {
              el.classList.add('revealed');
            }, parseInt(delay));

            observer.unobserve(el);
          }
        });
      }, observerOptions);

      revealElements.forEach(el => observer.observe(el));
    },

    initMicroInteractions() {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      if (!prefersReducedMotion) {
        document.querySelectorAll('.feature-card').forEach(card => {
          card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px)';
          });

          card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
          });
        });

        document.querySelectorAll('.sidebar-link').forEach(link => {
          link.addEventListener('mouseenter', () => {
            link.style.transform = 'translateX(4px)';
          });

          link.addEventListener('mouseleave', () => {
            link.style.transform = 'translateX(0)';
          });
        });
      }

      document.querySelectorAll('.invoices-table tbody tr, .table-enhanced tbody tr, .dashboard-section tbody tr').forEach(row => {
        row.addEventListener('mouseenter', () => {
          row.style.background = 'rgba(99, 102, 241, 0.08)';
          row.style.transition = 'background 0.2s ease';
        });

        row.addEventListener('mouseleave', () => {
          row.style.background = '';
        });
      });
    },

    initSmoothScroll() {
      document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
          const targetId = anchor.getAttribute('href');
          if (targetId === '#') return;

          const target = document.querySelector(targetId);
          if (!target) return;

          e.preventDefault();

          const headerOffset = 80;
          const elementPosition = target.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });

          target.focus({ preventScroll: true });
        });
      });
    },

    initLazyLoading() {
      if ('loading' in HTMLImageElement.prototype) {
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        lazyImages.forEach(img => {
          if (img.dataset.src) {
            img.src = img.dataset.src;
          }
        });
      } else {
        const lazyImageObserver = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const img = entry.target;
              if (img.dataset.src) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
              }
              lazyImageObserver.unobserve(img);
            }
          });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
          lazyImageObserver.observe(img);
        });
      }
    },

    initAccessibility() {
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
          document.body.classList.add('keyboard-navigation');
        }
      });

      document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
      });

      document.querySelectorAll('[role="button"]').forEach(el => {
        el.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            el.click();
          }
        });
      });
    },

    initToastSystem() {
      if (!document.querySelector('.toast-container')) {
        const container = document.createElement('div');
        container.className = 'toast-container';
        container.setAttribute('role', 'region');
        container.setAttribute('aria-label', 'Notifications');
        container.setAttribute('aria-live', 'polite');
        document.body.appendChild(container);
      }

      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      window.Toast = {
        show(options) {
          const { type = 'info', title, message, duration = 5000, closable = true } = options;
          const container = document.querySelector('.toast-container');
          
          const toast = document.createElement('div');
          toast.className = `toast toast-${type}`;
          toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
          
          if (prefersReducedMotion) {
            toast.style.animation = 'none';
          }
          
          const icons = {
            success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
            error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
            warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
          };

          toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
              ${title ? `<div class="toast-title">${title}</div>` : ''}
              ${message ? `<div class="toast-message">${message}</div>` : ''}
            </div>
            ${closable ? `<button class="toast-close" aria-label="Dismiss notification">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>` : ''}
          `;

          container.appendChild(toast);

          const closeBtn = toast.querySelector('.toast-close');
          const removeToast = () => {
            if (prefersReducedMotion) {
              toast.remove();
            } else {
              toast.classList.add('toast-exiting');
              setTimeout(() => toast.remove(), 300);
            }
          };

          if (closeBtn) {
            closeBtn.addEventListener('click', removeToast);
          }

          if (duration > 0) {
            setTimeout(removeToast, duration);
          }

          return toast;
        },

        success(title, message, duration) {
          return this.show({ type: 'success', title, message, duration });
        },

        error(title, message, duration) {
          return this.show({ type: 'error', title, message, duration });
        },

        warning(title, message, duration) {
          return this.show({ type: 'warning', title, message, duration });
        },

        info(title, message, duration) {
          return this.show({ type: 'info', title, message, duration });
        }
      };
    },

    initCounterAnimations() {
      const counters = document.querySelectorAll('[data-counter]');
      if (!counters.length) return;

      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      const animateCounter = (element) => {
        const target = parseInt(element.dataset.counter);
        const suffix = element.dataset.counterSuffix || '';
        const prefix = element.dataset.counterPrefix || '';

        if (prefersReducedMotion) {
          element.textContent = prefix + target.toLocaleString() + suffix;
          return;
        }

        const duration = parseInt(element.dataset.counterDuration) || 2000;
        const startTime = performance.now();

        const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);

        const updateCounter = (currentTime) => {
          const elapsed = currentTime - startTime;
          const progress = Math.min(elapsed / duration, 1);
          const easedProgress = easeOutQuart(progress);
          const current = Math.floor(easedProgress * target);

          element.textContent = prefix + current.toLocaleString() + suffix;

          if (progress < 1) {
            requestAnimationFrame(updateCounter);
          } else {
            element.textContent = prefix + target.toLocaleString() + suffix;
          }
        };

        requestAnimationFrame(updateCounter);
      };

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.5 });

      counters.forEach(counter => observer.observe(counter));
    },

    initEnhancedForms() {
      document.querySelectorAll('.form-input-enhanced').forEach(input => {
        input.addEventListener('focus', () => {
          const wrapper = input.closest('.form-group-enhanced');
          if (wrapper) wrapper.classList.add('focused');
        });

        input.addEventListener('blur', () => {
          const wrapper = input.closest('.form-group-enhanced');
          if (wrapper) wrapper.classList.remove('focused');
        });

        input.addEventListener('input', () => {
          if (input.value) {
            input.classList.add('has-value');
          } else {
            input.classList.remove('has-value');
          }
        });
      });
    },

    initModalSystem() {
      window.Modal = {
        show(options) {
          const { title, content, actions, onClose } = options;
          const previousActiveElement = document.activeElement;
          const modalId = 'modal-' + Date.now();

          const overlay = document.createElement('div');
          overlay.className = 'modal-overlay';
          overlay.id = modalId + '-overlay';

          const modal = document.createElement('div');
          modal.className = 'modal';
          modal.id = modalId;
          modal.setAttribute('role', 'dialog');
          modal.setAttribute('aria-modal', 'true');
          modal.setAttribute('aria-labelledby', modalId + '-title');

          let actionsHtml = '';
          if (actions && actions.length) {
            actionsHtml = `<div class="modal-footer">${actions.map(action => 
              `<button class="btn btn-${action.type || 'secondary'}" data-action="${action.id || ''}">${action.label}</button>`
            ).join('')}</div>`;
          }

          modal.innerHTML = `
            <div class="modal-header">
              <h3 class="modal-title" id="${modalId}-title">${title || ''}</h3>
              <button class="modal-close" aria-label="Close modal">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div class="modal-body">${content || ''}</div>
            ${actionsHtml}
          `;

          document.body.appendChild(overlay);
          document.body.appendChild(modal);
          document.body.style.overflow = 'hidden';

          requestAnimationFrame(() => {
            overlay.classList.add('active');
            modal.classList.add('active');
          });

          const closeModal = () => {
            overlay.classList.remove('active');
            modal.classList.remove('active');

            setTimeout(() => {
              overlay.remove();
              modal.remove();
              document.body.style.overflow = '';
              if (previousActiveElement) {
                previousActiveElement.focus();
              }
              if (onClose) onClose();
            }, 300);
          };

          modal.querySelector('.modal-close').addEventListener('click', closeModal);
          overlay.addEventListener('click', closeModal);

          document.addEventListener('keydown', function escHandler(e) {
            if (e.key === 'Escape') {
              closeModal();
              document.removeEventListener('keydown', escHandler);
            }
          });

          if (actions && actions.length) {
            actions.forEach(action => {
              const btn = modal.querySelector(`[data-action="${action.id}"]`);
              if (btn && action.handler) {
                btn.addEventListener('click', () => {
                  action.handler(closeModal);
                });
              }
            });
          }

          const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
          const firstFocusable = focusableElements[0];
          const lastFocusable = focusableElements[focusableElements.length - 1];

          firstFocusable.focus();

          modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
              if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                  e.preventDefault();
                  lastFocusable.focus();
                }
              } else {
                if (document.activeElement === lastFocusable) {
                  e.preventDefault();
                  firstFocusable.focus();
                }
              }
            }
          });

          return { close: closeModal, modal, overlay };
        },

        confirm(options) {
          const { title, message, confirmText = 'Confirm', cancelText = 'Cancel', onConfirm, onCancel, type = 'info' } = options;

          return this.show({
            title,
            content: `<p>${message}</p>`,
            actions: [
              { id: 'cancel', label: cancelText, type: 'secondary', handler: (close) => { if (onCancel) onCancel(); close(); } },
              { id: 'confirm', label: confirmText, type: type === 'danger' ? 'danger' : 'primary', handler: (close) => { if (onConfirm) onConfirm(); close(); } }
            ]
          });
        }
      };
    },

    throttle(func, limit) {
      let inThrottle;
      return function(...args) {
        if (!inThrottle) {
          func.apply(this, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    },

    debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    },

    formatCurrency(amount, currency = 'USD') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
      }).format(amount);
    },

    formatDate(date, options = {}) {
      const defaultOptions = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      };
      return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(new Date(date));
    }
  };

  document.addEventListener('DOMContentLoaded', () => InvoiceFlow.init());
  window.InvoiceFlow = InvoiceFlow;
})();
