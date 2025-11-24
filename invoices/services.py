"""
Business logic services for Smart Invoice platform.
Extracts logic from views into reusable service classes.
"""
from django.db import transaction
from decimal import Decimal
from .models import Invoice, LineItem
from .sendgrid_service import SendGridEmailService
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from django.template.loader import render_to_string
import json


class InvoiceService:
    """Handles all invoice operations."""
    
    @staticmethod
    @transaction.atomic
    def create_invoice(user, invoice_data, files_data, line_items_data):
        """Create invoice with line items in atomic transaction.
        
        Returns: (invoice, form) tuple where invoice is the created Invoice or None,
                 and form is the bound form (for displaying errors if invalid).
        """
        from .forms import InvoiceForm
        invoice_form = InvoiceForm(invoice_data, files_data)
        if not invoice_form.is_valid():
            return None, invoice_form
        
        invoice = invoice_form.save(commit=False)
        invoice.user = user
        invoice.save()
        
        for item_data in line_items_data:
            LineItem.objects.create(
                invoice=invoice,
                description=item_data["description"],
                quantity=Decimal(item_data["quantity"]),
                unit_price=Decimal(item_data["unit_price"]),
            )
        
        return invoice, invoice_form
    
    @staticmethod
    @transaction.atomic
    def update_invoice(invoice, invoice_data, files_data, line_items_data):
        """Update invoice with line items in atomic transaction.
        
        Returns: (invoice, form) tuple where invoice is the updated Invoice or None,
                 and form is the bound form (for displaying errors if invalid).
        """
        from .forms import InvoiceForm
        invoice_form = InvoiceForm(invoice_data, files_data, instance=invoice)
        if not invoice_form.is_valid():
            return None, invoice_form
        
        invoice = invoice_form.save()
        invoice.line_items.all().delete()
        
        for item_data in line_items_data:
            LineItem.objects.create(
                invoice=invoice,
                description=item_data["description"],
                quantity=Decimal(item_data["quantity"]),
                unit_price=Decimal(item_data["unit_price"]),
            )
        
        return invoice, invoice_form


class PDFService:
    """Handles PDF generation."""
    
    @staticmethod
    def generate_pdf_bytes(invoice):
        """Generate PDF bytes for invoice."""
        html_string = render_to_string("invoices/invoice_pdf.html", {"invoice": invoice})
        font_config = FontConfiguration()
        html = HTML(string=html_string)
        return html.write_pdf(font_config=font_config)


class AnalyticsService:
    """Handles analytics calculations."""
    
    @staticmethod
    def get_user_dashboard_stats(user):
        """Calculate dashboard statistics for user."""
        all_user_invoices = list(
            Invoice.objects.filter(user=user).prefetch_related('line_items')
        )
        
        paid_invoices = [inv for inv in all_user_invoices if inv.status == "paid"]
        unpaid_invoices = [inv for inv in all_user_invoices if inv.status == "unpaid"]
        
        total_revenue = sum(inv.total for inv in paid_invoices) if paid_invoices else Decimal("0")
        
        return {
            "total_invoices": len(all_user_invoices),
            "paid_count": len(paid_invoices),
            "unpaid_count": len(unpaid_invoices),
            "total_revenue": total_revenue,
            "unique_clients": len(set(inv.client_email for inv in all_user_invoices)),
        }
