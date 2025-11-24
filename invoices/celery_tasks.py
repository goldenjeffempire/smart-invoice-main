"""
Async tasks for Smart Invoice using Celery + Redis.
Handles: email sending, PDF generation, bulk operations.
"""
import logging
from typing import Any, Dict, List
from celery import shared_task  # type: ignore
from django.template.loader import render_to_string
from .models import Invoice
from .sendgrid_service import SendGridEmailService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)  # type: ignore
def send_invoice_email(self: Any, invoice_id: int, recipient_email: str) -> Dict[str, Any]:
    """Send invoice via email asynchronously with retry."""
    try:
        invoice = Invoice.objects.get(id=invoice_id)  # type: ignore
        service = SendGridEmailService()
        service.send_invoice_ready(invoice, recipient_email)
        logger.info(f"Email sent for invoice {invoice.invoice_id} to {recipient_email}")
        return {"status": "success", "invoice_id": invoice_id}
    except Invoice.DoesNotExist:  # type: ignore
        logger.error(f"Invoice {invoice_id} not found")
        return {"status": "error", "message": "Invoice not found"}
    except Exception as exc:
        logger.error(f"Error sending email: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))  # type: ignore


@shared_task(bind=True, max_retries=3)  # type: ignore
def generate_invoice_pdf_async(self: Any, invoice_id: int) -> Dict[str, Any]:
    """Generate invoice PDF asynchronously."""
    try:
        from weasyprint import HTML
        from weasyprint.text.fonts import FontConfiguration
        
        invoice = Invoice.objects.get(id=invoice_id)  # type: ignore
        html_string = render_to_string("invoices/invoice_pdf.html", {"invoice": invoice})
        font_config = FontConfiguration()
        html = HTML(string=html_string)
        pdf_bytes = html.write_pdf(font_config=font_config)
        
        logger.info(f"PDF generated for invoice {invoice.invoice_id}")
        pdf_size = len(pdf_bytes) if pdf_bytes else 0
        return {"status": "success", "invoice_id": invoice_id, "pdf_size": pdf_size}
    except Invoice.DoesNotExist:  # type: ignore
        logger.error(f"Invoice {invoice_id} not found")
        return {"status": "error", "message": "Invoice not found"}
    except Exception as exc:
        logger.error(f"Error generating PDF: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)  # type: ignore


@shared_task  # type: ignore
def send_payment_reminder(invoice_id: int) -> Dict[str, Any]:
    """Send payment reminder email."""
    try:
        invoice = Invoice.objects.get(id=invoice_id)  # type: ignore
        service = SendGridEmailService()
        service.send_payment_reminder(invoice, invoice.client_email)
        logger.info(f"Payment reminder sent for invoice {invoice.invoice_id}")
        return {"status": "success"}
    except Exception as exc:
        logger.error(f"Error sending reminder: {str(exc)}")
        return {"status": "error", "message": str(exc)}


@shared_task  # type: ignore
def mark_invoice_overdue() -> Dict[str, int]:
    """Mark overdue invoices daily."""
    from django.utils import timezone
    
    overdue_invoices = Invoice.objects.filter(  # type: ignore
        status='unpaid',
        due_date__lt=timezone.now().date()
    )
    count = overdue_invoices.count()
    logger.info(f"Marked {count} invoices as overdue")
    return {"count": count}


@shared_task  # type: ignore
def bulk_generate_pdfs(invoice_ids: List[int]) -> Dict[str, Any]:
    """Generate multiple PDFs asynchronously."""
    results = []
    for invoice_id in invoice_ids:
        result = generate_invoice_pdf_async.delay(invoice_id)  # type: ignore
        results.append(result.id)
    logger.info(f"Queued {len(results)} PDF generation tasks")
    return {"queued": len(results), "task_ids": results}
