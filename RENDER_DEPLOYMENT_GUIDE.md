# Smart Invoice - Complete Render Deployment Guide

## Prerequisites
- GitHub account with repository forked/pushed
- Render account (free tier available at render.com)
- SendGrid account for emails (free tier: 100 emails/day)
- ~15 minutes for complete setup

## Step 1: Prepare Repository

Ensure all code is committed and pushed:
```bash
git add .
git commit -m "Production ready: Smart Invoice v1.0"
git push origin main
```

## Step 2: Create Render PostgreSQL Database

1. Go to [render.com](https://render.com) and log in
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Database Name:** `smart-invoice-db`
   - **Region:** Choose closest to you
   - **PostgreSQL Version:** 15 (latest)
   - **Free Plan:** Yes (1 GB RAM)
4. Click **"Create Database"**
5. **IMPORTANT:** Copy the **DATABASE_URL** from the database details page

## Step 3: Create Render Web Service

1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub:** Authorize and select Smart Invoice repository
3. Configure Web Service:
   - **Name:** `smart-invoice-app`
   - **Environment:** `Python 3`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Build Command:**
     ```
     pip install -r requirements-production.txt && npm install && npm run build:css && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```
     gunicorn smart_invoice.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 30 --access-logfile - --error-logfile -
     ```
4. **Plan:** Free tier for testing, Starter ($7/month) for production
5. Click **"Create Web Service"**

## Step 4: Add Environment Variables

In Render dashboard:
1. Go to your Web Service → **Environment**
2. Add each variable:

```
DJANGO_SECRET_KEY=&d6r$7cfk*147tnd-89!exa7@^%19hs@+)k!j31dpy$h25dc90
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=[paste from Step 2]
SENDGRID_API_KEY=SG.your_key_here
SENDGRID_FROM_EMAIL=noreply@yourcompany.com
```

3. Click **"Save"** - deployment starts automatically

## Step 5: Verify Deployment

1. **Check Build Logs:**
   - Click "Logs" tab in dashboard
   - Should see: "Build successful" message
   - Wait 2-3 minutes for deployment

2. **Test the App:**
   - Click the service URL (e.g., `https://smart-invoice-app.onrender.com`)
   - You should see the homepage
   - Try: Sign up → Create invoice → Generate PDF

3. **Common Issues:**
   - **Build fails:** Check logs for errors, verify requirements.txt exists
   - **Database error:** Verify DATABASE_URL is copied exactly
   - **Static files missing:** Already configured with WhiteNoise

## Step 6: SendGrid Email Configuration

1. Create [SendGrid account](https://sendgrid.com) (free: 100/day)
2. **Create API Key:**
   - Go to Settings → API Keys
   - Create new key with "Mail Send" permission
   - Copy the key to Render environment as `SENDGRID_API_KEY`

3. **Verify Sender Email:**
   - Settings → Sender Authentication
   - Add your business email address
   - Verify the confirmation email

4. **Create Email Templates (Optional but Recommended):**
   - Marketing → Dynamic Templates
   - Create templates for: Invoice Ready, Invoice Paid, Payment Reminder, etc.
   - Copy template IDs to environment variables

## Step 7: Custom Domain (Optional)

1. In Render: Settings → **Custom Domains**
2. Add your domain: `yourdomain.com`
3. Follow the DNS setup instructions
4. SSL certificate auto-issued (free, ~30 mins)

## Step 8: Enable Auto-Deploy

1. Render: Web Service Settings → **Auto-Deploy**
2. Enable "Auto-deploy new pushes"
3. Now every `git push` automatically deploys

## Step 9: Health Checks & Monitoring

### Verify App is Running
```bash
curl https://your-app-name.onrender.com/health/
# Should return JSON status
```

### Monitor Logs
- Render dashboard: "Logs" tab
- See real-time application errors

### Database Backups
- Render auto-backups PostgreSQL daily
- Check: Postgres instance → Backups tab

## Production Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created on Render
- [ ] Web Service created on Render
- [ ] All environment variables set
- [ ] Build completed successfully (check logs)
- [ ] App loads at your URL
- [ ] Sign up/login works
- [ ] Invoice creation works
- [ ] PDF generation works
- [ ] SendGrid API key verified
- [ ] Email sending tested
- [ ] Custom domain added (if applicable)

## Monitoring Production

### Set Up Error Tracking (Recommended)
```bash
# Add to requirements.txt:
sentry-sdk

# Add SENTRY_DSN to environment variables
```

### Performance Optimization
- First load might be slow (Render free tier)
- Upgrade to Starter plan ($7/month) for better performance
- Database backups automatic

### Scaling for Growth
- Free tier: ~50-100 concurrent users
- Starter plan: ~1000+ concurrent users
- Upgrade in Render: Settings → Plan

## Troubleshooting

### 503 Service Unavailable
- Check if service is running: Render dashboard
- Restart service: Click "Restart Service"

### Database Connection Error
- Verify DATABASE_URL is correct
- Check PostgreSQL instance is active
- Try restarting web service

### Static Files (CSS/Images) Not Loading
- Already configured with WhiteNoise
- Check browser cache: Hard refresh (Ctrl+Shift+R)

### Emails Not Sending
- Verify SENDGRID_API_KEY
- Check sender email is verified
- Look at application logs for errors

### Out of Memory
- Free tier has 512MB RAM
- Upgrade to Starter: $7/month, 2GB RAM

## Production URLs

- **App URL:** `https://smart-invoice-app.onrender.com`
- **Admin URL:** `https://smart-invoice-app.onrender.com/admin/`
- **Health URL:** `https://smart-invoice-app.onrender.com/health/`

## Support & Resources

- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com
- SendGrid Docs: https://docs.sendgrid.com
- GitHub Issues: Check project repository

---

**Your Smart Invoice platform is now live! 🚀**

For questions or issues, check the Render dashboard logs or contact Render support.
