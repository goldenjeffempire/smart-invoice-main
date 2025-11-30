# SendGrid Email Templates

This directory contains 6 production-ready HTML email templates for InvoiceFlow. These templates are designed to be copy-pasted into SendGrid's Dynamic Template editor.

## Templates

### 1. **invoice_ready.html** - Invoice Ready Notification
- **Purpose**: Notify clients when they receive a new invoice
- **Template Variables**:
  - `{{invoice_id}}` - Invoice number
  - `{{client_name}}` - Client's name
  - `{{business_name}}` - Sender's business name
  - `{{business_email}}` - Business contact email
  - `{{business_phone}}` - Business phone number
  - `{{invoice_date}}` - Invoice issue date
  - `{{due_date}}` - Payment due date
  - `{{total_amount}}` - Total amount formatted with currency
  - `{{invoice_url}}` - Link to view the invoice online

### 2. **invoice_paid.html** - Payment Received Confirmation
- **Purpose**: Confirm payment receipt to clients
- **Template Variables**:
  - `{{invoice_id}}` - Invoice number
  - `{{client_name}}` - Client's name
  - `{{business_name}}` - Business name
  - `{{total_amount}}` - Amount paid formatted with currency
  - `{{paid_date}}` - Date payment was received

### 3. **payment_reminder.html** - Overdue Payment Reminder
- **Purpose**: Remind clients about overdue invoices
- **Template Variables**:
  - `{{invoice_id}}` - Invoice number
  - `{{client_name}}` - Client's name
  - `{{business_name}}` - Business name
  - `{{business_email}}` - Business contact email
  - `{{business_phone}}` - Business phone number
  - `{{due_date}}` - Original due date
  - `{{days_overdue}}` - Number of days past due
  - `{{total_amount}}` - Amount due formatted with currency
  - `{{invoice_url}}` - Link to pay the invoice

### 4. **new_user_welcome.html** - Welcome Email for New Users
- **Purpose**: Onboard new users to InvoiceFlow
- **Template Variables**:
  - `{{first_name}}` - User's first name
  - `{{username}}` - User's username
  - `{{email}}` - User's email
  - `{{dashboard_url}}` - Link to user dashboard
  - `{{help_url}}` - Link to help center

### 5. **password_reset.html** - Password Reset Request
- **Purpose**: Allow users to reset their password securely
- **Template Variables**:
  - `{{first_name}}` - User's first name
  - `{{username}}` - User's username
  - `{{reset_url}}` - Password reset link (with token)
  - `{{expires_in}}` - Link expiration time
  - `{{support_email}}` - Support contact email

### 6. **admin_alert.html** - Administrative Notifications
- **Purpose**: Alert admins about system events
- **Template Variables**:
  - `{{alert_type}}` - Type of alert
  - `{{timestamp}}` - When the event occurred
  - `{{user_name}}` - User who triggered the event
  - `{{action_taken}}` - What action was performed
  - `{{invoice_id}}` - Related invoice number
  - `{{details}}` - Additional event details
  - `{{action_url}}` - Link to review the event

## Setup Instructions

### Step 1: Create SendGrid Account
1. Sign up at [SendGrid.com](https://sendgrid.com)
2. Verify your email address
3. Complete sender authentication

### Step 2: Create Dynamic Templates

For each template:

1. Go to **Email API** → **Dynamic Templates**
2. Click **Create a Dynamic Template**
3. Name it appropriately (e.g., "InvoiceFlow - Invoice Ready")
4. Click **Add Version**
5. Choose **Code Editor**
6. Copy the entire content from the corresponding `.html` file
7. Paste it into the code editor
8. Click **Save**
9. **Copy the Template ID** (format: `d-xxxxxxxxxxxxxxx`)

### Step 3: Configure Environment Variables

Add the template IDs to your `.env` file:

```bash
# SendGrid Configuration
SENDGRID_API_KEY=your_api_key_here
SENDGRID_FROM_EMAIL=noreply@yourverifieddomain.com

# Template IDs (get these from SendGrid dashboard)
SENDGRID_INVOICE_READY_TEMPLATE_ID=d-xxxxxxxxxxxxxxx
SENDGRID_INVOICE_PAID_TEMPLATE_ID=d-xxxxxxxxxxxxxxx
SENDGRID_PAYMENT_REMINDER_TEMPLATE_ID=d-xxxxxxxxxxxxxxx
SENDGRID_NEW_USER_WELCOME_TEMPLATE_ID=d-xxxxxxxxxxxxxxx
SENDGRID_PASSWORD_RESET_TEMPLATE_ID=d-xxxxxxxxxxxxxxx
SENDGRID_ADMIN_ALERT_TEMPLATE_ID=d-xxxxxxxxxxxxxxx
```

### Step 4: Test Your Templates

Use the Django management command:

```bash
python manage.py send_test_email your-email@example.com
```

Or test individual templates in SendGrid:
1. Go to your template in SendGrid
2. Click **Test Data**
3. Add sample JSON data matching the template variables
4. Click **Send Test**

## Template Features

✅ **Fully Responsive** - Mobile-optimized layouts
✅ **Brand Consistent** - Matches InvoiceFlow design system
✅ **Professional Design** - Clean, modern aesthetics
✅ **High Deliverability** - Optimized for email clients
✅ **Dark Mode Ready** - Looks great in dark mode email clients
✅ **Accessible** - WCAG compliant with semantic HTML
✅ **Fast Loading** - Optimized file sizes and inline CSS

## Template Variables Mapping

The `SendGridEmailService` in `invoices/sendgrid_service.py` automatically maps Django model data to these template variables. No additional configuration needed!

## Troubleshooting

**Template not sending?**
- Verify your `SENDGRID_API_KEY` is correct
- Check that your sender email is verified in SendGrid
- Ensure template IDs match exactly (including the `d-` prefix)

**Variables not showing?**
- Check variable names match exactly (case-sensitive)
- Verify the data is being passed from `sendgrid_service.py`
- Use SendGrid's test data feature to debug

**Email going to spam?**
- Complete SendGrid domain authentication
- Avoid spam trigger words
- Ensure proper SPF/DKIM/DMARC records

## Support

For questions or issues:
- Review SendGrid documentation: https://docs.sendgrid.com
- Check the `invoices/sendgrid_service.py` implementation
- Contact InvoiceFlow support

---

**Last Updated**: November 24, 2025
**Version**: 1.0.0
