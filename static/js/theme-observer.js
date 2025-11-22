/**
 * Theme Observer - Watches for theme changes and updates charts/canvas elements
 */

class ThemeObserver {
    constructor() {
        this.observers = new Set();
        this.currentTheme = this.getCurrentTheme();
        this.init();
    }

    init() {
        // Listen for theme changes
        window.addEventListener('themechange', (e) => {
            this.currentTheme = e.detail.theme;
            this.notifyObservers(e.detail.theme);
        });

        // Listen for system preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            this.currentTheme = this.getCurrentTheme();
            this.notifyObservers(this.currentTheme);
        });
    }

    /**
     * Subscribe to theme changes
     */
    subscribe(callback) {
        this.observers.add(callback);
        return () => this.observers.delete(callback);
    }

    /**
     * Notify all observers of theme change
     */
    notifyObservers(theme) {
        this.observers.forEach(callback => {
            try {
                callback(theme);
            } catch (error) {
                console.error('Error in theme observer callback:', error);
            }
        });
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }

    /**
     * Get theme-specific colors
     */
    getThemeColors() {
        const isDark = this.currentTheme === 'dark';
        return {
            primary: isDark ? '#818cf8' : '#6366f1',
            secondary: isDark ? '#a78bfa' : '#8b5cf6',
            accent: isDark ? '#f472b6' : '#ec4899',
            background: isDark ? '#111827' : '#f9fafb',
            surface: isDark ? '#1f2937' : '#ffffff',
            text: isDark ? '#f9fafb' : '#111827',
            textSecondary: isDark ? '#9ca3af' : '#6b7280',
            border: isDark ? '#374151' : '#e5e7eb',
            success: isDark ? '#34d399' : '#10b981',
            warning: isDark ? '#fbbf24' : '#f59e0b',
            error: isDark ? '#f87171' : '#ef4444',
            info: isDark ? '#60a5fa' : '#3b82f6',
        };
    }

    /**
     * Get theme for Chart.js
     */
    getChartJsTheme() {
        const colors = this.getThemeColors();
        return {
            backgroundColor: colors.background,
            textColor: colors.text,
            gridColor: colors.border,
            colors: {
                primary: colors.primary,
                secondary: colors.secondary,
                accent: colors.accent,
                success: colors.success,
                warning: colors.warning,
                error: colors.error,
            }
        };
    }
}

// Initialize theme observer
const themeObserver = new ThemeObserver();

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeObserver;
}
