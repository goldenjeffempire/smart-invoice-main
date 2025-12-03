(function() {
  'use strict';

  const InvoiceFlow = {
    init() {
      this.initNavigation();
      this.initMobileMenu();
      this.initScrollAnimations();
      this.initScrollReveal();
      this.initParallax();
      this.initMicroInteractions();
      this.initSmoothScroll();
      this.initLazyLoading();
      this.initAccessibility();
      this.initToastSystem();
      this.initCounterAnimations();
      this.initEnhancedForms();
      this.initSkeletonLoaders();
      this.initModalSystem();
      console.log('InvoiceFlow v7.0 - Enhanced Edition initialized');
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

        if (currentScroll > lastScroll && currentScroll > 300) {
          nav.style.transform = 'translateY(-100%)';
        } else {
          nav.style.transform = 'translateY(0)';
        }

        lastScroll = currentScroll;
      };

      window.addEventListener('scroll', this.throttle(handleScroll, 16), { passive: true });
    },

    initMobileMenu() {
      const toggle = document.querySelector('.nav-mobile-toggle');
      const menu = document.querySelector('.nav-mobile-menu');
      const nav = document.querySelector('.nav');
      
      if (!toggle || !menu) return;

      toggle.addEventListener('click', () => {
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', !isExpanded);
        menu.setAttribute('aria-hidden', isExpanded);
        toggle.classList.toggle('active');
        menu.classList.toggle('active');
        document.body.classList.toggle('menu-open');
      });

      menu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          toggle.setAttribute('aria-expanded', 'false');
          menu.setAttribute('aria-hidden', 'true');
          toggle.classList.remove('active');
          menu.classList.remove('active');
          document.body.classList.remove('menu-open');
        });
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && menu.classList.contains('active')) {
          toggle.setAttribute('aria-expanded', 'false');
          menu.setAttribute('aria-hidden', 'true');
          toggle.classList.remove('active');
          menu.classList.remove('active');
          document.body.classList.remove('menu-open');
          toggle.focus();
        }
      });
    },

    initScrollAnimations() {
      const animatedElements = document.querySelectorAll('[data-animate]');
      if (!animatedElements.length) return;

      const observerOptions = {
        root: null,
        rootMargin: '0px 0px -100px 0px',
        threshold: 0.1
      };

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const animation = el.dataset.animate;
            const delay = el.dataset.delay || 0;

            setTimeout(() => {
              el.classList.add('animated', `animate-${animation}`);
            }, parseInt(delay));

            observer.unobserve(el);
          }
        });
      }, observerOptions);

      animatedElements.forEach(el => observer.observe(el));
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
        threshold: 0.15
      };

      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const delay = el.dataset.revealDelay || index * 100;

            setTimeout(() => {
              el.classList.add('revealed');
            }, parseInt(delay));

            observer.unobserve(el);
          }
        });
      }, observerOptions);

      revealElements.forEach(el => observer.observe(el));
    },

    initParallax() {
      const parallaxElements = document.querySelectorAll('[data-parallax]');
      if (!parallaxElements.length) return;

      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

      const handleParallax = () => {
        const scrollY = window.pageYOffset;

        parallaxElements.forEach(el => {
          const speed = parseFloat(el.dataset.parallax) || 0.5;
          const offset = scrollY * speed;
          el.style.transform = `translateY(${offset}px)`;
        });
      };

      window.addEventListener('scroll', this.throttle(handleParallax, 16), { passive: true });
    },

    initMicroInteractions() {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      if (!prefersReducedMotion) {
        document.querySelectorAll('.btn').forEach(btn => {
          btn.addEventListener('mouseenter', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.className = 'btn-ripple';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            btn.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
          });
        });

        document.querySelectorAll('.glass-card, .bento-card, .card-enhanced').forEach(card => {
          card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 30;
            const rotateY = (centerX - x) / 30;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
            
            const glowX = (x / rect.width) * 100;
            const glowY = (y / rect.height) * 100;
            card.style.setProperty('--glow-x', `${glowX}%`);
            card.style.setProperty('--glow-y', `${glowY}%`);
          });

          card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
          });
        });

        document.querySelectorAll('.feature-card, .stat-card').forEach(card => {
          card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
          });

          card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
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
        container.setAttribute('aria-atomic', 'false');
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
          toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
          
          if (prefersReducedMotion) {
            toast.style.animation = 'none';
          }
          
          const icons = {
            success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
            error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
            warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
          };

          toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
              ${title ? `<div class="toast-title">${title}</div>` : ''}
              ${message ? `<div class="toast-message">${message}</div>` : ''}
            </div>
            ${closable ? `<button class="toast-close" aria-label="Dismiss notification" type="button">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
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
            closeBtn.addEventListener('keydown', (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                removeToast();
              }
            });
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
          element.classList.add('counter-complete');
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
            element.classList.add('counter-complete');
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

      document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', (e) => {
          let isValid = true;
          
          form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
              isValid = false;
              field.classList.add('has-error');
              field.classList.remove('is-valid');
              
              const errorEl = field.parentNode.querySelector('.form-error');
              if (!errorEl) {
                const error = document.createElement('div');
                error.className = 'form-error';
                error.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg> This field is required';
                field.parentNode.appendChild(error);
              }
            } else {
              field.classList.remove('has-error');
              field.classList.add('is-valid');
              const errorEl = field.parentNode.querySelector('.form-error');
              if (errorEl) errorEl.remove();
            }
          });

          if (!isValid) {
            e.preventDefault();
            const firstError = form.querySelector('.has-error');
            if (firstError) {
              firstError.focus();
              firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }
        });
      });
    },

    initSkeletonLoaders() {
      window.Skeleton = {
        show(container) {
          container.dataset.originalContent = container.innerHTML;
          container.innerHTML = this.generateSkeleton(container);
          container.classList.add('loading');
        },

        hide(container) {
          if (container.dataset.originalContent) {
            container.innerHTML = container.dataset.originalContent;
            delete container.dataset.originalContent;
          }
          container.classList.remove('loading');
        },

        generateSkeleton(container) {
          const type = container.dataset.skeletonType || 'default';
          
          const skeletons = {
            card: `
              <div class="skeleton-stat-card">
                <div class="skeleton skeleton-icon"></div>
                <div class="skeleton skeleton-value"></div>
                <div class="skeleton skeleton-label"></div>
              </div>
            `,
            table: `
              <div class="skeleton-row">
                <div class="skeleton" style="width: 18px; height: 18px;"></div>
                <div class="skeleton" style="width: 100px; height: 16px;"></div>
                <div class="skeleton" style="width: 150px; height: 16px;"></div>
                <div class="skeleton" style="width: 80px; height: 16px;"></div>
                <div class="skeleton" style="width: 60px; height: 24px; border-radius: 12px;"></div>
              </div>
            `.repeat(5),
            text: `
              <div class="skeleton skeleton-title"></div>
              <div class="skeleton skeleton-text"></div>
              <div class="skeleton skeleton-text"></div>
              <div class="skeleton skeleton-text-sm"></div>
            `,
            default: `
              <div class="skeleton skeleton-card"></div>
            `
          };

          return skeletons[type] || skeletons.default;
        }
      };
    },

    initModalSystem() {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      window.Modal = {
        show(options) {
          const { title, content, actions, onClose } = options;
          const previousActiveElement = document.activeElement;
          const modalId = 'modal-' + Date.now();

          const overlay = document.createElement('div');
          overlay.className = 'modal-overlay';
          overlay.setAttribute('data-modal-overlay', modalId);
          
          const modal = document.createElement('div');
          modal.className = 'modal-container';
          modal.setAttribute('role', 'dialog');
          modal.setAttribute('aria-modal', 'true');
          modal.setAttribute('tabindex', '-1');
          modal.setAttribute('data-modal', modalId);
          if (title) modal.setAttribute('aria-labelledby', 'modal-title-' + modalId);
          
          if (prefersReducedMotion) {
            overlay.style.transition = 'opacity 0.01ms';
            modal.style.transition = 'opacity 0.01ms';
          }

          modal.innerHTML = `
            <div class="modal-header">
              ${title ? `<h2 class="modal-title" id="modal-title-${modalId}">${title}</h2>` : ''}
              <button class="modal-close" aria-label="Close dialog" type="button">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div class="modal-body">${content || ''}</div>
            ${actions ? `<div class="modal-actions">${actions}</div>` : ''}
          `;

          document.body.appendChild(overlay);
          document.body.appendChild(modal);
          document.body.style.overflow = 'hidden';

          const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          const firstFocusable = focusableElements[0];
          const lastFocusable = focusableElements[focusableElements.length - 1];

          const trapFocus = (e) => {
            if (e.key !== 'Tab') return;
            
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
          };

          requestAnimationFrame(() => {
            overlay.classList.add('active');
            modal.classList.add('active');
            if (firstFocusable) firstFocusable.focus();
          });

          const close = () => {
            modal.removeEventListener('keydown', trapFocus);
            document.removeEventListener('keydown', escHandler);
            
            if (prefersReducedMotion) {
              overlay.remove();
              modal.remove();
              document.body.style.overflow = '';
              if (previousActiveElement && previousActiveElement.focus) {
                previousActiveElement.focus();
              }
              if (onClose) onClose();
            } else {
              overlay.classList.remove('active');
              modal.classList.remove('active');
              setTimeout(() => {
                overlay.remove();
                modal.remove();
                document.body.style.overflow = '';
                if (previousActiveElement && previousActiveElement.focus) {
                  previousActiveElement.focus();
                }
                if (onClose) onClose();
              }, 300);
            }
          };

          const escHandler = (e) => {
            if (e.key === 'Escape') {
              close();
            }
          };

          overlay.addEventListener('click', close);
          modal.querySelector('.modal-close').addEventListener('click', close);
          modal.addEventListener('keydown', trapFocus);
          document.addEventListener('keydown', escHandler);

          return { close, modal };
        },

        confirm(options) {
          return new Promise((resolve) => {
            const { title, message, confirmText = 'Confirm', cancelText = 'Cancel', type = 'primary' } = options;
            
            const { close, modal } = this.show({
              title,
              content: `<p>${message}</p>`,
              actions: `
                <button class="btn btn-secondary modal-cancel" type="button">${cancelText}</button>
                <button class="btn btn-${type} modal-confirm" type="button">${confirmText}</button>
              `,
              onClose: () => resolve(false)
            });

            modal.querySelector('.modal-cancel').addEventListener('click', () => {
              close();
              resolve(false);
            });

            modal.querySelector('.modal-confirm').addEventListener('click', () => {
              close();
              resolve(true);
            });
          });
        }
      };
    },

    showConfetti() {
      const container = document.createElement('div');
      container.className = 'confetti-container';
      document.body.appendChild(container);

      const colors = ['#6366f1', '#8b5cf6', '#a855f7', '#10b981', '#f59e0b', '#ef4444'];
      
      for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 2 + 's';
        confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
        container.appendChild(confetti);
      }

      setTimeout(() => container.remove(), 5000);
    },

    throttle(func, limit) {
      let inThrottle;
      return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
          func.apply(context, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    },

    debounce(func, wait) {
      let timeout;
      return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
      };
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => InvoiceFlow.init());
  } else {
    InvoiceFlow.init();
  }

  window.InvoiceFlow = InvoiceFlow;
})();
