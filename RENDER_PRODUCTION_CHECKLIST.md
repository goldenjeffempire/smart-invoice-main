# Render Production Deployment Checklist

## 🚀 Pre-Deployment Setup

### 1. Environment Variables (REQUIRED)
Set these in your Render dashboard before deploying:

#### Critical Security Variables
```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate ENCRYPTION_SALT
python -c "import secrets; print(secrets.token_hex(32))"
```

**Set in Render Dashboard:**
- `SECRET_KEY` = [Generated secret key above]
- `ENCRYPTION_SALT` = [Generated encryption salt above]
- `ALLOWED_HOSTS` = your-app.onrender.com,www.your-domain.com
- `DEBUG` = False (already set in render.yaml)

#### Email Configuration (SendGrid)
- `SENDGRID_API_KEY` = [Your SendGrid API key]
- `SENDGRID_FROM_EMAIL` = noreply@yourdomain.com

#### Error Tracking (Optional but Recommended)
- `SENTRY_DSN` = [Your Sentry DSN for error tracking]

### 2. Database Setup
The PostgreSQL database is automatically created by Render. The `DATABASE_URL` environment variable is automatically set.

**After first deployment:**
- Run migrations (automatically run in buildCommand)
- Create superuser: `python manage.py createsuperuser`

### 3. Static Files
Static files are automatically collected during build. WhiteNoise serves them in production.

## 📋 Deployment Steps

### Step 1: Connect Repository
1. Go to render.com and click "New +"
2. Select "Blueprint" (this will use render.yaml)
3. Connect your GitHub/GitLab repository
4. Render will detect render.yaml automatically

### Step 2: Configure Environment Variables
1. Go to your service in Render dashboard
2. Navigate to "Environment" tab
3. Add all required environment variables listed above
4. Click "Save Changes"

### Step 3: Deploy
1. Render will automatically deploy your application
2. Build takes ~5-10 minutes first time
3. Monitor build logs for any issues

### Step 4: Post-Deployment
1. Run database migrations (auto-run in buildCommand)
2. Create admin user via Render Shell:
   ```bash
   python manage.py createsuperuser
   ```
3. Test the application at your-app.onrender.com
4. Verify email sending works (if SendGrid configured)

## 🔒 Security Checklist

- ✅ DEBUG = False in production
- ✅ SECRET_KEY is randomly generated and secure
- ✅ ENCRYPTION_SALT is randomly generated
- ✅ ALLOWED_HOSTS is properly configured
- ✅ HTTPS enabled (automatic on Render)
- ✅ Security headers configured (in middleware)
- ✅ CSRF protection enabled
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection (Django templates)

## 🎯 Performance Optimization

### Gunicorn Configuration
- **Workers**: 4 (configured in render.yaml)
- **Worker Class**: sync (suitable for CPU-bound Django apps)
- **Timeout**: 60 seconds
- **Max Requests**: 1000 (auto-restart workers to prevent memory leaks)

### Caching (Future Enhancement)
For better performance, consider adding Redis:
1. Add Redis service in render.yaml
2. Install django-redis: `pip install django-redis`
3. Configure caching in settings.py

## 📊 Monitoring

### Health Checks
- Endpoint: `/health/`
- Configured in render.yaml
- Render automatically monitors this endpoint

### Error Tracking
- Sentry integration configured (if SENTRY_DSN set)
- View errors in Sentry dashboard
- Real-time alerts for production issues

### Logs
- Access logs: Available in Render dashboard
- Error logs: Available in Render dashboard
- Application logs: Use Render's log viewer

## 🔄 Continuous Deployment

Render automatically deploys when you push to your main branch:
1. Push code to GitHub/GitLab
2. Render detects changes
3. Runs build command
4. Deploys new version
5. Zero-downtime deployment

## 🐛 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify requirements.txt is complete
- Ensure all dependencies are compatible

### Application Won't Start
- Check environment variables are set correctly
- Verify DATABASE_URL is set (auto-configured)
- Check application logs for errors

### Database Issues
- Verify DATABASE_URL environment variable
- Check migrations ran successfully
- Review database logs in Render dashboard

### Static Files Not Loading
- Verify collectstatic ran in build
- Check WhiteNoise is installed
- Review STATIC_ROOT and STATIC_URL settings

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com/
- **Application Issues**: Check logs in Render dashboard

## 🎉 Post-Launch

Once deployed successfully:
1. ✅ Test all core functionality
2. ✅ Verify email sending works
3. ✅ Create test invoices
4. ✅ Test PDF generation
5. ✅ Verify WhatsApp sharing
6. ✅ Test payment tracking
7. ✅ Check analytics dashboard
8. ✅ Test on mobile devices
9. ✅ Verify SEO metadata
10. ✅ Monitor error rates in Sentry

## 🚨 Important Notes

- **Free Tier Limitations**: 
  - Render free tier spins down after 15 minutes of inactivity
  - First request after spin-down takes 30-60 seconds
  - Consider upgrading to paid tier for production use

- **Database Backups**:
  - Render provides automatic daily backups on paid plans
  - Export database manually for free tier: Use Render dashboard

- **Custom Domain**:
  - Configure custom domain in Render dashboard
  - Update ALLOWED_HOSTS environment variable
  - Configure DNS records as instructed

---

**Ready to deploy? Follow the steps above and your Smart Invoice platform will be live in minutes!** 🚀
