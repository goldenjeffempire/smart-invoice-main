(function() {
  'use strict';

  const InvoiceFlow = {
    init() {
      this.initNavigation();
      this.initMobileMenu();
      this.initScrollAnimations();
      this.initParallax();
      this.initMicroInteractions();
      this.initSmoothScroll();
      this.initLazyLoading();
      this.initAccessibility();
      console.log('InvoiceFlow v6.0 - Enterprise Edition initialized');
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

      document.querySelectorAll('.glass-card, .bento-card').forEach(card => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        card.addEventListener('mousemove', (e) => {
          const rect = card.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          
          const rotateX = (y - centerY) / 30;
          const rotateY = (centerX - x) / 30;
          
          card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });

        card.addEventListener('mouseleave', () => {
          card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
      });

      document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
          card.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', () => {
          card.style.transform = 'translateY(0) scale(1)';
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
