"""SendGrid dynamic template email service."""
import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, TemplateId, Personalization, Attachment, FileContent, FileName, FileType
from django.core.files.base import ContentFile
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from django.template.loader import render_to_string


class SendGridTemplateService:
    """Service for sending emails using SendGrid dynamic templates."""
    
    def __init__(self):
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY not configured")
        self.client = SendGridAPIClient(self.api_key)
    
    def send_invoice_with_template(self, invoice, recipient_email, template_id=None):
        """
        Send invoice email using SendGrid dynamic template.
        
        Args:
            invoice: Invoice model instance
            recipient_email: Recipient email address
            template_id: SendGrid template ID (uses default if not provided)
        """
        try:
            # Use provided template ID or fall back to default
            sendgrid_template_id = template_id or os.environ.get(
                "SENDGRID_INVOICE_TEMPLATE_ID",
                None
            )
            
            if not sendgrid_template_id:
                # If no dynamic template ID, fall back to simple HTML email
                return self._send_invoice_simple(invoice, recipient_email)
            
            # Prepare template data
            template_data = self._prepare_template_data(invoice)
            
            # Generate PDF attachment
            pdf_data = self._generate_invoice_pdf(invoice)
            
            # Create Mail object
            message = Mail(
                from_email=From(invoice.business_email, invoice.business_name),
                to_emails=To(recipient_email),
                subject=f"Invoice #{invoice.invoice_id} from {invoice.business_name}",
            )
            
            # Set dynamic template
            message.template_id = TemplateId(sendgrid_template_id)
            
            # Add personalization with template variables
            message.personalizations = [Personalization()]
            message.personalizations[0].to = To(recipient_email)
            message.personalizations[0].dynamic_template_data = template_data
            
            # Add PDF attachment
            if pdf_data:
                attachment = Attachment(
                    FileContent(base64.b64encode(pdf_data).decode()),
                    FileName(f"Invoice_{invoice.invoice_id}.pdf"),
                    FileType("application/pdf")
                )
                message.attachment = attachment
            
            # Send email
            response = self.client.send(message)
            return {"status": "sent", "response": response}
            
        except Exception as e:
            print(f"Error sending invoice with dynamic template: {str(e)}")
            # Fall back to simple email
            return self._send_invoice_simple(invoice, recipient_email)
    
    def _prepare_template_data(self, invoice):
        """Prepare data for SendGrid dynamic template."""
        line_items = []
        for item in invoice.line_items.all():
            line_items.append({
                "description": item.description,
                "quantity": str(item.quantity),
                "unit_price": str(item.unit_price),
                "total": str(item.total),
            })
        
        payment_info = {}
        if invoice.bank_name:
            payment_info = {
                "bank_name": invoice.bank_name,
                "account_name": invoice.account_name,
                "account_number": invoice.account_number,
            }
        
        return {
            "invoice_id": invoice.invoice_id,
            "invoice_date": invoice.invoice_date.strftime("%B %d, %Y"),
            "due_date": invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "",
            "client_name": invoice.client_name,
            "client_email": invoice.client_email,
            "client_address": invoice.client_address,
            "business_name": invoice.business_name,
            "business_email": invoice.business_email,
            "business_phone": invoice.business_phone,
            "business_address": invoice.business_address,
            "currency": invoice.currency,
            "subtotal": str(invoice.subtotal),
            "tax_amount": str(invoice.tax_amount),
            "total": str(invoice.total),
            "notes": invoice.notes,
            "payment_info": payment_info,
            "line_items": line_items,
            "status": invoice.get_status_display(),
        }
    
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
    
    def _send_invoice_simple(self, invoice, recipient_email):
        """Fallback: Send simple HTML email without dynamic template."""
        try:
            payment_info = ""
            if invoice.bank_name:
                payment_info = f"Bank: {invoice.bank_name}\nAccount: {invoice.account_name}\nAccount #: {invoice.account_number}"
            
            plain_message = f"""Dear {invoice.client_name},

Thank you for your business! Please find attached invoice #{invoice.invoice_id}.

Invoice Details:
- Invoice Number: {invoice.invoice_id}
- Invoice Date: {invoice.invoice_date.strftime('%B %d, %Y')}
- Total Amount: {invoice.currency} {invoice.total:.2f}
- Status: {invoice.get_status_display()}

{payment_info}

If you have any questions, please contact us at {invoice.business_email}.

Best regards,
{invoice.business_name}
"""
            
            message = Mail(
                from_email=From(invoice.business_email, invoice.business_name),
                to_emails=To(recipient_email),
                subject=f"Invoice #{invoice.invoice_id} from {invoice.business_name}",
                plain_text_content=plain_message,
            )
            
            # Add PDF attachment
            pdf_data = self._generate_invoice_pdf(invoice)
            if pdf_data:
                attachment = Attachment(
                    FileContent(base64.b64encode(pdf_data).decode()),
                    FileName(f"Invoice_{invoice.invoice_id}.pdf"),
                    FileType("application/pdf")
                )
                message.attachment = attachment
            
            response = self.client.send(message)
            return {"status": "sent", "response": response}
            
        except Exception as e:
            print(f"Error sending simple email: {str(e)}")
            return {"status": "error", "message": str(e)}


def send_invoice_email_sendgrid(invoice, recipient_email):
    """Helper function to send invoice via SendGrid."""
    service = SendGridTemplateService()
    return service.send_invoice_with_template(invoice, recipient_email)
