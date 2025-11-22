# Smart Invoice - Professional Invoicing SaaS Platform

> Create stunning, professional invoices in seconds. Send via email or WhatsApp. Get paid faster.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-green)
![Django](https://img.shields.io/badge/Django-5.2.8%20LTS-darkgreen)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 🚀 Features

✨ **Professional Invoice Creation** | 📄 **PDF Generation** | 📧 **Email Distribution**  
💬 **WhatsApp Integration** | 💰 **Multi-Currency** | 🎨 **Custom Branding**  
📊 **Analytics Dashboard** | 🔐 **Bank-Level Security** | 📱 **Mobile-First Design**  
🌙 **Dark Mode** | ⚡ **Lightning Fast** | 🧪 **Comprehensive Tests**  
🔄 **Recurring Invoices** | 📋 **Invoice Templates** | 📤 **Bulk Export/Delete**

---

## 🎯 New in v1.0.0

### Core Features
- ✅ **Recurring Invoices**: Automate invoice generation (weekly, bi-weekly, monthly, quarterly, yearly)
- ✅ **Invoice Templates**: Save and reuse templates for faster invoice creation
- ✅ **Advanced Search**: Multi-filter dashboard with date range, amount range, currency, status
- ✅ **Bulk Operations**: Export multiple invoices as CSV or delete in bulk
- ✅ **User Profiles**: Manage company info, preferences, and default settings
- ✅ **Enhanced Analytics**: Chart.js visualizations with monthly trends
- ✅ **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- ✅ **Sentry Integration**: Real-time error tracking and monitoring

### Security & Performance
- ✅ **Database Optimization**: Strategic indexes and N+1 query elimination
- ✅ **Enhanced Security Headers**: CSP, HSTS, X-Frame-Options, X-XSS-Protection
- ✅ **Pre-commit Hooks**: Automated code quality checks
- ✅ **Comprehensive Testing**: 50%+ code coverage with pytest
- ✅ **Production Hardening**: Environment variable validation, secure defaults

---

## 📋 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.2.8 LTS, Gunicorn, PostgreSQL |
| **Frontend** | Tailwind CSS v3, Responsive HTML5, Vanilla JS |
| **PDF** | WeasyPrint 66.0 (high-fidelity generation) |
| **Analytics** | Chart.js for visualizations |
| **Security** | Encryption, CSP, CSRF, Rate Limiting, Sentry |
| **Testing** | pytest 9.0.1, 15+ test cases, pre-commit hooks |
| **Automation** | Django management commands for recurring invoices |

---

## 🎯 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (recommended)

### Installation (2 minutes)

```bash
git clone https://github.com/yourusername/smart-invoice.git
cd smart-invoice

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
npm install

cp .env.example .env
python manage.py migrate
npm run build:css
python manage.py runserver
```

Visit `http://localhost:8000`

---

## 📊 Dashboard Features

- Invoice list with advanced filtering
- Real-time revenue tracking & payment metrics
- Monthly trend visualization with Chart.js
- Client count & payment rate analytics
- Quick invoice creation & template management

---

## 💰 Supported Currencies

USD • EUR • GBP • NGN • CAD • AUD

---

## 🔄 Recurring Invoices

Generate invoices automatically with configurable frequency:

```bash
# Manual trigger
python manage.py generate_recurring_invoices

# Schedule with cron (daily at 2 AM)
0 2 * * * cd /path/to/smart-invoice && python manage.py generate_recurring_invoices
```

---

## 🧪 Testing

```bash
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest --cov=invoices       # With coverage report
pre-commit run --all-files  # Code quality checks
```

**Coverage:** 50%+ across all modules

---

## 🚀 Deployment

### Render (Recommended)

1. Connect GitHub repository to Render
2. Configure environment variables:
   - `DEBUG=False`
   - `SECRET_KEY=<strong-secret>`
   - `DATABASE_URL=<postgres-connection>`
   - `ENCRYPTION_SALT=<generated-salt>`
   - `SENTRY_DSN=<sentry-url>`

3. Build command:
```bash
pip install -r requirements.txt && npm install && npm run build:css && python manage.py migrate
```

4. Start command:
```bash
gunicorn smart_invoice.wsgi -b 0.0.0.0:5000 --workers 2
```

### Heroku

```bash
heroku create your-app
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set DEBUG=False SECRET_KEY=your-key ENCRYPTION_SALT=your-salt
git push heroku main
```

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Setup PostgreSQL database
- [ ] Generate & set `ENCRYPTION_SALT`
- [ ] Configure SMTP for email delivery
- [ ] Enable `HTTPS_ONLY = True`
- [ ] Setup Sentry error tracking
- [ ] Configure CSRF trusted origins
- [ ] Setup SSL certificate (automatic on Render)
- [ ] Test recurring invoice generation
- [ ] Configure backup strategy

---

## 📚 Documentation

- 📖 [.env.example](.env.example) - Configuration reference
- 🔧 [.pre-commit-config.yaml](.pre-commit-config.yaml) - Code quality tools

---

## 🔒 Security Features

| Feature | Details |
|---------|---------|
| **Authentication** | Secure login, password hashing, session management |
| **Data Protection** | HTTPS-only, secure cookies, CSRF tokens |
| **Encryption** | Field-level encryption for sensitive data |
| **API Security** | Rate limiting, SQL injection prevention, XSS protection |
| **Headers** | CSP, HSTS, X-Frame-Options, X-XSS-Protection |
| **Monitoring** | Sentry error tracking, debug logging |

---

## 📱 Mobile Optimization

✅ Fully responsive on all devices  
✅ Touch-optimized forms  
✅ Mobile-first CSS design  
✅ Fast load times on 4G  
✅ Dark mode support  

---

## 🤝 Contributing

Contributions welcome! Fork, create feature branch, submit PR.

```bash
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

---

## 📝 License

MIT License - Free for personal and commercial use

---

**Production-Ready. Fully Tested. Secure. 🎉**

For support: contact@smartinvoice.com
