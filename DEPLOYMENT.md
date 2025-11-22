# Smart Invoice - Deployment Guide

Complete step-by-step guide for deploying Smart Invoice to production on Render.

## Table of Contents

1. [Email Configuration](#email-configuration)
2. [Render Deployment](#render-deployment)
3. [Recurring Invoice Scheduler](#recurring-invoice-scheduler)
4. [Post-Deployment Checklist](#post-deployment-checklist)
5. [Troubleshooting](#troubleshooting)

---

## Email Configuration

### Option A: SendGrid (Recommended for Production)

1. Create account at https://sendgrid.com
2. Generate API key in Settings → API Keys
3. Add to `.env`:
```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxx
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Smart Invoice <noreply@smartinvoice.com>
```

### Option B: Gmail (Development Only)

1. Enable 2-Factor Authentication on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Smart Invoice <your-email@gmail.com>
```

### Test Email Configuration

**Local Testing:**
```bash
python manage.py send_test_email your-test@email.com
```

Expected: "Test email sent successfully!"

---

## Render Deployment

### Step 1: Prepare Repository

Ensure these files are committed to GitHub:
- ✅ `render.yaml` - Render configuration
- ✅ `Procfile` - Process file
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Example configuration

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create Web Service

1. Dashboard → "New +" → "Web Service"
2. Select your GitHub repository
3. Configure:
   - **Name:** smart-invoice
   - **Environment:** Python 3
   - **Region:** Choose closest to users
   - **Plan:** Free (can upgrade later)
4. Click "Create Web Service"

Render will automatically:
- Build from `render.yaml`
- Install dependencies
- Run migrations
- Start the server

### Step 4: Configure Environment Variables

In Render Dashboard → Web Service → Environment:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Run: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `ENCRYPTION_SALT` | Run: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `EMAIL_HOST` | `smtp.sendgrid.net` |
| `EMAIL_HOST_PASSWORD` | Your SendGrid API key |
| `SENTRY_DSN` | (Optional) From Sentry.io |

### Step 5: Create PostgreSQL Database

1. Dashboard → "New +" → "PostgreSQL"
2. Configure:
   - **Name:** smart-invoice-db
   - **Database:** smartinvoice
   - **Region:** Same as web service
   - **Plan:** Free
3. Copy "Internal Database URL"
4. Add to Web Service environment: `DATABASE_URL`

### Step 6: Deploy

Render automatically deploys when you push to GitHub.

**Check deployment:**
- Dashboard → Deployments
- Look for green checkmark
- Visit your app URL

Your app is live at: `https://your-app-name.onrender.com`

---

## Recurring Invoice Scheduler

### Option 1: Render Background Worker (Recommended)

**Create Background Worker:**

1. Dashboard → "New +" → "Background Worker"
2. Select same repository
3. Configure:
   - **Name:** recurring-invoice-generator
   - **Environment:** Python 3
   - **Region:** Same as web service
   - **Plan:** Free
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python manage.py generate_recurring_invoices`
4. Add same environment variables as web service
5. Deploy

**Schedule the task:**

The background worker runs once. To run daily, use a cron service:

**Using EasyCron (Free):**
1. Go to https://easycron.com
2. Create new cron job:
   - **URL:** `https://your-app.onrender.com/admin/`
   - **Frequency:** Daily at 2 AM UTC
3. Render will wake up and run the task

### Option 2: External Cron Service

**Using GitHub Actions (Free):**

Create `.github/workflows/recurring-invoices.yml`:

```yaml
name: Generate Recurring Invoices
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Trigger recurring invoice generation
        run: |
          curl -X POST https://your-app.onrender.com/api/recurring/generate \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

---

## Post-Deployment Checklist

- [ ] App loads at your URL
- [ ] Test email: `python manage.py send_test_email your-email@example.com`
- [ ] Create admin user: `python manage.py createsuperuser`
- [ ] Test user signup
- [ ] Create sample invoice
- [ ] Download PDF
- [ ] Send invoice via email
- [ ] Check recurring invoices run daily
- [ ] Monitor Sentry for errors
- [ ] Configure SSL (automatic on Render)

---

## Troubleshooting

### Email Not Sending

**Check logs:**
```bash
# In Render Dashboard
Web Service → Logs (look for email errors)
```

**Test configuration:**
```bash
python manage.py send_test_email your-test@email.com
```

**Common issues:**
- Wrong SendGrid API key
- EMAIL_USE_TLS not set to True
- Firewall blocking port 587

### App Won't Start

**Check logs:**
- Dashboard → Deployments → Latest → Build Log

**Fix database issues:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Migrations Failed

**SSH into Render:**
1. Web Service → Shell
2. Run: `python manage.py migrate --verbose`

---

## Performance & Scaling

- **Free tier:** Good for development/testing
- **Paid tier:** For production traffic (can scale horizontally)
- **Database:** Upgrade if >50GB needed
- **Cache:** Enable Redis for better performance

---

**Version:** 1.0.0  
**Last Updated:** November 2025
