/**
 * InvoiceFlow Premium Landing Page
 * Advanced Animations & Interactions v3.0
 * Performance & Accessibility Optimized
 */

(function() {
  'use strict';
  
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  const isDesktop = window.innerWidth >= 1024;
  
  let rafId = null;
  let resizeTimeout = null;
  let scrollTicking = false;
  
  function init() {
    initScrollReveal();
    initSmoothScroll();
    initFloatingCards();
    initNavScroll();
    
    if (!prefersReducedMotion && isDesktop && !isTouchDevice) {
      initParallax();
      initTiltEffect();
      initMagneticButtons();
    }
    
    initProgressAnimation();
    initChartAnimations();
    initStaggerAnimations();
    initLazyLoading();
    initFAQAccordion();
    
    window.addEventListener('resize', handleResize);
    window.addEventListener('beforeunload', cleanup);
  }
  
  function initFAQAccordion() {
    var faqItems = document.querySelectorAll('.faq-item');
    var faqButtons = [];
    
    faqItems.forEach(function(item, index) {
      var question = item.querySelector('.faq-question');
      var answer = item.querySelector('.faq-answer');
      
      if (question && answer) {
        var panelId = 'faq-panel-' + index;
        var buttonId = 'faq-button-' + index;
        
        question.setAttribute('id', buttonId);
        question.setAttribute('aria-controls', panelId);
        answer.setAttribute('id', panelId);
        answer.setAttribute('role', 'region');
        answer.setAttribute('aria-labelledby', buttonId);
        
        faqButtons.push(question);
        
        function toggleItem(open) {
          if (open) {
            faqItems.forEach(function(otherItem) {
              otherItem.classList.remove('active');
              var otherQuestion = otherItem.querySelector('.faq-question');
              var otherAnswer = otherItem.querySelector('.faq-answer');
              if (otherQuestion) {
                otherQuestion.setAttribute('aria-expanded', 'false');
              }
              if (otherAnswer) {
                otherAnswer.setAttribute('aria-hidden', 'true');
              }
            });
            
            item.classList.add('active');
            question.setAttribute('aria-expanded', 'true');
            answer.setAttribute('aria-hidden', 'false');
          } else {
            item.classList.remove('active');
            question.setAttribute('aria-expanded', 'false');
            answer.setAttribute('aria-hidden', 'true');
          }
        }
        
        question.addEventListener('click', function() {
          var isActive = item.classList.contains('active');
          toggleItem(!isActive);
        });
        
        question.addEventListener('keydown', function(e) {
          var currentIndex = faqButtons.indexOf(question);
          var lastIndex = faqButtons.length - 1;
          
          switch (e.key) {
            case 'Enter':
            case ' ':
              e.preventDefault();
              var isActive = item.classList.contains('active');
              toggleItem(!isActive);
              break;
            case 'ArrowDown':
              e.preventDefault();
              var nextIndex = currentIndex < lastIndex ? currentIndex + 1 : 0;
              faqButtons[nextIndex].focus();
              break;
            case 'ArrowUp':
              e.preventDefault();
              var prevIndex = currentIndex > 0 ? currentIndex - 1 : lastIndex;
              faqButtons[prevIndex].focus();
              break;
            case 'Home':
              e.preventDefault();
              faqButtons[0].focus();
              break;
            case 'End':
              e.preventDefault();
              faqButtons[lastIndex].focus();
              break;
          }
        });
        
        if (!item.classList.contains('active')) {
          answer.setAttribute('aria-hidden', 'true');
        } else {
          answer.setAttribute('aria-hidden', 'false');
        }
      }
    });
  }
  
  function handleResize() {
    clearTimeout(resizeTimeout);
    document.body.classList.add('resize-animation-stopper');
    
    resizeTimeout = setTimeout(function() {
      document.body.classList.remove('resize-animation-stopper');
    }, 250);
  }
  
  function cleanup() {
    if (rafId) {
      cancelAnimationFrame(rafId);
    }
    clearTimeout(resizeTimeout);
  }
  
  function initScrollReveal() {
    var observerOptions = {
      root: null,
      rootMargin: '0px 0px -80px 0px',
      threshold: 0.12
    };
    
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          
          if (entry.target.classList.contains('stagger-children')) {
            var children = entry.target.querySelectorAll('li');
            children.forEach(function(child, index) {
              child.style.animationDelay = (0.1 + index * 0.1) + 's';
            });
          }
          
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);
    
    document.querySelectorAll('[data-reveal]').forEach(function(el) {
      observer.observe(el);
    });
    
    document.querySelectorAll('.stagger-children').forEach(function(el) {
      observer.observe(el);
    });
  }
  
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
      anchor.addEventListener('click', function(e) {
        var targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        var target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          var headerOffset = 80;
          var elementPosition = target.getBoundingClientRect().top;
          var offsetPosition = elementPosition + window.pageYOffset - headerOffset;
          
          window.scrollTo({
            top: offsetPosition,
            behavior: prefersReducedMotion ? 'auto' : 'smooth'
          });
        }
      });
    });
  }
  
  function initFloatingCards() {
    if (prefersReducedMotion) return;
    
    var cards = document.querySelectorAll('.floating-card');
    
    cards.forEach(function(card) {
      var delay = parseInt(card.getAttribute('data-float-delay')) || 0;
      
      setTimeout(function() {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, delay + 600);
    });
  }
  
  function throttle(func, limit) {
    var inThrottle;
    return function() {
      var args = arguments;
      var context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(function() {
          inThrottle = false;
        }, limit);
      }
    };
  }
  
  function initParallax() {
    var parallaxElements = document.querySelectorAll('[data-parallax]');
    if (!parallaxElements.length) return;
    
    var updateParallax = throttle(function() {
      var scrollY = window.pageYOffset;
      
      parallaxElements.forEach(function(el) {
        var speed = parseFloat(el.getAttribute('data-parallax')) || 0.1;
        var rect = el.getBoundingClientRect();
        
        if (rect.top < window.innerHeight && rect.bottom > 0) {
          var centerY = rect.top + rect.height / 2;
          var viewportCenter = window.innerHeight / 2;
          var distance = centerY - viewportCenter;
          var yPos = distance * speed * 0.5;
          
          el.style.transform = 'translateY(' + yPos + 'px)';
        }
      });
    }, 16);
    
    window.addEventListener('scroll', function() {
      if (!scrollTicking) {
        rafId = requestAnimationFrame(function() {
          updateParallax();
          scrollTicking = false;
        });
        scrollTicking = true;
      }
    }, { passive: true });
  }
  
  function initTiltEffect() {
    var tiltElements = document.querySelectorAll('.tilt-element');
    
    tiltElements.forEach(function(el) {
      var container = el.closest('.perspective-container');
      if (!container) return;
      
      container.addEventListener('mousemove', function(e) {
        var rect = container.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;
        var centerX = rect.width / 2;
        var centerY = rect.height / 2;
        
        var rotateX = ((y - centerY) / centerY) * -3;
        var rotateY = ((x - centerX) / centerX) * 3;
        
        el.style.transform = 'rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg) translateZ(8px)';
      });
      
      container.addEventListener('mouseleave', function() {
        el.style.transform = 'rotateX(2deg) rotateY(-2deg)';
      });
    });
  }
  
  function initMagneticButtons() {
    var magneticBtns = document.querySelectorAll('.magnetic-btn');
    
    magneticBtns.forEach(function(btn) {
      btn.addEventListener('mousemove', function(e) {
        var rect = btn.getBoundingClientRect();
        var x = e.clientX - rect.left - rect.width / 2;
        var y = e.clientY - rect.top - rect.height / 2;
        
        var moveX = x * 0.15;
        var moveY = y * 0.15;
        
        btn.style.transform = 'translate(' + moveX + 'px, ' + moveY + 'px)';
      });
      
      btn.addEventListener('mouseleave', function() {
        btn.style.transform = '';
      });
    });
  }
  
  function initProgressAnimation() {
    var progressBars = document.querySelectorAll('.analytics-progress-bar');
    
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var progress = entry.target.style.getPropertyValue('--progress') || '0%';
          entry.target.style.width = progress;
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    
    progressBars.forEach(function(bar) {
      observer.observe(bar);
    });
    
    var stepLines = document.querySelectorAll('.step-line-progress');
    var stepObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          setTimeout(function() {
            entry.target.style.height = '100%';
          }, 200);
          stepObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.25 });
    
    stepLines.forEach(function(line) {
      stepObserver.observe(line);
    });
  }
  
  function initChartAnimations() {
    if (prefersReducedMotion) return;
    
    var chartLines = document.querySelectorAll('.chart-line, .chart-line-animated');
    
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.style.strokeDashoffset = '0';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    
    chartLines.forEach(function(line) {
      try {
        var length = line.getTotalLength ? line.getTotalLength() : 200;
        line.style.strokeDasharray = length;
        line.style.strokeDashoffset = length;
        line.style.transition = 'stroke-dashoffset 1.5s ease-out';
        observer.observe(line);
      } catch (e) {
        line.style.strokeDasharray = '200';
        line.style.strokeDashoffset = '200';
        observer.observe(line);
      }
    });
  }
  
  function initStaggerAnimations() {
    if (prefersReducedMotion) return;
    
    var staggerContainers = document.querySelectorAll('.stagger-children');
    
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var children = entry.target.children;
          Array.prototype.forEach.call(children, function(child, index) {
            child.style.opacity = '0';
            child.style.transform = 'translateX(-15px)';
            child.style.transition = 'opacity 0.4s ease-out ' + (index * 0.08) + 's, transform 0.4s ease-out ' + (index * 0.08) + 's';
            
            requestAnimationFrame(function() {
              child.style.opacity = '1';
              child.style.transform = 'translateX(0)';
            });
          });
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    
    staggerContainers.forEach(function(container) {
      observer.observe(container);
    });
  }
  
  function initNavScroll() {
    var nav = document.querySelector('.nav');
    if (!nav) return;
    
    var updateNav = throttle(function() {
      var currentScroll = window.pageYOffset;
      
      if (currentScroll > 50) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
    }, 100);
    
    window.addEventListener('scroll', updateNav, { passive: true });
  }
  
  function initLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
      var lazyImages = document.querySelectorAll('img[loading="lazy"]');
      lazyImages.forEach(function(img) {
        if (img.dataset.src) {
          img.src = img.dataset.src;
        }
      });
    }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  window.addEventListener('load', function() {
    document.body.classList.add('loaded');
    
    if (!prefersReducedMotion) {
      setTimeout(function() {
        document.querySelectorAll('.title-reveal').forEach(function(el) {
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
        });
      }, 50);
    }
  });
  
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-nav');
    }
  });
  
  document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-nav');
  });
  
})();
