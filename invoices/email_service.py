"""Improved email service with better error handling and thread management."""

import logging
import threading
from .models import Invoice
from .sendgrid_service import SendGridEmailService

logger = logging.getLogger(__name__)


class EmailService:
    """Enhanced email service with proper error handling and logging."""

    @staticmethod
    def send_invoice_email_async(invoice_id: int, recipient_email: str) -> None:
        """
        Send invoice email in background thread with proper error handling.

        NOTE: For production deployment, replace with Celery + Redis for:
        - Retry logic on failures
        - Task monitoring and observability
        - Guaranteed delivery
        - Proper queue management
        """

        def _send_with_error_handling():
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                service = SendGridEmailService()
                result = service.send_invoice_ready(invoice, recipient_email)

                if result.get("status") == "sent":
                    logger.info(
                        f"Invoice #{invoice.invoice_id} sent to {recipient_email}",
                        extra={"invoice_id": invoice_id, "recipient": recipient_email},
                    )
                elif result.get("configured") is False:
                    logger.warning(
                        f"Email delivery disabled for invoice #{invoice.invoice_id}",
                        extra={"invoice_id": invoice_id},
                    )
                else:
                    logger.error(
                        f"Failed to send invoice email: {result.get('message')}",
                        extra={"invoice_id": invoice_id, "error": result.get("message")},
                    )
            except Invoice.DoesNotExist:
                logger.error(f"Invoice {invoice_id} not found for email sending")
            except Exception as e:
                logger.exception(
                    f"Unexpected error sending invoice email: {str(e)}",
                    extra={"invoice_id": invoice_id, "error": str(e)},
                )

        # Create thread with proper error handling
        thread = threading.Thread(
            target=_send_with_error_handling, name=f"email-invoice-{invoice_id}", daemon=True
        )
        thread.start()

        # Log thread creation
        logger.debug(
            f"Started email thread for invoice {invoice_id}", extra={"thread_name": thread.name}
        )

    @staticmethod
    def send_payment_reminder_async(invoice_id: int) -> None:
        """Send payment reminder email in background thread."""

        def _send_reminder():
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                service = SendGridEmailService()
                result = service.send_payment_reminder(invoice, invoice.client_email)

                if result.get("status") == "sent":
                    logger.info(f"Payment reminder sent for invoice #{invoice.invoice_id}")
                else:
                    logger.error(f"Failed to send reminder: {result.get('message')}")
            except Exception as e:
                logger.exception(f"Error sending payment reminder: {str(e)}")

        thread = threading.Thread(
            target=_send_reminder, name=f"reminder-invoice-{invoice_id}", daemon=True
        )
        thread.start()
