"""
Async task processing for InvoiceFlow platform.
Uses ThreadPoolExecutor for background task execution without Redis/Celery dependency.
"""

import logging
import functools
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Callable, Dict, Optional
from threading import Lock

logger = logging.getLogger(__name__)

_executor: Optional[ThreadPoolExecutor] = None
_executor_lock = Lock()
MAX_WORKERS = 4


def get_executor() -> ThreadPoolExecutor:
    """Get or create the global thread pool executor."""
    global _executor
    if _executor is None:
        with _executor_lock:
            if _executor is None:
                _executor = ThreadPoolExecutor(
                    max_workers=MAX_WORKERS,
                    thread_name_prefix="async_task"
                )
                logger.info(f"Created ThreadPoolExecutor with {MAX_WORKERS} workers")
    return _executor


def shutdown_executor(wait: bool = True) -> None:
    """Shutdown the executor gracefully."""
    global _executor
    if _executor is not None:
        with _executor_lock:
            if _executor is not None:
                _executor.shutdown(wait=wait)
                _executor = None
                logger.info("ThreadPoolExecutor shutdown complete")


def run_async(func: Callable) -> Callable:
    """Decorator to run a function asynchronously in the thread pool.
    
    Usage:
        @run_async
        def my_slow_task(arg1, arg2):
            # This runs in background thread
            do_something_slow()
    
    The decorated function returns a Future that can be used to get the result.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Future:
        executor = get_executor()
        future = executor.submit(func, *args, **kwargs)
        logger.debug(f"Submitted async task: {func.__name__}")
        return future
    return wrapper


class AsyncTaskService:
    """Service for managing async background tasks."""

    @staticmethod
    def submit_task(func: Callable, *args, **kwargs) -> Future:
        """Submit a function to run asynchronously.
        
        Args:
            func: The function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Future object that can be used to check status or get result
        """
        executor = get_executor()
        
        def task_wrapper():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Async task {func.__name__} failed: {e}")
                raise
        
        future = executor.submit(task_wrapper)
        logger.debug(f"Submitted task: {func.__name__}")
        return future

    @staticmethod
    def generate_pdf_async(invoice_id: int) -> Future:
        """Generate PDF for an invoice asynchronously.
        
        Returns a Future that resolves to the PDF bytes.
        """
        from .models import Invoice
        from .services import PDFService
        
        def _generate():
            try:
                invoice = Invoice.objects.select_related().prefetch_related('line_items').get(id=invoice_id)
                pdf_bytes = PDFService.generate_pdf_bytes(invoice)
                logger.info(f"Generated PDF for invoice #{invoice.invoice_id} ({len(pdf_bytes)} bytes)")
                return pdf_bytes
            except Invoice.DoesNotExist:
                logger.error(f"Invoice {invoice_id} not found for PDF generation")
                raise
            except Exception as e:
                logger.exception(f"Failed to generate PDF for invoice {invoice_id}: {e}")
                raise
        
        return AsyncTaskService.submit_task(_generate)

    @staticmethod
    def send_invoice_email_async(invoice_id: int, recipient_email: str) -> Future:
        """Send invoice email asynchronously with proper error handling.
        
        Returns a Future that resolves to the send result dict.
        """
        from .models import Invoice
        from .sendgrid_service import SendGridEmailService
        
        def _send():
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                service = SendGridEmailService()
                result = service.send_invoice_ready(invoice, recipient_email)
                
                if result.get("status") == "sent":
                    logger.info(
                        f"Invoice #{invoice.invoice_id} sent to {recipient_email}",
                        extra={"invoice_id": invoice_id, "recipient": recipient_email}
                    )
                elif result.get("configured") is False:
                    logger.warning(
                        f"Email delivery disabled for invoice #{invoice.invoice_id}",
                        extra={"invoice_id": invoice_id}
                    )
                else:
                    logger.error(
                        f"Failed to send invoice email: {result.get('message')}",
                        extra={"invoice_id": invoice_id, "error": result.get("message")}
                    )
                return result
            except Invoice.DoesNotExist:
                logger.error(f"Invoice {invoice_id} not found for email sending")
                return {"status": "error", "message": "Invoice not found"}
            except Exception as e:
                logger.exception(f"Unexpected error sending invoice email: {e}")
                return {"status": "error", "message": str(e)}
        
        return AsyncTaskService.submit_task(_send)

    @staticmethod
    def send_payment_reminder_async(invoice_id: int) -> Future:
        """Send payment reminder email asynchronously.
        
        Returns a Future that resolves to the send result dict.
        """
        from .models import Invoice
        from .sendgrid_service import SendGridEmailService
        
        def _send():
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                service = SendGridEmailService()
                result = service.send_payment_reminder(invoice, invoice.client_email)
                
                if result.get("status") == "sent":
                    logger.info(f"Payment reminder sent for invoice #{invoice.invoice_id}")
                else:
                    logger.error(f"Failed to send reminder: {result.get('message')}")
                return result
            except Exception as e:
                logger.exception(f"Error sending payment reminder: {e}")
                return {"status": "error", "message": str(e)}
        
        return AsyncTaskService.submit_task(_send)

    @staticmethod
    def generate_and_email_invoice(invoice_id: int, recipient_email: str) -> Future:
        """Generate PDF and send invoice email as a combined async task.
        
        This is useful when both operations need to happen together.
        """
        from .models import Invoice
        from .services import PDFService
        from .sendgrid_service import SendGridEmailService
        
        def _generate_and_send():
            try:
                invoice = Invoice.objects.select_related().prefetch_related('line_items').get(id=invoice_id)
                
                pdf_bytes = PDFService.generate_pdf_bytes(invoice)
                logger.info(f"Generated PDF for invoice #{invoice.invoice_id}")
                
                service = SendGridEmailService()
                result = service.send_invoice_ready(invoice, recipient_email)
                
                if result.get("status") == "sent":
                    logger.info(f"Invoice #{invoice.invoice_id} generated and sent to {recipient_email}")
                
                return {
                    "pdf_generated": True,
                    "pdf_size": len(pdf_bytes),
                    "email_result": result
                }
            except Exception as e:
                logger.exception(f"Failed to generate and send invoice {invoice_id}: {e}")
                return {
                    "pdf_generated": False,
                    "email_result": {"status": "error", "message": str(e)}
                }
        
        return AsyncTaskService.submit_task(_generate_and_send)
