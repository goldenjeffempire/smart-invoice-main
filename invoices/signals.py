"""Signal handlers for InvoiceFlow emails and cache invalidation."""

import logging
from typing import Any, Type

from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Invoice, LineItem
from .sendgrid_service import SendGridEmailService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_welcome_email_on_signup(sender, instance, created, **kwargs):
    """Send welcome email when new user is created."""
    if created:
        try:
            service = SendGridEmailService()
            result = service.send_welcome_email(instance)
            if result.get("status") == "sent":
                logger.info(f"Welcome email sent to {instance.email}")
            elif result.get("configured") is False:
                logger.warning("Email delivery disabled for welcome email")
            else:
                logger.error(f"Failed to send welcome email: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error in signup signal: {str(e)}")


@receiver(post_save, sender=Invoice)
def handle_invoice_status_change(sender, instance, created, **kwargs):
    """Send appropriate email when invoice status changes."""
    if not created:
        try:
            old_instance = Invoice.objects.get(pk=instance.pk)  # type: ignore
            if old_instance.status != instance.status and instance.status == "paid":
                service = SendGridEmailService()
                result = service.send_invoice_paid(instance, instance.client_email)
                if result.get("status") == "sent":
                    logger.info(f"Invoice paid email sent for Invoice #{instance.invoice_id}")
                elif result.get("configured") is False:
                    logger.warning("Email delivery disabled for paid notification")
                else:
                    logger.error(f"Failed to send invoice paid email: {result.get('message')}")
        except Exception as e:
            logger.error(f"Error in invoice status change handler: {str(e)}")


@receiver(post_delete, sender=Invoice)
def invalidate_cache_on_invoice_delete(
    sender: Type[Invoice], instance: Invoice, **kwargs: Any
) -> None:
    """Invalidate user analytics cache when invoice is deleted."""
    from .services import AnalyticsService

    try:
        AnalyticsService.invalidate_user_cache(instance.user_id)
        logger.debug(f"Cache invalidated for user {instance.user_id} on invoice delete")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache on invoice delete: {e}")


@receiver(post_delete, sender=LineItem)
def invalidate_cache_on_lineitem_delete(
    sender: Type[LineItem], instance: LineItem, **kwargs: Any
) -> None:
    """Invalidate user analytics cache when line item is deleted."""
    from .services import AnalyticsService

    try:
        if instance.invoice_id:
            user_id = instance.invoice.user_id
            AnalyticsService.invalidate_user_cache(user_id)
            logger.debug(f"Cache invalidated for user {user_id} on lineitem delete")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache on lineitem delete: {e}")


@receiver(user_logged_in)
def warm_cache_on_login(sender: Any, request: Any, user: Any, **kwargs: Any) -> None:
    """Pre-warm user analytics cache on login for faster dashboard loads."""
    from .services import CacheWarmingService

    try:
        CacheWarmingService.warm_user_cache_async(user)
        logger.debug(f"Cache warming initiated for user {user.id} on login")
    except Exception as e:
        logger.warning(f"Failed to warm cache on login: {e}")
