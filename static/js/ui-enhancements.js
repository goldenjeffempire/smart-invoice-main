// ========== MODERN UI/UX ENHANCEMENTS ==========

document.addEventListener('DOMContentLoaded', function() {
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href !== '#' && document.querySelector(href)) {
        e.preventDefault();
        document.querySelector(href).scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Stagger animations for list items
  const staggerElements = document.querySelectorAll('.fade-up, [data-stagger]');
  staggerElements.forEach((el, index) => {
    el.style.animationDelay = `${index * 0.1}s`;
  });

  // Form interactions
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

  // Intersection Observer for scroll animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-slide-in-up');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('[data-animate]').forEach(el => {
    observer.observe(el);
  });

  // Navbar scroll effect
  const navbar = document.querySelector('nav');
  if (navbar) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 10) {
        navbar.classList.add('shadow-md', 'backdrop-blur-sm');
      } else {
        navbar.classList.remove('shadow-md', 'backdrop-blur-sm');
      }
    });
  }

  // Button ripple effect
  document.querySelectorAll('button, a.btn').forEach(button => {
    button.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';
      ripple.classList.add('ripple');

      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // Lazy loading images
  if ('IntersectionObserver' in window) {
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

  // Smooth page transitions
  window.addEventListener('load', function() {
    document.body.classList.add('animate-page-enter');
  });

  // Tooltip functionality
  document.querySelectorAll('[data-tooltip]').forEach(el => {
    el.addEventListener('mouseenter', function() {
      const tooltip = document.createElement('div');
      tooltip.className = 'absolute bg-gray-900 text-white px-3 py-1 rounded text-sm whitespace-nowrap z-50 animate-fade-in';
      tooltip.textContent = this.dataset.tooltip;
      document.body.appendChild(tooltip);

      const rect = this.getBoundingClientRect();
      tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
      tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';

      this.addEventListener('mouseleave', () => tooltip.remove(), { once: true });
    });
  });
});
