# Production Deployment Guide - Smart Invoice
**Version:** 4.0  
**Last Updated:** November 24, 2025

## Overview
This guide covers deploying Smart Invoice to production using Render's autoscale deployment option for optimal performance and cost efficiency.

## Pre-Deployment Checklist

### 1. Environment Variables (Required)
Set these in your Render dashboard under Environment Variables:

**Django Core:**
```bash
SECRET_KEY=<generate-with-get_random_secret_key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

**Database:**
```bash
DATABASE_URL=<provided-by-render-postgres>
```

**Email (SendGrid):**
```bash
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=noreply@your-domain.com
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**Security:**
```bash
ENCRYPTION_SALT=<generate-with-secrets.token_hex(32)>
```

**Optional (Monitoring):**
```bash
SENTRY_DSN=<your-sentry-dsn>
```

### 2. Build Production Assets
Before deploying, build all optimized assets:

```bash
# Install dependencies
npm install

# Build minified CSS, JS, and optimize images
npm run build:prod

# Collect Django static files
python manage.py collectstatic --noinput
```

### 3. Database Setup
Run migrations on production database:

```bash
python manage.py migrate
```

Create a superuser for admin access:

```bash
python manage.py createsuperuser
```

## Render Configuration

### Web Service Settings
- **Build Command:** 
  ```bash
  pip install -r requirements.txt && npm install && npm run build:prod && python manage.py collectstatic --noinput && python manage.py migrate
  ```

- **Start Command:**
  ```bash
  gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:5000 --workers 4 --timeout 30 --access-logfile - --error-logfile - --log-level info
  ```

- **Environment:** Python 3.11
- **Region:** Select closest to your users
- **Instance Type:** Starter (can scale up based on traffic)

### Database
- Create a PostgreSQL database in Render
- Link it to your web service (DATABASE_URL will be auto-configured)

### Auto-Scaling Configuration
**Recommended Settings:**
- **Min Instances:** 1
- **Max Instances:** 5
- **Target CPU:** 70%
- **Target Memory:** 80%

## Performance Optimizations

### 1. Static Files
- WhiteNoise handles static file serving with compression
- Brotli compression enabled automatically
- Cache headers set for 1 year on static assets

### 2. Database
- Connection pooling via Render
- Indexes on frequently queried fields
- Query optimization with select_related/prefetch_related

### 3. Caching
- LocMemCache for development
- Redis recommended for production (optional)
- Cached template loader in production

### 4. Asset Optimization
**Achieved Reductions:**
- JavaScript: 50% reduction (23KB → 12KB)
- CSS: 32% average reduction
- Images: Optimized and lazy-loaded

## Security Hardening

### Production Security Features
✅ HTTPS redirect (SECURE_SSL_REDIRECT=True)  
✅ Secure cookies (SESSION_COOKIE_SECURE=True)  
✅ HSTS headers (31536000 seconds)  
✅ CSP headers via django-csp  
✅ Rate limiting middleware  
✅ CSRF protection  
✅ Field-level encryption for sensitive data  
✅ XSS and clickjacking protection  

### SSL/TLS
- Render provides automatic SSL certificates
- HTTPS is enforced in production settings

## Monitoring & Logging

### Application Logs
Access via Render dashboard:
- Real-time log streaming
- Historical log search
- Error tracking

### Health Checks
Endpoint: `/health/`
- Returns 200 OK when healthy
- Checks database connectivity
- Monitors application status

### Performance Monitoring
**Recommended Tools:**
- Sentry for error tracking
- Render metrics for infrastructure
- Django Debug Toolbar (development only)

## Post-Deployment Verification

### 1. Smoke Tests
Run these checks after deployment:

```bash
# Test home page
curl https://your-domain.com/

# Test health endpoint
curl https://your-domain.com/health/

# Test static files
curl https://your-domain.com/static/js/app.min.js
```

### 2. Functional Tests
- [ ] User registration works
- [ ] Login authentication works
- [ ] Invoice creation works
- [ ] PDF generation works
- [ ] Email sending works
- [ ] Dashboard analytics load correctly

### 3. Performance Tests
Run Lighthouse audit:
- Target: 90+ for all metrics
- Check Core Web Vitals
- Verify SEO score

## Rollback Procedure

If deployment fails:

1. **Immediate Rollback via Render:**
   - Go to Render dashboard
   - Select your service
   - Click "Deployments"
   - Select previous stable deployment
   - Click "Redeploy"

2. **Database Rollback (if needed):**
   - Restore from automatic Render backup
   - Or manually restore from snapshot

## Scaling Guidelines

### Vertical Scaling (Upgrade Instance)
**When to upgrade:**
- CPU consistently > 80%
- Memory consistently > 85%
- Response times > 2s

**Instance types:**
- Starter: 0.5 CPU, 512MB RAM
- Standard: 1 CPU, 2GB RAM
- Pro: 2 CPU, 4GB RAM

### Horizontal Scaling (Add Instances)
Auto-scaling handles this automatically based on:
- CPU usage
- Memory usage
- Request queue depth

## Maintenance

### Regular Tasks
**Weekly:**
- Review error logs in Sentry
- Check performance metrics
- Monitor disk usage

**Monthly:**
- Update dependencies
- Review security patches
- Database optimization (VACUUM, ANALYZE)

**Quarterly:**
- Security audit
- Performance optimization review
- Disaster recovery drill

### Database Backups
- Automatic daily backups via Render
- Manual backups before major changes
- Test restore procedure quarterly

## Troubleshooting

### Common Issues

**Static files not loading:**
```bash
# Re-run collectstatic
python manage.py collectstatic --clear --noinput
```

**Database connection errors:**
- Verify DATABASE_URL is set correctly
- Check PostgreSQL instance is running
- Verify connection pooling settings

**Slow response times:**
- Check database query performance
- Review caching configuration
- Analyze with Django Debug Toolbar (staging)
- Enable query logging temporarily

**Memory issues:**
- Check worker count (recommended: 2-4 × CPU cores)
- Monitor memory per worker
- Review for memory leaks

## Support Resources

- **Render Documentation:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/
- **Smart Invoice Support:** support@smartinvoice.com

## Emergency Contacts

- **Technical Lead:** [Your contact]
- **DevOps:** [Your contact]
- **On-call:** [Your contact]

---

**Last successful deployment:** [Auto-updated by CI/CD]  
**Current version:** 4.0  
**Environment:** Production
