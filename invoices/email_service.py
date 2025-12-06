"""Email service using AsyncTaskService for background processing."""

import logging
from .async_tasks import AsyncTaskService

logger = logging.getLogger(__name__)


class EmailService:
    """Email service with async background processing via thread pool."""

    @staticmethod
    def send_invoice_email_async(invoice_id: int, recipient_email: str) -> None:
        """Send invoice email in background using thread pool.
        
        Uses AsyncTaskService for proper thread pool management.
        """
        AsyncTaskService.send_invoice_email_async(invoice_id, recipient_email)
        logger.debug(f"Queued invoice email for invoice {invoice_id} to {recipient_email}")

    @staticmethod
    def send_payment_reminder_async(invoice_id: int) -> None:
        """Send payment reminder email in background using thread pool."""
        AsyncTaskService.send_payment_reminder_async(invoice_id)
        logger.debug(f"Queued payment reminder for invoice {invoice_id}")
