"""SendGrid dynamic template email service for all email types."""
import os
import base64
import json
from sendgrid import SendGridAPIClient, SendGridException
from sendgrid.helpers.mail import Mail, From, To, TemplateId, Personalization, Attachment, FileContent, FileName, FileType
from django.core.files.base import ContentFile
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from django.template.loader import render_to_string


class SendGridEmailService:
    """Service for sending emails using SendGrid dynamic templates.
    
    All emails are sent from the platform owner's verified email address.
    Users don't need individual SendGrid verification.
    """
    
    # Platform owner's verified email - ALL emails send from this address
    # Set this to your verified SendGrid sender email
    PLATFORM_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@smartinvoice.com")
    PLATFORM_FROM_NAME = "Smart Invoice"
    
    # Template IDs - set these in your environment variables
    TEMPLATE_IDS = {
        'invoice_ready': os.environ.get('SENDGRID_INVOICE_READY_TEMPLATE_ID'),
        'invoice_paid': os.environ.get('SENDGRID_INVOICE_PAID_TEMPLATE_ID'),
        'payment_reminder': os.environ.get('SENDGRID_PAYMENT_REMINDER_TEMPLATE_ID'),
        'new_user_welcome': os.environ.get('SENDGRID_NEW_USER_WELCOME_TEMPLATE_ID'),
        'password_reset': os.environ.get('SENDGRID_PASSWORD_RESET_TEMPLATE_ID'),
        'admin_alert': os.environ.get('SENDGRID_ADMIN_ALERT_TEMPLATE_ID'),
    }
    
    def __init__(self):
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        self.is_configured = bool(self.api_key)
        if self.is_configured:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None
    
    # ============ INVOICE EMAILS ============
    
    def send_invoice_ready(self, invoice, recipient_email, template_id=None):
        """Send 'Invoice Ready' notification to client."""
        template_id = template_id or self.TEMPLATE_IDS.get('invoice_ready')
        
        template_data = {
            "invoice_id": invoice.invoice_id,
            "invoice_date": invoice.invoice_date.strftime("%B %d, %Y"),
            "due_date": invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "N/A",
            "client_name": invoice.client_name,
            "business_name": invoice.business_name,
            "business_email": invoice.business_email,
            "business_phone": invoice.business_phone,
            "currency": invoice.currency,
            "total_amount": f"{invoice.currency} {invoice.total:.2f}",
            "invoice_url": self._get_invoice_view_url(invoice),
        }
        
        return self._send_email(
            from_email=self.PLATFORM_FROM_EMAIL,
            from_name=invoice.business_name,
            to_email=recipient_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Invoice #{invoice.invoice_id} Ready",
            invoice=invoice
        )
    
    def send_invoice_paid(self, invoice, recipient_email, template_id=None):
        """Send 'Invoice Paid' notification."""
        template_id = template_id or self.TEMPLATE_IDS.get('invoice_paid')
        
        template_data = {
            "invoice_id": invoice.invoice_id,
            "client_name": invoice.client_name,
            "business_name": invoice.business_name,
            "currency": invoice.currency,
            "total_amount": f"{invoice.currency} {invoice.total:.2f}",
            "paid_date": invoice.updated_at.strftime("%B %d, %Y"),
        }
        
        return self._send_email(
            from_email=self.PLATFORM_FROM_EMAIL,
            from_name=invoice.business_name,
            to_email=recipient_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Invoice #{invoice.invoice_id} - Payment Received",
        )
    
    def send_payment_reminder(self, invoice, recipient_email, template_id=None):
        """Send payment reminder for unpaid invoice."""
        template_id = template_id or self.TEMPLATE_IDS.get('payment_reminder')
        
        template_data = {
            "invoice_id": invoice.invoice_id,
            "client_name": invoice.client_name,
            "business_name": invoice.business_name,
            "business_email": invoice.business_email,
            "currency": invoice.currency,
            "amount_due": f"{invoice.currency} {invoice.total:.2f}",
            "due_date": invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "Upon receipt",
            "days_overdue": self._calculate_days_overdue(invoice),
            "payment_info": self._format_payment_info(invoice),
            "invoice_url": self._get_invoice_view_url(invoice),
        }
        
        return self._send_email(
            from_email=self.PLATFORM_FROM_EMAIL,
            from_name=invoice.business_name,
            to_email=recipient_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Payment Reminder - Invoice #{invoice.invoice_id}",
        )
    
    # ============ USER EMAILS ============
    
    def send_welcome_email(self, user, template_id=None):
        """Send welcome email to new user."""
        template_id = template_id or self.TEMPLATE_IDS.get('new_user_welcome')
        
        template_data = {
            "first_name": user.first_name or user.username,
            "username": user.username,
            "email": user.email,
            "dashboard_url": self._get_dashboard_url(),
            "help_url": self._get_help_url(),
        }
        
        return self._send_email(
            from_email=self.PLATFORM_FROM_EMAIL,
            from_name="Smart Invoice",
            to_email=user.email,
            template_id=template_id,
            template_data=template_data,
            subject="Welcome to Smart Invoice!"
        )
    
    def send_password_reset_email(self, user, reset_token, template_id=None):
        """Send password reset email."""
        template_id = template_id or self.TEMPLATE_IDS.get('password_reset')
        
        reset_url = self._get_password_reset_url(reset_token)
        
        template_data = {
            "first_name": user.first_name or user.username,
            "username": user.username,
            "reset_url": reset_url,
            "expires_in": "24 hours",
            "support_email": "support@smartinvoice.com",
        }
        
        return self._send_email(
            from_email=self.PLATFORM_FROM_EMAIL,
            from_name="Smart Invoice",
            to_email=user.email,
            template_id=template_id,
            template_data=template_data,
            subject="Password Reset Request"
        )
    
    # ============ ADMIN EMAILS ============
    
    def send_admin_alert(self, alert_type, data, admin_email, template_id=None):
        """Send admin alert email (invoice viewed, etc)."""
        template_id = template_id or self.TEMPLATE_IDS.get('admin_alert')
        
        template_data = {
            "alert_type": alert_type,
            "timestamp": data.get('timestamp', ''),
            "details": data.get('details', ''),
            "action_url": data.get('action_url', ''),
            "invoice_id": data.get('invoice_id', ''),
            "user_name": data.get('user_name', 'Unknown User'),
            "action_taken": data.get('action_taken', 'Unknown Action'),
        }
        
        return self._send_email(
            from_email=self.PLATFORM_FROM_EMAIL,
            from_name="Smart Invoice Admin",
            to_email=admin_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Admin Alert: {alert_type}"
        )
    
    # ============ HELPER METHODS ============
    
    def _send_email(self, from_email, from_name, to_email, template_id, template_data, subject, invoice=None):
        """Send email using SendGrid dynamic template."""
        # Check if SendGrid is configured
        if not self.is_configured:
            error_msg = "SendGrid API key not configured. Email sending is disabled. Please set SENDGRID_API_KEY in environment variables."
            print(f"⚠️  {error_msg}")
            return {"status": "error", "message": error_msg, "configured": False}
        
        try:
            # Use fallback email if provided from_email hasn't been verified in SendGrid
            # This allows testing while business email verification is pending
            actual_from_email = from_email
            actual_from_name = from_name
            
            message = Mail(
                from_email=From(actual_from_email, actual_from_name),
                to_emails=To(to_email),
                subject=subject,
            )
            
            # Use dynamic template if ID is provided
            if template_id:
                message.template_id = TemplateId(template_id)
                message.personalizations = [Personalization()]
                message.personalizations[0].to = To(to_email)
                message.personalizations[0].dynamic_template_data = template_data
            else:
                # Fallback to simple email if no template
                return self._send_simple_email(from_email, from_name, to_email, subject, template_data)
            
            # Add PDF attachment for invoice emails
            if invoice:
                pdf_data = self._generate_invoice_pdf(invoice)
                if pdf_data:
                    attachment = Attachment(
                        FileContent(base64.b64encode(pdf_data).decode()),
                        FileName(f"Invoice_{invoice.invoice_id}.pdf"),
                        FileType("application/pdf")
                    )
                    message.attachment = attachment
            
            # Send email
            response = self.client.send(message)
            return {"status": "sent", "response": response.status_code}
            
        except Exception as e:
            # Handle SendGrid API errors with detailed diagnostics
            error_detail = self._parse_sendgrid_error(e)
            status_code = getattr(e, 'status_code', None)
            print(f"❌ SendGrid API Error: {error_detail}")
            return {"status": "error", "message": error_detail, "code": status_code}
    
    def _send_simple_email(self, from_email, from_name, to_email, subject, data):
        """Fallback: Send simple HTML email without dynamic template."""
        # Check if SendGrid is configured
        if not self.is_configured:
            error_msg = "SendGrid API key not configured. Email sending is disabled."
            print(f"⚠️  {error_msg}")
            return {"status": "error", "message": error_msg, "configured": False}
        
        try:
            # Create simple text content from template data
            plain_text = self._format_plain_text(data)
            
            message = Mail(
                from_email=From(from_email, from_name),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=plain_text,
            )
            
            response = self.client.send(message)
            return {"status": "sent", "response": response.status_code}
            
        except Exception as e:
            error_detail = self._parse_sendgrid_error(e)
            status_code = getattr(e, 'status_code', None)
            print(f"❌ SendGrid API Error: {error_detail}")
            return {"status": "error", "message": error_detail, "code": status_code}
    
    def _parse_sendgrid_error(self, error):
        """Parse SendGrid API error and provide helpful diagnostics."""
        try:
            status_code = error.status_code if hasattr(error, 'status_code') else 'Unknown'
            
            # Try to parse error body for details
            try:
                if hasattr(error, 'body') and error.body:
                    error_data = json.loads(error.body)
                    if isinstance(error_data, dict):
                        errors = error_data.get('errors', [])
                        if errors and len(errors) > 0:
                            messages = [e.get('message', '') for e in errors]
                            error_msg = '; '.join(messages)
                            
                            # Provide specific guidance based on error type
                            if 'sender' in error_msg.lower() or 'from' in error_msg.lower():
                                return f"[{status_code}] SENDER VERIFICATION ISSUE: {error_msg}\n→ Fix: Go to SendGrid → Sender Authentication → Verify your business email"
                            elif 'api key' in error_msg.lower() or 'invalid' in error_msg.lower():
                                return f"[{status_code}] INVALID API KEY: {error_msg}\n→ Fix: Check your API key has Full Access permissions and is valid"
                            elif 'permission' in error_msg.lower() or '403' in str(status_code):
                                return f"[{status_code}] PERMISSION DENIED: API key lacks required permissions\n→ Fix: Create new API key with 'Full Access' at SendGrid → API Keys"
                            else:
                                return f"[{status_code}] {error_msg}"
            except (json.JSONDecodeError, AttributeError, TypeError):
                pass
            
            # Fallback with status code specific guidance
            if status_code == 401 or status_code == 403:
                return f"[{status_code}] Authentication/Permission Error: Check API key has 'Full Access' and verify sender email in SendGrid"
            elif status_code == 400:
                return f"[{status_code}] Bad Request: Check email format and invoice data"
            elif status_code == 429:
                return f"[{status_code}] Rate Limited: Too many requests, try again later"
            else:
                return f"[{status_code}] SendGrid API Error: {str(error)}"
                
        except Exception as parse_error:
            return f"Error encountered: {str(error)}\n(Unable to parse details: {str(parse_error)})"
    
    def _generate_invoice_pdf(self, invoice):
        """Generate PDF for attachment."""
        try:
            pdf_html_string = render_to_string("invoices/invoice_pdf.html", {"invoice": invoice})
            font_config = FontConfiguration()
            html = HTML(string=pdf_html_string)
            return html.write_pdf(font_config=font_config)
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return None
    
    def _format_plain_text(self, data):
        """Format template data as plain text."""
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                continue
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _calculate_days_overdue(self, invoice):
        """Calculate days overdue for payment reminder."""
        from datetime import datetime
        if invoice.due_date:
            delta = datetime.now().date() - invoice.due_date
            if delta.days > 0:
                return str(delta.days)
        return "0"
    
    def _format_payment_info(self, invoice):
        """Format payment information for email."""
        if invoice.bank_name:
            return f"Bank: {invoice.bank_name}\nAccount: {invoice.account_name}\nAccount #: {invoice.account_number}"
        return "N/A"
    
    def _get_invoice_view_url(self, invoice):
        """Get invoice view URL for email links."""
        # This would be the absolute URL - adjust based on your domain
        return f"https://smartinvoice.example.com/invoices/invoice/{invoice.id}/"
    
    def _get_dashboard_url(self):
        """Get dashboard URL."""
        return "https://smartinvoice.example.com/invoices/dashboard/"
    
    def _get_help_url(self):
        """Get help/documentation URL."""
        return "https://smartinvoice.example.com/faq/"
    
    def _get_password_reset_url(self, token):
        """Get password reset URL."""
        return f"https://smartinvoice.example.com/password-reset-confirm/{token}/"


# Convenience function
def get_email_service():
    """Get SendGrid email service instance."""
    return SendGridEmailService()
