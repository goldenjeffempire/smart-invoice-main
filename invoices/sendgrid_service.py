"""SendGrid dynamic template email service for all email types."""

import os
import base64
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    From,
    To,
    ReplyTo,
    TemplateId,
    Personalization,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Content,
)
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from django.template.loader import render_to_string


class SendGridEmailService:
    """Service for sending emails using SendGrid dynamic templates with Replit integration support.

    Smart Direct Sending:
    - Emails send FROM platform owner's verified email (technical requirement)
    - Emails show user's business details prominently
    - Reply-To header routes replies directly to user's business email
    - Users can send directly without SendGrid verification!
    """

    # Template IDs - set these in your environment variables
    TEMPLATE_IDS = {
        "invoice_ready": os.environ.get("SENDGRID_INVOICE_READY_TEMPLATE_ID"),
        "invoice_paid": os.environ.get("SENDGRID_INVOICE_PAID_TEMPLATE_ID"),
        "payment_reminder": os.environ.get("SENDGRID_PAYMENT_REMINDER_TEMPLATE_ID"),
        "new_user_welcome": os.environ.get("SENDGRID_NEW_USER_WELCOME_TEMPLATE_ID"),
        "password_reset": os.environ.get("SENDGRID_PASSWORD_RESET_TEMPLATE_ID"),
        "admin_alert": os.environ.get("SENDGRID_ADMIN_ALERT_TEMPLATE_ID"),
    }

    def __init__(self):
        # Try to get credentials from Replit integration first, fall back to environment variables
        self.api_key = None
        self.from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@invoiceflow.com.ng")
        self.PLATFORM_FROM_EMAIL = self.from_email  # Alias for backward compatibility
        self.platform_from_name = "InvoiceFlow"

        # Try Replit integration if available
        if self._try_replit_integration():
            self.is_configured = True
        else:
            # Fall back to environment variables
            self.api_key = os.environ.get("SENDGRID_API_KEY")
            self.is_configured = bool(self.api_key)

        if self.is_configured and self.api_key:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None

    def _try_replit_integration(self) -> bool:
        """Try to get SendGrid credentials from Replit integration connector."""
        try:
            # Check if we're in Replit environment
            hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
            token = os.environ.get("REPL_IDENTITY") or os.environ.get("WEB_REPL_RENEWAL")

            if not hostname or not token:
                return False

            # Prepare token header
            token_header = f"repl {token}" if "REPL_IDENTITY" in os.environ else f"depl {token}"

            # For synchronous operation, we'll try async operations
            import urllib.request
            import json

            url = f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=sendgrid"
            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            req.add_header("X_REPLIT_TOKEN", token_header)

            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                connection = data.get("items", [{}])[0]
                settings = connection.get("settings", {})

                if settings.get("api_key") and settings.get("from_email"):
                    self.api_key = settings["api_key"]
                    self.from_email = settings["from_email"]
                    return True
        except Exception:
            # Silently fall back to environment variables
            pass

        return False

    # ============ INVOICE EMAILS ============

    def send_invoice_ready(self, invoice, recipient_email, template_id=None):
        """Send 'Invoice Ready' notification to client.

        Sends from platform owner's verified email with Reply-To user's business email.
        No SendGrid verification needed for users!
        """
        template_id = template_id or self.TEMPLATE_IDS.get("invoice_ready")

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
            user_business_email=invoice.business_email,
            from_name=invoice.business_name,
            to_email=recipient_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Invoice #{invoice.invoice_id} Ready",
            invoice=invoice,
        )

    def send_invoice_paid(self, invoice, recipient_email, template_id=None):
        """Send 'Invoice Paid' notification.

        Sends from platform owner's verified email with Reply-To user's business email.
        No SendGrid verification needed for users!
        """
        template_id = template_id or self.TEMPLATE_IDS.get("invoice_paid")

        template_data = {
            "invoice_id": invoice.invoice_id,
            "client_name": invoice.client_name,
            "business_name": invoice.business_name,
            "currency": invoice.currency,
            "total_amount": f"{invoice.currency} {invoice.total:.2f}",
            "paid_date": invoice.updated_at.strftime("%B %d, %Y"),
        }

        return self._send_email(
            user_business_email=invoice.business_email,
            from_name=invoice.business_name,
            to_email=recipient_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Invoice #{invoice.invoice_id} - Payment Received",
        )

    def send_payment_reminder(self, invoice, recipient_email, template_id=None):
        """Send payment reminder for unpaid invoice.

        Sends from platform owner's verified email with Reply-To user's business email.
        No SendGrid verification needed for users!
        """
        template_id = template_id or self.TEMPLATE_IDS.get("payment_reminder")

        template_data = {
            "invoice_id": invoice.invoice_id,
            "client_name": invoice.client_name,
            "business_name": invoice.business_name,
            "business_email": invoice.business_email,
            "currency": invoice.currency,
            "amount_due": f"{invoice.currency} {invoice.total:.2f}",
            "due_date": (
                invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "Upon receipt"
            ),
            "days_overdue": self._calculate_days_overdue(invoice),
            "payment_info": self._format_payment_info(invoice),
            "invoice_url": self._get_invoice_view_url(invoice),
        }

        return self._send_email(
            user_business_email=invoice.business_email,
            from_name=invoice.business_name,
            to_email=recipient_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Payment Reminder - Invoice #{invoice.invoice_id}",
        )

    # ============ USER EMAILS ============

    def send_welcome_email(self, user, template_id=None):
        """Send welcome email to new user."""
        template_id = template_id or self.TEMPLATE_IDS.get("new_user_welcome")

        template_data = {
            "first_name": user.first_name or user.username,
            "username": user.username,
            "email": user.email,
            "dashboard_url": self._get_dashboard_url(),
            "help_url": self._get_help_url(),
        }

        return self._send_email(
            user_business_email=None,
            from_name="InvoiceFlow",
            to_email=user.email,
            template_id=template_id,
            template_data=template_data,
            subject="Welcome to InvoiceFlow!",
        )

    def send_password_reset_email(self, user, reset_token, template_id=None):
        """Send password reset email."""
        template_id = template_id or self.TEMPLATE_IDS.get("password_reset")

        reset_url = self._get_password_reset_url(reset_token)

        template_data = {
            "first_name": user.first_name or user.username,
            "username": user.username,
            "reset_url": reset_url,
            "expires_in": "24 hours",
            "support_email": "support@invoiceflow.com.ng",
        }

        return self._send_email(
            user_business_email=None,
            from_name="InvoiceFlow",
            to_email=user.email,
            template_id=template_id,
            template_data=template_data,
            subject="Password Reset Request",
        )

    # ============ ADMIN EMAILS ============

    def send_admin_alert(self, alert_type, data, admin_email, template_id=None):
        """Send admin alert email (invoice viewed, etc)."""
        template_id = template_id or self.TEMPLATE_IDS.get("admin_alert")

        template_data = {
            "alert_type": alert_type,
            "timestamp": data.get("timestamp", ""),
            "details": data.get("details", ""),
            "action_url": data.get("action_url", ""),
            "invoice_id": data.get("invoice_id", ""),
            "user_name": data.get("user_name", "Unknown User"),
            "action_taken": data.get("action_taken", "Unknown Action"),
        }

        return self._send_email(
            user_business_email=None,
            from_name="InvoiceFlow Admin",
            to_email=admin_email,
            template_id=template_id,
            template_data=template_data,
            subject=f"Admin Alert: {alert_type}",
        )

    # ============ HELPER METHODS ============

    def _send_email(
        self,
        user_business_email,
        from_name,
        to_email,
        template_id,
        template_data,
        subject,
        invoice=None,
    ):
        """Send email using SendGrid dynamic template.

        Smart Direct Sending System:
        - Sends FROM platform owner's verified email (technical requirement for deliverability)
        - Sets Reply-To to user's business email (customers reply directly to user)
        - No SendGrid verification needed for users!
        - Recipients see user's business name prominently
        """
        # Check if SendGrid is configured
        if not self.is_configured:
            error_msg = "SendGrid API key not configured. Email sending is disabled. Please set SENDGRID_API_KEY in environment variables."
            print(f"⚠️  {error_msg}")
            return {"status": "error", "message": error_msg, "configured": False}

        try:
            # Always send from platform owner's verified email for deliverability
            # But set Reply-To to user's business email for direct replies

            message = Mail(
                from_email=From(self.from_email, from_name),
                to_emails=To(to_email),
                subject=subject,
            )

            # Set Reply-To header to user's business email
            # This allows customers to reply directly to the user without verification
            if user_business_email:
                message.reply_to = ReplyTo(user_business_email)

            # Use dynamic template if ID is provided
            if template_id:
                message.template_id = TemplateId(template_id)
                message.personalizations = [Personalization()]
                message.personalizations[0].to = To(to_email)
                message.personalizations[0].dynamic_template_data = template_data
            else:
                # Fallback to simple email if no template
                return self._send_simple_email(
                    user_business_email, from_name, to_email, subject, template_data
                )

            # Add PDF attachment for invoice emails
            if invoice:
                pdf_data = self._generate_invoice_pdf(invoice)
                if pdf_data:
                    attachment = Attachment(
                        FileContent(base64.b64encode(pdf_data).decode()),
                        FileName(f"Invoice_{invoice.invoice_id}.pdf"),
                        FileType("application/pdf"),
                    )
                    message.attachment = attachment

            # Send email
            response = self.client.send(message)
            print("✅ Email sent successfully!")
            print(f"   From: {self.from_email} (verified platform email)")
            print(f"   Reply-To: {user_business_email} (user's direct email)")
            print(f"   Display Name: {from_name}")
            return {
                "status": "sent",
                "response": response.status_code,
                "from_email": self.from_email,
                "reply_to": user_business_email,
            }

        except Exception as e:
            error_detail = self._parse_sendgrid_error(e)
            status_code = getattr(e, "status_code", None)
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
            status_code = getattr(e, "status_code", None)
            print(f"❌ SendGrid API Error: {error_detail}")
            return {"status": "error", "message": error_detail, "code": status_code}

    def _parse_sendgrid_error(self, error):
        """Parse SendGrid API error and provide helpful diagnostics."""
        try:
            status_code = error.status_code if hasattr(error, "status_code") else "Unknown"

            # Try to parse error body for details
            try:
                if hasattr(error, "body") and error.body:
                    error_data = json.loads(error.body)
                    if isinstance(error_data, dict):
                        errors = error_data.get("errors", [])
                        if errors and len(errors) > 0:
                            messages = [e.get("message", "") for e in errors]
                            error_msg = "; ".join(messages)

                            # Provide specific guidance based on error type
                            if "sender" in error_msg.lower() or "from" in error_msg.lower():
                                return f"[{status_code}] SENDER VERIFICATION ISSUE: {error_msg}\n→ Fix: Go to SendGrid → Sender Authentication → Verify your business email"
                            elif "api key" in error_msg.lower() or "invalid" in error_msg.lower():
                                return f"[{status_code}] INVALID API KEY: {error_msg}\n→ Fix: Check your API key has Full Access permissions and is valid"
                            elif "permission" in error_msg.lower() or "403" in str(status_code):
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

    def _get_base_url(self):
        """Get base URL from environment or default to production domain."""
        base_url = os.environ.get("WEBHOOK_BASE_URL") or os.environ.get("API_BASE_URL")
        if base_url:
            return base_url.rstrip("/")
        return "https://invoiceflow.com.ng"

    def _get_invoice_view_url(self, invoice):
        """Get invoice view URL for email links."""
        return f"{self._get_base_url()}/invoices/invoice/{invoice.id}/"

    def _get_dashboard_url(self):
        """Get dashboard URL."""
        return f"{self._get_base_url()}/invoices/dashboard/"

    def _get_help_url(self):
        """Get help/documentation URL."""
        return f"{self._get_base_url()}/faq/"

    def _get_password_reset_url(self, token):
        """Get password reset URL."""
        return f"{self._get_base_url()}/password-reset-confirm/{token}/"

    def send_test_email(self, recipient_email):
        """Send a test email to verify SendGrid configuration.

        Args:
            recipient_email: Email address to send test to

        Returns:
            dict: Result with 'status' and 'message' keys
        """
        if not self.is_configured:
            return {
                "status": "error",
                "configured": False,
                "message": "SendGrid API key not configured",
            }

        try:
            message = Mail()
            message.from_email = From(self.from_email, self.platform_from_name)
            message.to = To(recipient_email)
            message.subject = "InvoiceFlow - Email Test"
            message.content = [
                Content(
                    "text/plain",
                    "If you received this email, your SendGrid configuration is working correctly!",
                ),
                Content(
                    "text/html",
                    "<strong>Success!</strong> If you received this email, your SendGrid configuration is working correctly!",
                ),
            ]

            response = self.client.send(message)

            return {
                "status": "sent",
                "message": f"Test email sent successfully to {recipient_email}",
                "status_code": response.status_code,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to send test email: {str(e)}"}


# Convenience function
def get_email_service():
    """Get SendGrid email service instance."""
    return SendGridEmailService()
