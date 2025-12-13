/**
 * InvoiceFlow - Responsive Navigation System
 * Handles sidebar toggle, mobile navigation, and responsive behaviors
 */

(function() {
    'use strict';

    // State
    let sidebarOpen = false;
    let mobileNavOpen = false;
    let lastScrollY = 0;

    // DOM Elements
    const sidebar = document.querySelector('.dashboard-sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const navLanding = document.querySelector('.nav-landing');
    const navToggle = document.querySelector('.nav-landing-toggle');
    const mobileNav = document.querySelector('.mobile-nav');

    // Initialize
    function init() {
        setupSidebar();
        setupMobileNav();
        setupLandingNav();
        setupScrollBehavior();
        setupKeyboardNav();
        handleResize();
        window.addEventListener('resize', debounce(handleResize, 150));
    }

    // Sidebar functionality
    function setupSidebar() {
        if (!sidebar) return;

        // Mobile toggle
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', toggleSidebar);
        }

        // Desktop collapse toggle
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', toggleSidebarCollapse);
        }

        // Overlay click to close
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', closeSidebar);
        }

        // Restore collapsed state from localStorage
        const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        if (isCollapsed && window.innerWidth >= 1024) {
            sidebar.classList.add('is-collapsed');
        }
    }

    function toggleSidebar() {
        sidebarOpen = !sidebarOpen;
        sidebar.classList.toggle('is-open', sidebarOpen);
        
        if (sidebarOverlay) {
            sidebarOverlay.classList.toggle('is-visible', sidebarOpen);
        }
        
        if (mobileMenuToggle) {
            mobileMenuToggle.setAttribute('aria-expanded', sidebarOpen);
        }
        
        document.body.style.overflow = sidebarOpen ? 'hidden' : '';
        
        if (sidebarOpen) {
            trapFocus(sidebar);
        }
    }

    function closeSidebar() {
        sidebarOpen = false;
        sidebar.classList.remove('is-open');
        
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('is-visible');
        }
        
        if (mobileMenuToggle) {
            mobileMenuToggle.setAttribute('aria-expanded', 'false');
        }
        
        document.body.style.overflow = '';
    }

    function toggleSidebarCollapse() {
        sidebar.classList.toggle('is-collapsed');
        const isCollapsed = sidebar.classList.contains('is-collapsed');
        localStorage.setItem('sidebar-collapsed', isCollapsed);
        
        if (sidebarToggle) {
            sidebarToggle.setAttribute('aria-expanded', !isCollapsed);
        }
    }

    // Mobile navigation for landing pages
    function setupMobileNav() {
        if (!navToggle || !mobileNav) return;

        navToggle.addEventListener('click', toggleMobileNav);

        // Close when clicking links
        const mobileLinks = mobileNav.querySelectorAll('.mobile-nav-link, .mobile-nav-btn');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                closeMobileNav();
            });
        });
    }

    function toggleMobileNav() {
        mobileNavOpen = !mobileNavOpen;
        mobileNav.classList.toggle('is-open', mobileNavOpen);
        navToggle.setAttribute('aria-expanded', mobileNavOpen);
        document.body.style.overflow = mobileNavOpen ? 'hidden' : '';
        
        if (mobileNavOpen) {
            trapFocus(mobileNav);
        }
    }

    function closeMobileNav() {
        mobileNavOpen = false;
        mobileNav.classList.remove('is-open');
        
        if (navToggle) {
            navToggle.setAttribute('aria-expanded', 'false');
        }
        
        document.body.style.overflow = '';
    }

    // Landing page navigation scroll behavior
    function setupLandingNav() {
        if (!navLanding) return;

        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            
            if (scrollY > 50) {
                navLanding.classList.add('is-scrolled');
            } else {
                navLanding.classList.remove('is-scrolled');
            }
            
            lastScrollY = scrollY;
        }, { passive: true });
    }

    // Scroll behavior
    function setupScrollBehavior() {
        // Close mobile menus on scroll
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                if (mobileNavOpen && Math.abs(window.scrollY - lastScrollY) > 100) {
                    closeMobileNav();
                }
            }, 100);
        }, { passive: true });
    }

    // Keyboard navigation
    function setupKeyboardNav() {
        document.addEventListener('keydown', (e) => {
            // Escape to close menus
            if (e.key === 'Escape') {
                if (sidebarOpen) {
                    closeSidebar();
                    mobileMenuToggle?.focus();
                }
                if (mobileNavOpen) {
                    closeMobileNav();
                    navToggle?.focus();
                }
            }
        });
    }

    // Handle window resize
    function handleResize() {
        const width = window.innerWidth;
        
        // Close mobile sidebar on larger screens
        if (width >= 768 && sidebarOpen) {
            closeSidebar();
        }
        
        // Close mobile nav on larger screens
        if (width >= 768 && mobileNavOpen) {
            closeMobileNav();
        }
    }

    // Focus trap for modals/sidebars
    function trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        firstElement.focus();
        
        element.addEventListener('keydown', function handleTab(e) {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        });
    }

    // Utility: Debounce
    function debounce(func, wait) {
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

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
