# SendGrid Dynamic Templates Integration

Your Smart Invoice platform now integrates with SendGrid dynamic templates for professional, scalable email sending.

## Features

✅ **SendGrid Dynamic Templates**
- Professional email templates with dynamic data
- Invoice data automatically injected into template
- Professional styling and formatting
- Reliable delivery tracking

✅ **Automatic Fallback**
- If SendGrid not configured: Uses Django email backend
- If template ID not set: Falls back to simple HTML email
- No disruption to functionality

✅ **PDF Attachments**
- Invoice PDF automatically generated
- Attached to every email
- Base64 encoded for reliable delivery

## Setup Instructions

### 1. Get SendGrid API Key
1. Go to https://app.sendgrid.com/settings/api_keys
2. Click "Create API Key"
3. Give it a name (e.g., "Smart Invoice")
4. Select "Full Access" (or minimal permissions: Mail Send, Template Read)
5. Copy the API key

### 2. Set API Key in Replit
1. Go to Replit Secrets (lock icon)
2. Add secret: `SENDGRID_API_KEY` = (your API key from step 1)

### 3. Create Dynamic Template in SendGrid
1. Go to https://app.sendgrid.com/dynamic_templates
2. Click "Create a Dynamic Template"
3. Click "Create Template"
4. Name it "Invoice Email"
5. Create a new version (Blank template)
6. Use the template variables in your HTML:

```handlebars
{{invoice_id}}
{{invoice_date}}
{{due_date}}
{{client_name}}
{{client_email}}
{{business_name}}
{{currency}}
{{total}}
{{line_items}}
```

### 4. Copy Template ID
1. Click the template you created
2. Copy the Template ID (starts with "d-")
3. Add to Replit Secrets: `SENDGRID_INVOICE_TEMPLATE_ID` = (your template ID)

### 5. Example Dynamic Template HTML

```html
<h2>Invoice {{invoice_id}}</h2>

<p>Dear {{client_name}},</p>

<p>Thank you for your business! Please find attached your invoice.</p>

<h3>Invoice Details</h3>
<table>
  <tr>
    <td><strong>Invoice #:</strong></td>
    <td>{{invoice_id}}</td>
  </tr>
  <tr>
    <td><strong>Date:</strong></td>
    <td>{{invoice_date}}</td>
  </tr>
  <tr>
    <td><strong>Due Date:</strong></td>
    <td>{{due_date}}</td>
  </tr>
  <tr>
    <td><strong>Total:</strong></td>
    <td>{{currency}} {{total}}</td>
  </tr>
</table>

<h3>Line Items</h3>
{{#each line_items}}
<div>
  {{this.description}} - {{this.quantity}} x {{this.unit_price}} = {{this.total}}
</div>
{{/each}}

<p>Best regards,<br>{{business_name}}</p>
```

## Available Template Variables

```javascript
{
  "invoice_id": "INV-001",
  "invoice_date": "November 22, 2025",
  "due_date": "December 22, 2025",
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "client_address": "123 Main St",
  "business_name": "Your Company",
  "business_email": "invoice@company.com",
  "business_phone": "+1-234-567-8900",
  "business_address": "456 Business Ave",
  "currency": "USD",
  "subtotal": "1000.00",
  "tax_amount": "100.00",
  "total": "1100.00",
  "notes": "Thank you for your business",
  "status": "paid",
  "line_items": [
    {
      "description": "Item name",
      "quantity": "1",
      "unit_price": "500.00",
      "total": "500.00"
    }
  ],
  "payment_info": {
    "bank_name": "Bank Name",
    "account_name": "Account Holder",
    "account_number": "****1234"
  }
}
```

## Testing

1. Create an invoice in Smart Invoice
2. Click "Send via Email"
3. Enter recipient email
4. Check SendGrid dashboard for delivery status

## Features

- ✅ Professional email styling
- ✅ Invoice PDF attachment
- ✅ Dynamic data injection
- ✅ Delivery tracking
- ✅ Bounce/complaint handling
- ✅ SMTP logs in SendGrid dashboard

## Troubleshooting

### Email not sending?
1. Check SENDGRID_API_KEY is set in Secrets
2. Verify API key has Mail Send permission
3. Check email address is valid
4. View SendGrid Activity Feed: https://app.sendgrid.com/email_activity

### Template not working?
1. Verify SENDGRID_INVOICE_TEMPLATE_ID is correct
2. Check template is published in SendGrid
3. Verify template has an active version
4. Check variable names match exactly

### Still having issues?
1. Check application logs in Replit console
2. Verify sender email (business_email) is verified in SendGrid
3. Ensure API key hasn't expired

---

**That's it!** Your Smart Invoice now uses professional SendGrid templates for invoice delivery.
