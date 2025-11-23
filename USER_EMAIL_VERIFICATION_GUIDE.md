# How Users Verify Email with SendGrid - Step-by-Step Guide

**Time Required**: 5 minutes  
**Difficulty**: Very Easy  

---

## 📋 Prerequisites

Before starting, users need:
- ✅ SendGrid account (free at https://sendgrid.com)
- ✅ Their business email address (e.g., sales@mycompany.com)
- ✅ Access to that email inbox

---

## 🔧 Step-by-Step Verification Process

### Step 1: Log Into SendGrid

1. Go to: **https://app.sendgrid.com**
2. Log in with your SendGrid account
3. You're now in the SendGrid Dashboard

---

### Step 2: Go to Sender Authentication

1. On the left sidebar, find **Settings**
2. Click **Settings** (expands menu)
3. Click **Sender Authentication**
4. You should see "Authenticate your domain and verify your senders"

**Direct Link**: https://app.sendgrid.com/settings/sender_authentication

---

### Step 3: Create New Sender

1. Look for a button that says **"Create New"** or **"Create Sender"**
2. Click it
3. A form will appear asking for sender details

---

### Step 4: Fill In Sender Information

**The form will have these fields:**

| Field | What to Enter | Example |
|-------|---------------|---------|
| **From Email Address** | Your business email | sales@mycompany.com |
| **From Display Name** | Your business name | My Company Inc |
| **Reply To Email** | Same as From email (optional) | sales@mycompany.com |
| **Company Address** | Your company address | 123 Main St, City, State |

**What each means:**
- **From Email**: The email address that will appear in the "From:" field of invoices
- **Display Name**: The name that appears next to the email (what customers see)

---

### Step 5: Submit the Form

1. Fill in all fields
2. Click **"Create"** button
3. SendGrid will show: "Verification email sent"

---

### Step 6: Check Your Email

1. Go to your **email inbox** (the email you entered)
2. Look for email from SendGrid
3. Subject line will be something like: **"Verify your sender"** or **"Authenticate Your Sender"**
4. **⚠️ Check spam/junk folder** if you don't see it in inbox

---

### Step 7: Click Verification Link

1. Open the email from SendGrid
2. Find the verification link (button or hyperlink)
3. **Click the link**
4. A page will open saying "Verified!" or "Sender verified"

---

### Step 8: Wait for SendGrid Update

1. Wait **1-2 minutes**
2. SendGrid backend needs to update
3. No action needed, just wait

---

### Step 9: Verify It Worked

1. Go back to SendGrid Sender Authentication page
2. Refresh the page
3. Your sender should show **"✓ Verified"** or **green checkmark**

---

## ✅ You're Done!

Your email is now verified. Your Smart Invoice app can now send emails from this address.

---

## 🧪 Test It Works

1. Go back to Smart Invoice app
2. Create a test invoice
3. Click "Send Email"
4. Check if email arrives

**Expected result:**
- ✅ Email arrives
- ✅ "From" shows your business email
- ✅ Invoice PDF is attached

---

## 🆘 Troubleshooting

### Problem: Can't find verification email

**Solution:**
1. Check your **spam/junk folder**
2. Search for "sendgrid" in your email
3. If still missing:
   - Go back to SendGrid Sender Authentication
   - Find your sender
   - Click **"Resend verification"**
   - Wait a few minutes
   - Check email again

---

### Problem: Getting 403 error when sending invoices

**What it means:** Your email isn't verified yet

**Fix:**
1. Make sure you completed all steps above
2. Verify the verification email was confirmed
3. Wait 5 minutes
4. Refresh SendGrid page - should show ✓ Verified
5. Try sending invoice again

---

### Problem: Email says verified but still getting 403 error

**Try this:**
1. Wait 10 minutes (SendGrid backend sync)
2. Or: Create a new API key in SendGrid with "Full Access"
3. Update the SENDGRID_API_KEY in your app settings
4. Try again

---

### Problem: Verification email never arrives

**Try this:**
1. Check spam folder thoroughly
2. Add SendGrid to safe senders (sendgrid.com)
3. Request new verification link from SendGrid
4. Try a different email address if needed
5. Contact SendGrid support if persistent

---

## 📊 What Happens Next

### After Verification

Your SendGrid account can now:
- ✅ Send emails from your verified address
- ✅ Send invoices to customers
- ✅ Track email delivery
- ✅ See open/click rates

### If You Want to Add More Emails

1. Go back to Sender Authentication
2. Click "Create New" again
3. Add another email address
4. Repeat steps 4-8
5. You can verify multiple emails

---

## 💡 Pro Tips

**Tip 1: Verify Once Per Email**
- You only verify each email ONCE
- After verified, it works forever
- No need to re-verify

**Tip 2: Use Professional Email**
- ✅ info@company.com (good)
- ✅ sales@company.com (good)
- ❌ yourname@gmail.com (less professional)
- Business email looks more professional

**Tip 3: Verify Multiple Emails (Optional)**
- You can verify sales@, billing@, support@, etc.
- Each one gets its own verification email
- Use any verified email for sending invoices

**Tip 4: Use Same Email Consistently**
- If you verify sales@company.com
- Always send invoices from sales@company.com
- Don't switch emails frequently
- Customers will recognize your email

---

## 📱 Quick Reference Card

For users to bookmark:

```
SENDGRID EMAIL VERIFICATION CHECKLIST

1. Log in to https://app.sendgrid.com
2. Go to Settings → Sender Authentication
3. Click "Create New"
4. Enter your business email
5. Enter your business name
6. Click "Create"
7. Check your email inbox
8. Click verification link from SendGrid
9. Wait 1-2 minutes
10. Go back to SendGrid, refresh page
11. Should show ✓ Verified
12. Done! Now emails will work

Total time: 5 minutes
```

---

## 🎯 Success Indicators

You'll know it worked when:

✅ SendGrid shows green checkmark  
✅ Email in your app doesn't show error  
✅ Customers receive invoice in their inbox  
✅ Email shows your verified address  

---

## 📞 Need More Help?

**SendGrid Support:**
- https://support.sendgrid.com/
- Live chat available
- Email support

**Smart Invoice Support:**
- Check app documentation
- Run: `python manage.py verify_sendgrid_setup`
- Check console logs for errors

---

**Your email verification is now complete!** 🎉

Your Smart Invoice app will now send all emails from your verified address.
