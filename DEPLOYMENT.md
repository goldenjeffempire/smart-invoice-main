# InvoiceFlow - Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Render account (or any platform supporting Django/PostgreSQL)
- SendGrid account (for email) or SMTP provider
- Domain name (optional)

### 1. Environment Setup

**Required Environment Variables:**
```bash
SECRET_KEY=<generate-with-python>
ENCRYPTION_SALT=<generate-with-python>
ALLOWED_HOSTS=yourdomain.com,yourapp.onrender.com
DATABASE_URL=postgresql://user:password@host:port/dbname
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.onrender.com
```

**Email Configuration (choose one):**
```bash
# Option A: SendGrid
SENDGRID_API_KEY=your-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Option B: Generic SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Optional:**
```bash
SENTRY_DSN=<for-error-tracking>
DEBUG=False
WEB_CONCURRENCY=4
```

### 2. Generate Secrets

```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate ENCRYPTION_SALT
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Deploy to Render

#### Option A: Using render.yaml (Recommended)
1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml`
4. Set required environment variables in Render dashboard
5. Deploy!

#### Option B: Manual Setup
1. Create new Web Service on Render
2. Build Command: `./build.sh`
3. Start Command: `gunicorn invoiceflow.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
4. Environment: Python 3.11+
5. Add PostgreSQL database
6. Set environment variables
7. Deploy!

### 4. Post-Deployment

**Create superuser:**
```bash
python manage.py createsuperuser
```

**Verify deployment:**
- Visit: `https://yourapp.onrender.com/health/`
- Should return: `{"status": "healthy"}`

**Test critical flows:**
- [ ] User signup
- [ ] User login
- [ ] Create invoice
- [ ] Send invoice via email
- [ ] Mark invoice as paid
- [ ] View dashboard analytics

## 📋 Pre-Deployment Checklist

### Security
- [x] CSRF protection enabled
- [x] XSS protection enabled
- [x] HSTS headers configured
- [x] CSP headers configured
- [x] Rate limiting enabled
- [x] SQL injection protection (Django ORM)
- [x] Secure password hashing (Django defaults)
- [ ] SECRET_KEY set to secure random value
- [ ] ENCRYPTION_SALT set to secure random value
- [ ] ALLOWED_HOSTS configured with actual domains
- [ ] DEBUG=False in production

### Database
- [x] PostgreSQL configured via DATABASE_URL
- [x] Migrations ready
- [ ] Database backup strategy in place
- [ ] Connection pooling configured (if needed)

### Static Files
- [x] WhiteNoise configured for static file serving
- [x] Compression enabled (CompressedManifestStaticFilesStorage)
- [x] collectstatic in build command
- [x] STATIC_ROOT configured

### Email
- [ ] SendGrid API key or SMTP credentials configured
- [ ] FROM_EMAIL set to valid email
- [ ] Test email sending works
- [ ] Template IDs configured (if using SendGrid templates)

### Monitoring
- [ ] Health check endpoint accessible (/health/)
- [ ] Error tracking configured (Sentry optional)
- [ ] Logging configured
- [ ] Performance monitoring setup (optional)

### Performance
- [x] Gunicorn with multiple workers
- [x] Database query optimization completed
- [x] Static file caching enabled
- [x] Gzip/Brotli compression enabled

## 🔧 Configuration Files

### Requirements
- `requirements.txt` - Development dependencies
- `requirements-production.txt` - Production dependencies
- `package.json` - Node.js dependencies (Tailwind CSS)

### Deployment
- `render.yaml` - Render.com configuration
- `Procfile` - Heroku-style process definition
- `build.sh` - Production build script
- `.env.example` - Environment variable template

### Django
- `invoiceflow/settings.py` - Production-ready settings
- `invoiceflow/wsgi.py` - WSGI application entry

## 🛠️ Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --noinput --clear
```

### Database connection errors
- Verify DATABASE_URL is correct
- Check PostgreSQL service is running
- Verify firewall/network settings

### CSRF errors
- Add your domain to CSRF_TRUSTED_ORIGINS
- Verify ALLOWED_HOSTS includes your domain

### Email not sending
- Check SendGrid API key is valid
- Verify FROM_EMAIL is verified in SendGrid
- Check spam folders
- Review error logs

## 📊 Performance Optimization

### Database
- Indexes on frequently queried fields (already configured)
- Connection pooling for high traffic
- Regular VACUUM/ANALYZE maintenance

### Caching
- Configure Redis for session/cache storage (optional upgrade)
- Enable database query caching
- Use CDN for static assets (optional)

### Monitoring
- Set up Sentry for error tracking
- Configure New Relic/DataDog for APM (optional)
- Regular security audits

## 🔄 Updates & Maintenance

### Regular Updates
```bash
# Update dependencies
pip list --outdated
pip install --upgrade <package>

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

### Database Backups
- Enable automated backups on Render
- Test restore procedures regularly
- Keep backups for 30+ days

### Security Updates
- Monitor Django security releases
- Update dependencies regularly
- Review security headers periodically

## 🌐 Domain Configuration

### Custom Domain Setup (Render)
1. Go to Render Dashboard → Settings
2. Add custom domain
3. Update DNS records (A or CNAME)
4. Wait for SSL certificate provisioning
5. Update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS

### DNS Configuration
```
Type: CNAME
Name: www
Value: yourapp.onrender.com
TTL: 3600
```

## 📞 Support

### Resources
- Django Documentation: https://docs.djangoproject.com/
- Render Documentation: https://render.com/docs
- SendGrid Documentation: https://docs.sendgrid.com/

### Common Issues
- Check logs: Render Dashboard → Logs tab
- Health check: `/health/` endpoint
- Admin panel: `/admin/` (create superuser first)

---

**Last Updated:** November 2025
**Platform Version:** Django 5.2.8, Python 3.11+
