"""
Business logic services for InvoiceFlow platform.
Extracts logic from views into reusable service classes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from django.db import transaction
from django.db.models import Count, Sum, F, DecimalField, Value, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import Invoice, LineItem
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
from django.template.loader import render_to_string

if TYPE_CHECKING:
    from .forms import InvoiceForm


class InvoiceService:
    """Handles all invoice operations."""

    @staticmethod
    @transaction.atomic
    def create_invoice(
        user: Any, invoice_data: Any, files_data: Any, line_items_data: List[Dict[str, Any]]
    ) -> Tuple[Optional[Invoice], InvoiceForm]:
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
            LineItem.objects.create(  # type: ignore[attr-defined]
                invoice=invoice,
                description=item_data["description"],
                quantity=Decimal(item_data["quantity"]),
                unit_price=Decimal(item_data["unit_price"]),
            )

        return invoice, invoice_form

    @staticmethod
    @transaction.atomic
    def update_invoice(
        invoice: Invoice,
        invoice_data: Any,
        files_data: Any,
        line_items_data: List[Dict[str, Any]],
    ) -> Tuple[Optional[Invoice], InvoiceForm]:
        """Update invoice with line items in atomic transaction.

        Returns: (invoice, form) tuple where invoice is the updated Invoice or None,
                 and form is the bound form (for displaying errors if invalid).
        """
        from .forms import InvoiceForm

        invoice_form = InvoiceForm(invoice_data, files_data, instance=invoice)
        if not invoice_form.is_valid():
            return None, invoice_form

        invoice = invoice_form.save()
        invoice.line_items.all().delete()  # type: ignore[attr-defined]

        for item_data in line_items_data:
            LineItem.objects.create(  # type: ignore[attr-defined]
                invoice=invoice,
                description=item_data["description"],
                quantity=Decimal(item_data["quantity"]),
                unit_price=Decimal(item_data["unit_price"]),
            )

        return invoice, invoice_form


class PDFService:
    """Handles PDF generation."""

    @staticmethod
    def generate_pdf_bytes(invoice: Invoice) -> bytes:
        """Generate PDF bytes for invoice."""
        html_string = render_to_string("invoices/invoice_pdf.html", {"invoice": invoice})
        font_config = FontConfiguration()
        html = HTML(string=html_string)
        result = html.write_pdf(font_config=font_config)
        if result is None:
            raise ValueError("Failed to generate PDF")
        return result


class AnalyticsService:
    """Handles analytics calculations with optimized database-level SQL aggregations.
    
    Performance Optimizations:
    - Uses Django's annotate() for database-level aggregations
    - Calculates invoice totals using SUM(quantity * unit_price) at DB level
    - Reduces N+1 queries by aggregating in single queries
    - Target: Sub-250ms dashboard load time
    """

    @staticmethod
    def _get_invoice_total_annotation():
        """Returns annotation for calculating invoice total at database level."""
        return Coalesce(
            Sum(F('line_items__quantity') * F('line_items__unit_price')),
            Value(Decimal('0')),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )

    @staticmethod
    def get_user_dashboard_stats(user: Any) -> Dict[str, Any]:
        """Calculate dashboard statistics using optimized database-level aggregations.

        Performance: Single query for counts, single query for revenue aggregation.
        Target response time: <100ms
        """
        invoices = Invoice.objects.filter(user=user)

        stats = invoices.aggregate(
            total_invoices=Count('id'),
            paid_count=Count('id', filter=Q(status='paid')),
            unpaid_count=Count('id', filter=Q(status='unpaid')),
            unique_clients=Count('client_email', distinct=True),
        )

        total_revenue = LineItem.objects.filter(
            invoice__user=user,
            invoice__status='paid'
        ).aggregate(
            total=Coalesce(
                Sum(F('quantity') * F('unit_price')),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )['total']

        return {
            "total_invoices": stats['total_invoices'] or 0,
            "paid_count": stats['paid_count'] or 0,
            "unpaid_count": stats['unpaid_count'] or 0,
            "total_revenue": total_revenue or Decimal('0'),
            "unique_clients": stats['unique_clients'] or 0,
        }

    @staticmethod
    def get_user_analytics_stats(user: Any) -> Dict[str, Any]:
        """Calculate comprehensive analytics using database-level aggregations.

        Performance: Uses aggregate() for all metrics, single query for invoice list.
        Target response time: <200ms
        """
        from datetime import datetime

        invoices = Invoice.objects.filter(user=user)

        stats = invoices.aggregate(
            total_invoices=Count('id'),
            paid_count=Count('id', filter=Q(status='paid')),
            unpaid_count=Count('id', filter=Q(status='unpaid')),
        )

        total_invoices = stats['total_invoices'] or 0
        paid_count = stats['paid_count'] or 0
        unpaid_count = stats['unpaid_count'] or 0

        revenue_stats = LineItem.objects.filter(
            invoice__user=user
        ).aggregate(
            total_revenue=Coalesce(
                Sum(F('quantity') * F('unit_price'), filter=Q(invoice__status='paid')),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            ),
            outstanding_amount=Coalesce(
                Sum(F('quantity') * F('unit_price'), filter=Q(invoice__status='unpaid')),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            ),
            total_all=Coalesce(
                Sum(F('quantity') * F('unit_price')),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            ),
        )

        total_revenue = revenue_stats['total_revenue'] or Decimal('0')
        outstanding_amount = revenue_stats['outstanding_amount'] or Decimal('0')
        total_all = revenue_stats['total_all'] or Decimal('0')

        average_invoice = (total_all / total_invoices) if total_invoices > 0 else Decimal('0')
        payment_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0

        now = datetime.now()
        current_month_invoices = invoices.filter(
            invoice_date__year=now.year,
            invoice_date__month=now.month
        ).count()

        all_invoices_list = list(
            invoices.prefetch_related('line_items').order_by('-created_at')
        )

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
    def get_top_clients(user: Any, limit: int = 10) -> List[Dict[str, Any]]:
        """Calculate top clients with database-level aggregations.

        Performance: Uses annotate() and aggregate() at database level.
        Groups by client_name with revenue and count calculations in SQL.
        """
        from django.db.models import Avg

        clients = Invoice.objects.filter(user=user).values('client_name').annotate(
            invoice_count=Count('id'),
            paid_count=Count('id', filter=Q(status='paid')),
        ).order_by('client_name')

        client_data: Dict[str, Dict[str, Any]] = {}
        for c in clients:
            client_data[c['client_name']] = {
                'client_name': c['client_name'],
                'invoice_count': c['invoice_count'],
                'paid_count': c['paid_count'],
                'total_revenue': Decimal('0'),
                'total_all': Decimal('0'),
            }

        revenue_by_client = LineItem.objects.filter(
            invoice__user=user
        ).values('invoice__client_name').annotate(
            paid_revenue=Coalesce(
                Sum(F('quantity') * F('unit_price'), filter=Q(invoice__status='paid')),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            ),
            total_revenue=Coalesce(
                Sum(F('quantity') * F('unit_price')),
                Value(Decimal('0')),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            ),
        )

        for r in revenue_by_client:
            client_name = r['invoice__client_name']
            if client_name in client_data:
                client_data[client_name]['total_revenue'] = r['paid_revenue']
                client_data[client_name]['total_all'] = r['total_revenue']

        top_clients = sorted(
            [
                {
                    'client_name': data['client_name'],
                    'invoice_count': data['invoice_count'],
                    'total_revenue': data['total_revenue'],
                    'paid_count': data['paid_count'],
                    'avg_invoice': (
                        data['total_all'] / data['invoice_count']
                        if data['invoice_count'] > 0
                        else Decimal('0')
                    ),
                    'payment_rate': (
                        (data['paid_count'] / data['invoice_count'] * 100)
                        if data['invoice_count'] > 0
                        else 0
                    ),
                }
                for data in client_data.values()
            ],
            key=lambda x: x['total_revenue'],
            reverse=True
        )[:limit]

        return top_clients
