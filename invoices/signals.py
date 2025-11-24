"""Signal handlers for Smart Invoice emails."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Invoice
from .sendgrid_service import SendGridEmailService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_welcome_email_on_signup(sender, instance, created, **kwargs):
    """Send welcome email when new user is created."""
    if created:
        try:
            service = SendGridEmailService()
            result = service.send_welcome_email(instance)
            if result.get('status') == 'sent':
                logger.info(f"Welcome email sent to {instance.email}")
            elif result.get('configured') is False:
                logger.warning(f"Email delivery disabled for welcome email")
            else:
                logger.error(f"Failed to send welcome email: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error in signup signal: {str(e)}")


@receiver(post_save, sender=Invoice)
def handle_invoice_status_change(sender, instance, created, **kwargs):
    """Send appropriate email when invoice status changes."""
    if not created:
        try:
            old_instance = Invoice.objects.get(pk=instance.pk)
            if old_instance.status != instance.status and instance.status == 'paid':
                service = SendGridEmailService()
                result = service.send_invoice_paid(instance, instance.client_email)
                if result.get('status') == 'sent':
                    logger.info(f"Invoice paid email sent for Invoice #{instance.invoice_id}")
                elif result.get('configured') is False:
                    logger.warning(f"Email delivery disabled for paid notification")
                else:
                    logger.error(f"Failed to send invoice paid email: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error in invoice status change handler: {str(e)}")
