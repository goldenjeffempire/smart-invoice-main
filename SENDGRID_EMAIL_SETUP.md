# SendGrid Email Templates Setup Guide

This guide explains how to set up all 6 SendGrid dynamic email templates for Smart Invoice.

## Status

✅ **Email System Ready** - The app can send emails via SendGrid with API key already configured!
- API Key: Already set in environment secrets
- Email Service: Fully implemented with 6 template types
- Fallback: System sends formatted HTML emails even without template IDs

## Email Types Implemented

1. **Invoice Ready** - Sent when invoice is created/ready to send
2. **Invoice Paid** - Sent when invoice status changes to paid
3. **Payment Reminder** - Sent to remind client about pending payment
4. **New User Welcome** - Sent automatically to new signup
5. **Password Reset** - Sent for password reset requests
6. **Admin Alert** - Sent to admin for important events (invoice viewed, etc)

## How to Enable Dynamic Templates (Optional)

If you want to use SendGrid's dynamic template feature for enhanced email designs:

### Step 1: Create Templates in SendGrid Dashboard

1. Login to [SendGrid Dashboard](https://app.sendgrid.com)
2. Go to **Email API** → **Dynamic Templates**
3. Click **Create a Dynamic Template**
4. For each template below, create it and note the **Template ID** (starts with `d-`)

#### Template 1: Invoice Ready Email
```
Name: Invoice Ready
Template ID: d-xxxxxxxxxxxxxx
Variables:
- {{invoice_id}}
- {{invoice_date}}
- {{due_date}}
- {{client_name}}
- {{business_name}}
- {{business_email}}
- {{currency}}
- {{total_amount}}
- {{invoice_url}}
```

#### Template 2: Invoice Paid
```
Name: Invoice Paid
Template ID: d-xxxxxxxxxxxxxx
Variables:
- {{invoice_id}}
- {{client_name}}
- {{business_name}}
- {{currency}}
- {{total_amount}}
- {{paid_date}}
```

#### Template 3: Payment Reminder
```
Name: Payment Reminder
Template ID: d-xxxxxxxxxxxxxx
Variables:
- {{invoice_id}}
- {{client_name}}
- {{business_name}}
- {{amount_due}}
- {{due_date}}
- {{days_overdue}}
- {{payment_info}}
- {{invoice_url}}
```

#### Template 4: New User Welcome
```
Name: Welcome Email
Template ID: d-xxxxxxxxxxxxxx
Variables:
- {{first_name}}
- {{username}}
- {{email}}
- {{dashboard_url}}
- {{help_url}}
```

#### Template 5: Password Reset
```
Name: Password Reset
Template ID: d-xxxxxxxxxxxxxx
Variables:
- {{first_name}}
- {{username}}
- {{reset_url}}
- {{expires_in}}
- {{support_email}}
```

#### Template 6: Admin Alert
```
Name: Admin Alert
Template ID: d-xxxxxxxxxxxxxx
Variables:
- {{alert_type}}
- {{timestamp}}
- {{details}}
- {{action_url}}
- {{invoice_id}}
- {{user_name}}
- {{action_taken}}
```

### Step 2: Add Template IDs to Replit Secrets

In Replit, add these environment variables in the **Secrets** tab:

```
SENDGRID_INVOICE_READY_TEMPLATE_ID=d-xxxxxxxxxxxxxx
SENDGRID_INVOICE_PAID_TEMPLATE_ID=d-xxxxxxxxxxxxxx
SENDGRID_PAYMENT_REMINDER_TEMPLATE_ID=d-xxxxxxxxxxxxxx
SENDGRID_NEW_USER_WELCOME_TEMPLATE_ID=d-xxxxxxxxxxxxxx
SENDGRID_PASSWORD_RESET_TEMPLATE_ID=d-xxxxxxxxxxxxxx
SENDGRID_ADMIN_ALERT_TEMPLATE_ID=d-xxxxxxxxxxxxxx
```

### Step 3: Verify Setup

Run this command to verify templates are configured:

```bash
python manage.py shell
>>> from invoices.sendgrid_service import SendGridEmailService
>>> service = SendGridEmailService()
>>> for name, template_id in service.TEMPLATE_IDS.items():
...     status = "✓" if template_id else "✗"
...     print(f"{status} {name}: {template_id}")
```

## Current Email System Status

### Without Template IDs (Current State)

✅ **WORKING**: System sends formatted HTML emails via SendGrid API
- Clean, professional formatting
- Includes invoice PDFs as attachments
- Supports all 6 email types
- Fallback ensures delivery even if templates not set

### With Template IDs (Optional Enhancement)

✅ **Enhanced**: System uses SendGrid's dynamic templates
- Custom HTML designs
- Better personalization
- Professional branded emails
- Template versioning and A/B testing

## Testing Emails

### Send Test Invoice Email

```python
# In Python shell or script:
from invoices.models import Invoice
from invoices.sendgrid_service import SendGridEmailService

invoice = Invoice.objects.first()
service = SendGridEmailService()

# Send invoice ready email
result = service.send_invoice_ready(invoice, "test@example.com")
print(f"Result: {result}")

# Send payment reminder
result = service.send_payment_reminder(invoice, "test@example.com")
print(f"Result: {result}")

# Send invoice paid notification
result = service.send_invoice_paid(invoice, "test@example.com")
print(f"Result: {result}")
```

### Send Test User Welcome Email

```python
from django.contrib.auth.models import User
from invoices.sendgrid_service import SendGridEmailService

user = User.objects.first()
service = SendGridEmailService()

result = service.send_welcome_email(user)
print(f"Result: {result}")
```

## Troubleshooting

### Email Not Received

1. **Check SendGrid API Status**: Visit https://status.sendgrid.com
2. **Verify API Key**: Ensure `SENDGRID_API_KEY` is set correctly
3. **Check Spam Folder**: Sometimes emails end up in spam
4. **View SendGrid Logs**: Check SendGrid dashboard → Email Activity
5. **Test API Key**: 
   ```bash
   curl -X GET "https://api.sendgrid.com/v3/mail/settings/general" \
     -H "Authorization: Bearer YOUR_SENDGRID_API_KEY"
   ```

### "From" Email Issues

SendGrid requires the "from" email address to be verified. Make sure:
- Invoice business email is verified in SendGrid
- Default from email is verified in SendGrid
- Add verification: https://app.sendgrid.com/settings/sender_auth

## Email Flow Diagram

```
User Creates Invoice
  ↓
System Sends "Invoice Ready" Email
  ├─ Via SendGrid API
  ├─ With PDF attachment
  └─ To client email

User Marks Invoice Paid
  ↓
Signal Handler Triggered
  ↓
System Sends "Invoice Paid" Email
  ├─ Via SendGrid API
  └─ To client email

New User Signup
  ↓
Signal Handler Triggered
  ↓
System Sends "Welcome" Email
  ├─ Via SendGrid API
  └─ To new user email

Admin Views Invoice
  ↓
System Sends "Admin Alert" Email
  ├─ Via SendGrid API
  └─ To admin email
```

## API Reference

### SendGridEmailService Class

```python
from invoices.sendgrid_service import SendGridEmailService

service = SendGridEmailService()

# Invoice Emails
service.send_invoice_ready(invoice, recipient_email)
service.send_invoice_paid(invoice, recipient_email)
service.send_payment_reminder(invoice, recipient_email)

# User Emails
service.send_welcome_email(user)
service.send_password_reset_email(user, reset_token)

# Admin Emails
service.send_admin_alert(alert_type, data, admin_email)
```

## Environment Variables

Required:
- `SENDGRID_API_KEY` - Your SendGrid API key (already set)

Optional (for dynamic templates):
- `SENDGRID_INVOICE_READY_TEMPLATE_ID`
- `SENDGRID_INVOICE_PAID_TEMPLATE_ID`
- `SENDGRID_PAYMENT_REMINDER_TEMPLATE_ID`
- `SENDGRID_NEW_USER_WELCOME_TEMPLATE_ID`
- `SENDGRID_PASSWORD_RESET_TEMPLATE_ID`
- `SENDGRID_ADMIN_ALERT_TEMPLATE_ID`

## Files Modified

- `invoices/sendgrid_service.py` - Core email service with 6 template types
- `invoices/signals.py` - Auto-send welcome and paid notification emails
- `invoices/email_utils.py` - Utility functions for payment reminders and admin alerts
- `invoices/views.py` - Updated to use new SendGrid service
- `invoices/apps.py` - Register signals on app startup

## Next Steps

1. ✅ Email system is **FULLY OPERATIONAL** right now
2. (Optional) Create custom templates in SendGrid for enhanced designs
3. (Optional) Set template IDs in environment variables
4. Test by sending an invoice email
5. Monitor SendGrid dashboard for delivery status

---

**Questions?** Check SendGrid docs: https://docs.sendgrid.com
