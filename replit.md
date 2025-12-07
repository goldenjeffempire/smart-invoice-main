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
The platform features a modern, professional UI/UX with a focus on clean light themes, professional business aesthetics, and responsive design. Key design elements include:
- **Design System Foundation**: Professional light theme design tokens, indigo primary colors (#4f46e5), emerald accents (#10b981), clean white backgrounds, subtle gray accents, modern shadow system, and an 8pt grid spacing scale.
- **Typography**: Modern Inter font family.
- **Animations**: Advanced animation system with shimmer, bounce, slide-in, fade-in, wiggle effects, scroll reveals, parallax, and confetti for user feedback. Supports `prefers-reduced-motion`.
- **Component Library**: Modular CSS for buttons, cards, forms, navigation, modals, skeleton loaders, and toast notifications.
- **Responsive Design**: Comprehensive mobile-first approach with CSS breakpoints, including mobile navigation, collapsible dashboard sidebar, and responsive tables.
- **Interactive Elements**: Hover effects, 3D tilt interactions, animated counters, floating labels, and live form validation.

### Technical Implementations
- **Backend**: Django with PostgreSQL.
- **Frontend**: Primarily HTML/CSS with JavaScript for interactive elements. Tailwind CSS for utility-first styling.
- **Email Service**: SendGrid integration.
- **PDF Generation**: WeasyPrint.
- **Security**: Comprehensive measures including CSRF protection, XSS prevention, SQL injection prevention, modern security headers (CSP, HSTS), rate limiting, honeypot spam protection, secure session management, and Two-Factor Authentication (TOTP MFA).
- **Performance**: Gunicorn with multiple workers, database connection pooling, static file compression (Brotli), asset hashing, and lazy loading.
- **Health Checks**: Dedicated `/health/`, `/health/ready/`, and `/health/live/` endpoints for monitoring.
- **SEO**: robots.txt, sitemap.xml, Open Graph, Twitter Card meta tags, and JSON-LD structured data.

### Feature Specifications
- **Invoice Management**: Create, edit, delete, track, and export invoices (CSV, PDF), including recurring invoices.
- **Multi-channel Sharing**: Share invoices via email and WhatsApp.
- **Payment Tracking**: Record and track invoice payments.
- **Customization**: Customizable invoice templates with branding options.
- **Analytics Dashboard**: Visualizations for revenue, payment status, and other key metrics.
- **User Authentication**: Secure login, signup, and password reset.
- **Contact Management**: Contact forms with admin panel management.

### System Design Choices
- **Micro-interactions**: Subtle animations and feedback for user actions.
- **Error Handling**: Robust error handling with user-friendly toast notifications and validation.
- **Accessibility**: ARIA attributes, labeled form inputs, descriptive alt texts, keyboard navigation, and focus indicators.
- **Deployment**: Production-ready Gunicorn configuration, integrated with Render for autoscale deployments, including SSL.
- **Logging**: Structured JSON logging with request context propagation.
- **Compliance**: GDPR compliance with cookie consent and comprehensive Privacy Policy/Terms of Service.

## External Dependencies
- **Database**: PostgreSQL
- **Web Server**: Gunicorn
- **Static Files Serving**: WhiteNoise
- **Email Service**: SendGrid
- **PDF Generation**: WeasyPrint
- **Payment Processing**: Paystack (optional)
- **Error Tracking**: Sentry (optional)
- **Frontend Frameworks/Libraries**: Tailwind CSS, PostCSS, Node.js (for asset compilation)