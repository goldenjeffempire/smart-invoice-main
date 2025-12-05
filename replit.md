# InvoiceFlow - Production-Grade Full-Stack Platform

## Overview
InvoiceFlow is a production-grade professional invoicing platform designed to streamline financial operations for freelancers, agencies, small teams, and service-based businesses. It offers a comprehensive suite of features including PDF generation, multi-channel invoice sharing (email/WhatsApp), payment tracking, recurring invoices, customizable templates, and an analytics dashboard for financial reporting. The platform emphasizes enterprise-grade security and a modern, intuitive user experience. The business vision is to provide a robust, scalable solution that saves users time, accelerates payments, and drives revenue growth.

## User Preferences
- Preserve Django backend while rebuilding frontend
- Execute phases sequentially with artifact reporting
- Modern, professional UI/UX aligned with component showcase
- Comprehensive documentation at each phase

## System Architecture
### UI/UX Decisions
The platform features a modern, professional UI/UX with a focus on dark themes, glassmorphism, and responsive design. Key design elements include:
- **Design System Foundation**: "InvoiceFlow Platinum" design tokens, deep indigo primary colors, gradient accents, glassmorphism tokens (glass-bg, glass-blur), enhanced shadow system, and an 8pt grid spacing scale.
- **Typography**: Modern Inter font family.
- **Animations**: Advanced animation system (`enhancements.css`, `landing-animations.css`) with shimmer, bounce, slide-in, fade-in, wiggle effects, scroll reveals, parallax, and confetti for user feedback. Supports `prefers-reduced-motion`.
- **Component Library**: Modular CSS for buttons, cards, forms, navigation, modals, skeleton loaders, and toast notifications.
- **Responsive Design**: Comprehensive mobile-first approach with CSS breakpoints at 768px (tablet), 1024px (desktop), 1280px (large desktop), and 1536px (extra large). Features include:
  - Mobile navigation with hamburger menu and overlay
  - Collapsible dashboard sidebar with touch-friendly toggle
  - Responsive tables with horizontal scroll on mobile
  - Form layouts that stack on smaller screens
  - Touch-optimized buttons (min 44px hit targets)
  - Reduced motion support for accessibility
  - Print styles for invoice output
  - Landscape phone and high-DPI optimizations
- **Interactive Elements**: Hover effects, 3D tilt interactions, animated counters, floating labels, and live form validation.

### Technical Implementations
- **Backend**: Django with PostgreSQL for database management.
- **Frontend**: Primarily HTML/CSS with JavaScript for interactive elements. Tailwind CSS is used for utility-first styling, extended with custom design tokens and plugins.
- **Email Service**: SendGrid integration for template-based emails and PDF attachments.
- **PDF Generation**: WeasyPrint for high-quality PDF invoice generation.
- **Security**: Comprehensive security measures including CSRF protection, XSS prevention, SQL injection prevention, modern security headers (CSP, HSTS), rate limiting, honeypot spam protection, and secure session management.
- **Performance**: Gunicorn with multiple workers, database connection pooling, static file compression (Brotli), asset hashing, and lazy loading for images.
- **Health Checks**: Dedicated `/health/`, `/health/ready/`, and `/health/live/` endpoints for monitoring.
- **SEO**: robots.txt, sitemap.xml, Open Graph, Twitter Card meta tags, and JSON-LD structured data.

### Feature Specifications
- **Invoice Management**: Create, edit, delete, track, and export invoices (CSV, PDF). Support for recurring invoices.
- **Multi-channel Sharing**: Share invoices via email and WhatsApp.
- **Payment Tracking**: Record and track invoice payments.
- **Customization**: Customizable invoice templates with branding options.
- **Analytics Dashboard**: Visualizations for revenue, payment status, and other key metrics.
- **User Authentication**: Secure login, signup, and password reset functionalities.
- **Contact Management**: Contact forms with submissions stored and managed in the admin panel.

### System Design Choices
- **Micro-interactions**: Subtle animations and feedback for user actions to enhance engagement.
- **Error Handling**: Robust error handling with user-friendly toast notifications and clear validation messages.
- **Accessibility**: ARIA attributes, labeled form inputs, descriptive alt texts, keyboard navigation, and focus indicators.
- **Deployment**: Production-ready Gunicorn configuration, integrated with Render for autoscale deployments, including SSL certificate setup.

## External Dependencies
- **Database**: PostgreSQL
- **Web Server**: Gunicorn
- **Static Files Serving**: WhiteNoise
- **Email Service**: SendGrid
- **PDF Generation**: WeasyPrint
- **Payment Processing**: Paystack (optional, via `PAYSTACK_SECRET_KEY`)
- **Error Tracking**: Sentry (optional, via `SENTRY_DSN`)
- **Frontend Frameworks/Libraries**: Tailwind CSS, PostCSS, Node.js (for asset compilation)

## Recent Changes (December 2025)

### Phase 0: Critical Security & Compliance Hardening (COMPLETED)
- Implemented comprehensive security headers via SecurityHeadersMiddleware:
  - HSTS with preload, includeSubDomains (max-age: 31536000)
  - Content Security Policy (CSP) with strict directives
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy restricting dangerous features
- GDPR compliance with cookie consent management
- CORS configuration for API endpoints

### Phase 1: Authentication & Login Security (COMPLETED)
- Session security hardening:
  - SESSION_COOKIE_HTTPONLY = True
  - SESSION_COOKIE_SAMESITE = "Strict"
  - SESSION_COOKIE_SECURE = True (production)
  - CSRF_COOKIE_HTTPONLY = True
- Enhanced password validators:
  - Minimum 12 characters
  - Complexity requirements (uppercase, lowercase, digit, special char)
  - Breach detection via Have I Been Pwned API (k-anonymity)
- TOTP MFA implementation:
  - MFAProfile model with encrypted secrets
  - QR code generation for authenticator apps
  - Recovery codes (8 codes, one-time use)
  - MFAEnforcementMiddleware blocks protected views until mfa_verified=True
  - Admin access requires MFA verification
  - MFA disable requires password + TOTP verification
- Login security:
  - LoginAttempt model tracks all login attempts
  - Dual lockout system (per-IP and per-username)
  - Configurable thresholds via settings

### Phase 2: Deployment, DevOps, Secrets & Observability (COMPLETED)
- Structured JSON logging with request context propagation:
  - JsonFormatter for log aggregation compatibility
  - Thread-local request context (request_id, user_id, ip_address)
  - RequestContextFilter attached to all handlers
- Health check endpoints:
  - /health/ - basic health with version and uptime
  - /health/ready/ - readiness with database, migrations, cache checks
  - /health/live/ - liveness with response time
  - /health/detailed/ - extended system info and env status
- Environment validation on startup (wsgi.py)
- Production deployment configuration (autoscale with gunicorn)