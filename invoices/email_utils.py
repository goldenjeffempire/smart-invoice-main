"""Email utilities and configuration for Smart Invoice."""
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration validator and utilities."""

    @staticmethod
    def validate_smtp_settings():
        """Validate that SMTP settings are properly configured."""
        required_settings = [
            'EMAIL_HOST',
            'EMAIL_PORT',
            'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD',
        ]
        
        missing = []
        for setting in required_settings:
            if not getattr(settings, setting, None):
                missing.append(setting)
        
        if missing:
            raise ImproperlyConfigured(
                f"Missing email settings: {', '.join(missing)}. "
                "Configure SMTP in .env file."
            )
        
        return True

    @staticmethod
    def send_test_email(recipient_email):
        """Send a test email to verify SMTP configuration."""
        try:
            EmailConfig.validate_smtp_settings()
            send_mail(
                subject='Smart Invoice - Email Configuration Test',
                message='If you received this email, your SMTP configuration is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            logger.info(f"Test email sent successfully to {recipient_email}")
            return True, "Test email sent successfully!"
        except ImproperlyConfigured as e:
            logger.error(f"SMTP configuration error: {str(e)}")
            return False, f"Configuration error: {str(e)}"
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False, f"Failed to send email: {str(e)}"


class InvoiceEmailer:
    """Send invoice emails to clients."""

    @staticmethod
    def send_invoice(invoice, client_email=None):
        """Send invoice to client via email."""
        try:
            EmailConfig.validate_smtp_settings()
            
            email = client_email or invoice.client_email
            context = {'invoice': invoice}
            
            html_message = render_to_string('invoices/invoice_email.html', context)
            
            email_msg = EmailMessage(
                subject=f'Invoice {invoice.invoice_id}',
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            
            logger.info(f"Invoice {invoice.invoice_id} sent to {email}")
            return True, "Invoice sent successfully!"
        except ImproperlyConfigured as e:
            logger.error(f"SMTP configuration error: {str(e)}")
            return False, f"Configuration error: {str(e)}"
        except Exception as e:
            logger.error(f"Failed to send invoice: {str(e)}")
            return False, f"Failed to send invoice: {str(e)}"

    @staticmethod
    def send_payment_reminder(invoice):
        """Send payment reminder for unpaid invoices."""
        try:
            EmailConfig.validate_smtp_settings()
            
            context = {
                'invoice': invoice,
                'days_overdue': (timezone.now().date() - invoice.due_date).days
                if invoice.due_date else 0,
            }
            
            html_message = render_to_string('invoices/payment_reminder.html', context)
            
            email_msg = EmailMessage(
                subject=f'Payment Reminder - Invoice {invoice.invoice_id}',
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invoice.client_email],
            )
            email_msg.content_subtype = 'html'
            email_msg.send(fail_silently=False)
            
            logger.info(f"Payment reminder sent for invoice {invoice.invoice_id}")
            return True, "Reminder sent successfully!"
        except Exception as e:
            logger.error(f"Failed to send reminder: {str(e)}")
            return False, f"Failed to send reminder: {str(e)}"
