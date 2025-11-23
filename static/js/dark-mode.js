/**
 * Enhanced Dark Mode System for Smart Invoice
 * Features: smooth transitions, system preference detection, auto-switching, animations
 */

class DarkModeManager {
    constructor() {
        this.darkModeKey = 'smartinvoice-dark-mode';
        this.transitionDuration = 300;
        this.init();
    }

    init() {
        // LIGHT MODE IS THE ABSOLUTE DEFAULT
        // Remove dark class first to prevent any flashing
        document.documentElement.classList.remove('dark');
        document.documentElement.style.colorScheme = 'light';
        
        const savedTheme = localStorage.getItem(this.darkModeKey);
        const isDark = savedTheme === 'dark';
        
        if (isDark) {
            // User previously chose dark mode, apply it
            this.enableDarkMode(true);
        } else {
            // Default to light mode - always
            this.enableLightMode(true);
            // Ensure light mode is saved
            localStorage.setItem(this.darkModeKey, 'light');
        }
        
        this.setupToggleButton();
        this.setupSystemPreferenceListener();
        this.setupTransitionListeners();
    }

    /**
     * Enable dark mode with smooth transition
     */
    enableDarkMode(skipTransition = false) {
        if (!skipTransition) {
            this.addTransitionClass();
        }
        
        document.documentElement.classList.add('dark');
        document.body.setAttribute('data-theme', 'dark');
        localStorage.setItem(this.darkModeKey, 'dark');
        
        this.updateToggleButton(true);
        this.applyDarkModeStyles();
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme: 'dark' }
        }));
        
        if (!skipTransition) {
            setTimeout(() => this.removeTransitionClass(), this.transitionDuration);
        }
    }

    /**
     * Enable light mode with smooth transition
     */
    enableLightMode(skipTransition = false) {
        if (!skipTransition) {
            this.addTransitionClass();
        }
        
        document.documentElement.classList.remove('dark');
        document.body.setAttribute('data-theme', 'light');
        localStorage.setItem(this.darkModeKey, 'light');
        
        this.updateToggleButton(false);
        this.applyLightModeStyles();
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme: 'light' }
        }));
        
        if (!skipTransition) {
            setTimeout(() => this.removeTransitionClass(), this.transitionDuration);
        }
    }

    /**
     * Toggle between dark and light modes
     */
    toggle() {
        if (document.documentElement.classList.contains('dark')) {
            this.enableLightMode();
        } else {
            this.enableDarkMode();
        }
    }

    /**
     * Add smooth transition animation
     */
    addTransitionClass() {
        document.documentElement.classList.add('theme-transitioning');
    }

    /**
     * Remove transition animation
     */
    removeTransitionClass() {
        document.documentElement.classList.remove('theme-transitioning');
    }

    /**
     * Setup toggle button with ripple effect
     */
    setupToggleButton() {
        const toggleButton = document.getElementById('dark-mode-toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', (e) => {
                this.addRippleEffect(e);
                this.toggle();
            });
            
            // Keyboard accessibility
            toggleButton.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggle();
                }
            });
        }
    }

    /**
     * Add ripple effect to button
     */
    addRippleEffect(event) {
        const button = event.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.className = 'ripple';
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    /**
     * Setup system preference listener
     * NOTE: Light mode is default. System preference is IGNORED unless user explicitly toggles theme.
     */
    setupSystemPreferenceListener() {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        darkModeQuery.addEventListener('change', (e) => {
            // Do nothing - we don't follow system preference
            // Users must explicitly toggle theme to change from light mode default
        });
    }

    /**
     * Setup element transition listeners
     */
    setupTransitionListeners() {
        document.addEventListener('transitionend', (e) => {
            if (e.propertyName === 'background-color' || e.propertyName === 'color') {
                e.target.classList.remove('transitioning');
            }
        });
    }

    /**
     * Update toggle button state
     */
    updateToggleButton(isDark) {
        const toggleButton = document.getElementById('dark-mode-toggle');
        if (toggleButton) {
            toggleButton.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            toggleButton.setAttribute('data-theme', isDark ? 'dark' : 'light');
        }
    }

    /**
     * Apply dark mode specific styles
     */
    applyDarkModeStyles() {
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', '#1f2937');
        }
        
        // Update favicon if needed
        this.updateFaviconForTheme('dark');
    }

    /**
     * Apply light mode specific styles
     */
    applyLightModeStyles() {
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', '#ffffff');
        }
        
        // Update favicon if needed
        this.updateFaviconForTheme('light');
    }

    /**
     * Update favicon for current theme
     */
    updateFaviconForTheme(theme) {
        // Implement favicon switching if needed
        // const favicon = document.querySelector('link[rel="icon"]');
        // if (favicon) {
        //     favicon.href = `/static/images/favicon-${theme}.svg`;
        // }
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }

    /**
     * Check if dark mode is enabled
     */
    isDarkMode() {
        return this.getCurrentTheme() === 'dark';
    }

    /**
     * Get all theme-aware colors
     */
    getThemeColors() {
        return {
            light: {
                primary: '#6366f1',
                secondary: '#8b5cf6',
                accent: '#ec4899',
                background: '#f9fafb',
                surface: '#ffffff',
                text: '#111827',
                textSecondary: '#6b7280',
                border: '#e5e7eb',
                success: '#10b981',
                warning: '#f59e0b',
                error: '#ef4444',
            },
            dark: {
                primary: '#818cf8',
                secondary: '#a78bfa',
                accent: '#f472b6',
                background: '#111827',
                surface: '#1f2937',
                text: '#f9fafb',
                textSecondary: '#9ca3af',
                border: '#374151',
                success: '#34d399',
                warning: '#fbbf24',
                error: '#f87171',
            }
        };
    }

    /**
     * Apply theme to canvas elements
     */
    applyThemeToCanvas(canvas) {
        const theme = this.isDarkMode() ? 'dark' : 'light';
        const colors = this.getThemeColors()[theme];
        return colors;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.darkModeManager = new DarkModeManager();
    });
} else {
    window.darkModeManager = new DarkModeManager();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkModeManager;
}

// Handle mobile toggle buttons
document.addEventListener('DOMContentLoaded', () => {
    const mobileToggleButtons = document.querySelectorAll('#dark-mode-toggle-mobile');
    mobileToggleButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            if (window.darkModeManager) {
                e.preventDefault();
                window.darkModeManager.toggle();
            }
        });
        
        // Keyboard accessibility
        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (window.darkModeManager) {
                    window.darkModeManager.toggle();
                }
            }
        });
    });
});
