/**
 * InvoiceFlow Enhanced Lazy Loading Module
 * Progressive enhancement with IntersectionObserver
 * Fallback for browsers without native lazy loading
 */

(function() {
  'use strict';

  var config = {
    rootMargin: '50px 0px 200px 0px',
    threshold: 0.01,
    loadedClass: 'lazy-loaded',
    loadingClass: 'lazy-loading',
    errorClass: 'lazy-error'
  };

  var supportsNativeLazyLoading = 'loading' in HTMLImageElement.prototype;
  var supportsIntersectionObserver = 'IntersectionObserver' in window;

  function init() {
    var dataImages = document.querySelectorAll('img[data-src]');
    var lazyBackgrounds = document.querySelectorAll('[data-bg]');

    enhanceNativeImages();

    if (dataImages.length > 0) {
      if (supportsIntersectionObserver) {
        observeImages(dataImages);
      } else {
        loadAllImmediately(dataImages, []);
      }
    }

    if (lazyBackgrounds.length > 0) {
      if (supportsIntersectionObserver) {
        observeBackgrounds(lazyBackgrounds);
      } else {
        loadAllImmediately([], lazyBackgrounds);
      }
    }
  }

  function enhanceNativeImages() {
    var images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(function(img) {
      if (img.complete) {
        img.classList.add(config.loadedClass);
      } else {
        img.classList.add(config.loadingClass);
        img.addEventListener('load', function() {
          img.classList.remove(config.loadingClass);
          img.classList.add(config.loadedClass);
        });
        img.addEventListener('error', function() {
          img.classList.remove(config.loadingClass);
          img.classList.add(config.errorClass);
        });
      }
    });
  }

  function observeImages(images) {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          loadImage(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: config.rootMargin,
      threshold: config.threshold
    });

    images.forEach(function(img) {
      observer.observe(img);
    });
  }

  function observeBackgrounds(elements) {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          loadBackground(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: config.rootMargin,
      threshold: config.threshold
    });

    elements.forEach(function(el) {
      observer.observe(el);
    });
  }

  function loadImage(img) {
    var src = img.dataset.src || img.getAttribute('data-src');
    var srcset = img.dataset.srcset || img.getAttribute('data-srcset');
    var sizes = img.dataset.sizes || img.getAttribute('data-sizes');

    if (!src && img.src) {
      img.classList.add(config.loadedClass);
      return;
    }

    img.classList.add(config.loadingClass);

    if (srcset) {
      img.srcset = srcset;
    }
    if (sizes) {
      img.sizes = sizes;
    }
    if (src) {
      img.src = src;
    }

    img.addEventListener('load', function() {
      img.classList.remove(config.loadingClass);
      img.classList.add(config.loadedClass);
      img.removeAttribute('data-src');
      img.removeAttribute('data-srcset');
      img.removeAttribute('data-sizes');
    });

    img.addEventListener('error', function() {
      img.classList.remove(config.loadingClass);
      img.classList.add(config.errorClass);
    });
  }

  function loadBackground(el) {
    var bg = el.dataset.bg || el.getAttribute('data-bg');
    if (bg) {
      el.style.backgroundImage = 'url(' + bg + ')';
      el.classList.add(config.loadedClass);
      el.removeAttribute('data-bg');
    }
  }

  function loadAllImmediately(images, backgrounds) {
    images.forEach(function(img) {
      loadImage(img);
    });
    backgrounds.forEach(function(el) {
      loadBackground(el);
    });
  }

  function preloadImage(src) {
    return new Promise(function(resolve, reject) {
      var img = new Image();
      img.onload = function() { resolve(img); };
      img.onerror = reject;
      img.src = src;
    });
  }

  function preloadCriticalImages() {
    var criticalImages = document.querySelectorAll('img[fetchpriority="high"], img[data-critical]');
    criticalImages.forEach(function(img) {
      if (img.dataset.src) {
        preloadImage(img.dataset.src).then(function() {
          loadImage(img);
        });
      }
    });
  }

  window.LazyImages = {
    init: init,
    loadImage: loadImage,
    preloadImage: preloadImage,
    preloadCriticalImages: preloadCriticalImages
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
