# Smart Invoice - Project Documentation

## Overview
Smart Invoice is a production-ready Django SaaS platform designed for creating, managing, and distributing professional invoices with enterprise-grade email delivery. Its core purpose is to provide businesses with a robust solution for streamlined invoicing, encompassing features from creation and PDF generation to status tracking and automated email communication. The platform aims to offer a professional and efficient experience for users managing their billing processes.

## User Preferences
- Fast, efficient development cycle
- Functional, production-ready features
- Professional, enterprise-grade UI/UX
- Complete documentation
- Minimal user hand-holding

## System Architecture
The platform is built on a Django backend (Python 3) utilizing PostgreSQL (Neon-backed) for data persistence. Gunicorn with async workers handles the server, integrating with SendGrid for email services. The frontend employs Tailwind CSS for a professional, responsive, and mobile-first design, featuring a default light theme with an enhanced theme system using CSS variables and a dark mode option. WeasyPrint is used for professional PDF invoice generation, supporting SVG logos and custom fonts.

The system features a multi-page settings architecture with a professional enterprise-format interface and sidebar navigation. Email sending is managed asynchronously via SendGrid API v3, using threading and Django signal handlers for automated triggers and a "Direct Send" architecture for user replies. All footer pages are custom-built with professional styling, responsiveness, and dark mode support.

### Feature Specifications:
- **Invoice Management**: Create, edit, delete invoices; PDF generation; professional templates; line item management; status tracking; search/filtering.
- **Email System**: SendGrid integration for 6 email types (Invoice Ready, Invoice Paid, Payment Reminder, Welcome, Password Reset, Admin Alert) with async sending and signal handlers.
- **Settings System**: Profile, Business, Security, Email Notifications, Billing & Account pages with sidebar navigation.
- **Additional Features**: User authentication, password reset, user profiles, analytics dashboard, recurring invoices, templates, bulk export/delete, WhatsApp sharing.
- **UI/UX**: Professional light theme as default with dark mode option, responsive design (mobile, tablet, desktop breakpoints), enhanced styling for cards, buttons, forms, and tables. Color schemes are used to differentiate settings pages.

## External Dependencies
- **PostgreSQL**: Database backend (Neon-backed).
- **SendGrid API v3**: For all email sending functionalities.
- **WeasyPrint**: For generating PDF invoices.
- **Tailwind CSS**: Frontend styling framework.
- **JavaScript**: For frontend interactivity and theme management.