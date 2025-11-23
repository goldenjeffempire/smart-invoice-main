# Optional: Verify Your Email for Direct Sending

**Time Required**: 5 minutes  
**Difficulty**: Very Easy  
**Required?**: No - your emails work without this!

---

## 🎯 What Is Email Verification?

By default, your invoices work perfectly! 

But if you want customers to see **your email address** instead of the platform's, you can verify your email in SendGrid.

---

## 📋 Do You Need This?

### ✅ Verify If You Want:
- Customers to reply directly to your email
- Professional appearance: "From: sales@acme.com"
- More control over email sending

### ✅ Skip If You Want:
- Quick setup (no verification needed)
- System handles it automatically
- Email works great as-is

---

## Step-by-Step Verification (Optional)

### Step 1: Access SendGrid

Ask your platform owner for SendGrid access, OR:
1. Go to: **https://app.sendgrid.com**
2. Log in with your account
3. You're in the SendGrid Dashboard

---

### Step 2: Go to Sender Authentication

1. Left sidebar → Click **Settings**
2. Click **Sender Authentication**
3. See: "Authenticate your domain and verify your senders"

**Direct Link**: https://app.sendgrid.com/settings/sender_authentication

---

### Step 3: Create New Sender

1. Click **"Create New"** button
2. A form appears

---

### Step 4: Fill In Your Email

| Field | Enter | Example |
|-------|-------|---------|
| **Email** | Your business email | sales@acme.com |
| **Name** | Your business name | ACME Corp |

---

### Step 5: Create & Verify

1. Click **"Create"**
2. Check your email inbox (sales@acme.com)
3. Look for email from SendGrid
4. Click the **verification link**

---

### Step 6: Wait & Confirm

1. Wait **1-2 minutes** for SendGrid to update
2. Go back to Sender Authentication page
3. Refresh the page
4. Should show **✓ Verified** with green checkmark

---

### Step 7: Done! ✅

Your email is verified. Next time you send an invoice:
- Email will come FROM your verified address
- Customers see: sales@acme.com

---

## ✨ After Verification

### Without Verification
```
Platform sends invoice:
├─ FROM: sales@acme.com (attempted)
└─ If not verified: Auto-fallback to platform email
```

### After Verification ✅
```
Platform sends invoice:
├─ FROM: sales@acme.com (verified)
└─ Email goes directly from your address
```

---

## 💡 Tips

**Professional Emails:**
- ✅ sales@company.com
- ✅ invoices@company.com
- ❌ personal@gmail.com

**Verify Multiple:**
- Can verify sales@, billing@, support@
- Each one independently
- Use any for sending

---

## 🆘 Troubleshooting

### Verification email not received?
1. Check spam folder
2. Ask platform owner to resend
3. Wait a few minutes

### Still not working after verification?
1. Wait 1-2 minutes for SendGrid sync
2. Check green checkmark on SendGrid page
3. Create new invoice and try again

---

## 🎉 You're All Set!

Your email is now verified.

**Next invoice you send will automatically use your email address.**

No more setup needed! 🚀
