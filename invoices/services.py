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
    """Handles analytics calculations with optimized SQL aggregations."""
    
    @staticmethod
    def get_user_dashboard_stats(user):
        """Calculate dashboard statistics using optimized database queries.
        
        Uses COUNT aggregations for counts and DISTINCT for unique clients.
        Only fetches paid invoices with line_items for revenue calculation.
        """
        from django.db.models import Count
        
        # Base queryset
        invoices = Invoice.objects.filter(user=user)
        
        # Use database aggregations for counts (no Python loops)
        total_invoices = invoices.count()
        paid_count = invoices.filter(status="paid").count()
        unpaid_count = invoices.filter(status="unpaid").count()
        
        # Unique clients using database DISTINCT (efficient)
        unique_clients = invoices.values('client_email').distinct().count()
        
        # Only fetch paid invoices for revenue calculation (not all invoices)
        # This reduces memory usage significantly for users with many unpaid invoices
        paid_invoices_with_items = list(
            invoices.filter(status="paid")
            .prefetch_related('line_items')
            .only('id', 'tax_rate')  # Only fetch needed fields
        )
        
        # Calculate revenue from paid invoices only
        total_revenue = sum(inv.total for inv in paid_invoices_with_items) if paid_invoices_with_items else Decimal("0")
        
        return {
            "total_invoices": total_invoices,
            "paid_count": paid_count,
            "unpaid_count": unpaid_count,
            "total_revenue": total_revenue,
            "unique_clients": unique_clients,
        }
    
    @staticmethod
    def get_user_analytics_stats(user):
        """Calculate comprehensive analytics using optimized SQL.
        
        This method computes totals, averages, and client statistics using
        database aggregations instead of Python loops for better performance.
        """
        from django.db.models import Q, Sum, Avg, Count, Case, When, DecimalField
        from datetime import datetime
        
        # Base queryset
        invoices = Invoice.objects.filter(user=user)
        
        # Get counts efficiently
        total_invoices = invoices.count()
        paid_count = invoices.filter(status="paid").count()
        unpaid_count = invoices.filter(status="unpaid").count()
        
        # Since total is a property (not a DB field), we need to fetch invoices with line_items
        # but we'll use optimized queries
        paid_invoices = list(invoices.filter(status="paid").prefetch_related('line_items'))
        unpaid_invoices = list(invoices.filter(status="unpaid").prefetch_related('line_items'))
        all_invoices_list = list(invoices.prefetch_related('line_items'))
        
        # Calculate totals from prefetched data
        total_revenue = sum(inv.total for inv in paid_invoices) if paid_invoices else Decimal("0")
        outstanding_amount = sum(inv.total for inv in unpaid_invoices) if unpaid_invoices else Decimal("0")
        average_invoice = (sum(inv.total for inv in all_invoices_list) / len(all_invoices_list)) if all_invoices_list else Decimal("0")
        
        # Payment rate
        payment_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0
        
        # Current month invoices
        now = datetime.now()
        current_month_invoices = invoices.filter(
            invoice_date__year=now.year,
            invoice_date__month=now.month
        ).count()
        
        return {
            "total_invoices": total_invoices,
            "paid_invoices": paid_count,
            "unpaid_invoices": unpaid_count,
            "total_revenue": total_revenue,
            "outstanding_amount": outstanding_amount,
            "average_invoice": average_invoice,
            "payment_rate": payment_rate,
            "current_month_invoices": current_month_invoices,
            "all_invoices": all_invoices_list,
        }
    
    @staticmethod
    def get_top_clients(user, limit=10):
        """Calculate top clients with efficient aggregation.
        
        Groups invoices by client and calculates metrics in Python
        (since total is a property, not aggregatable in SQL).
        """
        from collections import defaultdict
        
        invoices = Invoice.objects.filter(user=user).prefetch_related('line_items').order_by('client_name')
        
        client_data = defaultdict(lambda: {
            "client_name": "",
            "invoice_count": 0,
            "paid_count": 0,
            "total_revenue": Decimal("0"),
            "invoices": []
        })
        
        for invoice in invoices:
            client = client_data[invoice.client_name]
            client["client_name"] = invoice.client_name
            client["invoice_count"] += 1
            client["invoices"].append(invoice)
            if invoice.status == "paid":
                client["paid_count"] += 1
                client["total_revenue"] += invoice.total
        
        top_clients = sorted(
            [
                {
                    "client_name": data["client_name"],
                    "invoice_count": data["invoice_count"],
                    "total_revenue": data["total_revenue"],
                    "paid_count": data["paid_count"],
                    "avg_invoice": sum(inv.total for inv in data["invoices"]) / len(data["invoices"]),
                    "payment_rate": (data["paid_count"] / data["invoice_count"] * 100)
                    if data["invoice_count"] > 0
                    else 0,
                }
                for data in client_data.values()
            ],
            key=lambda x: x["total_revenue"],
            reverse=True,
        )[:limit]
        
        return top_clients
