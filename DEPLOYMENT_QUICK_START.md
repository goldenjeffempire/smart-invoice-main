# Smart Invoice - Quick Start Deployment

**Deploy to Render in 5 minutes** ⚡

## Prerequisites
- GitHub account with this repository
- Render.com account (free)
- SendGrid account (free tier: 100 emails/day)

---

## Step 1: Generate Secret Keys (5 min local)

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate ENCRYPTION_SALT
python -c "import secrets; print(secrets.token_hex(32))"

# Copy these values - you'll need them in Step 3
```

---

## Step 2: Setup Email (2 min)

**SendGrid (Recommended):**
1. Create free account: https://sendgrid.com
2. Get API key from Settings → API Keys
3. Add to Render as `EMAIL_HOST_PASSWORD`

**Gmail (Dev only):**
1. Generate app password: https://myaccount.google.com/apppasswords
2. Add as `EMAIL_HOST_PASSWORD`

---

## Step 3: Deploy to Render (3 min)

1. **Go to Render Dashboard:** https://dashboard.render.com

2. **Click "New +" → "Blueprint"**

3. **Connect GitHub repository** (authorize Render)

4. **Render auto-detects `render.yaml` and creates:**
   - Web Service ✅
   - PostgreSQL Database ✅
   - All base configs ✅

5. **Set these environment variables:**

   | Variable | Value |
   |----------|-------|
   | `SECRET_KEY` | Paste from Step 1 |
   | `ENCRYPTION_SALT` | Paste from Step 1 |
   | `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
   | `EMAIL_HOST_PASSWORD` | Your SendGrid API key |

6. **Click "Deploy"** - Takes 5-10 minutes

7. **Your app is live!** 🎉
   - Visit: `https://your-app-name.onrender.com`
   - Admin: `/admin/` (create superuser via Shell)

---

## Step 4: Test Everything

```bash
# Test email (via Shell tab)
python manage.py send_test_email your-email@example.com

# Create admin user (via Shell)
python manage.py createsuperuser

# Test recurring invoices
python manage.py generate_recurring_invoices
```

---

## Recurring Invoices - Auto-Generate Daily

**Option A: Render Background Worker**
1. Create new Background Worker (same repo)
2. Start Command: `python manage.py generate_recurring_invoices`
3. Deploy

**Option B: External Cron (Free)**
Use https://easycron.com or GitHub Actions to trigger daily.

---

## That's It! 🚀

Your Smart Invoice platform is now live in production with:
✅ User authentication  
✅ Invoice management  
✅ Email delivery  
✅ PDF generation  
✅ Recurring invoices  
✅ Analytics dashboard  
✅ Bank-level security  

---

**Need Help?**
- Check logs: Render Dashboard → Logs tab
- See full guide: DEPLOYMENT.md
- Test locally first: `python manage.py runserver`
