"""
Search and filter utilities for invoice dashboard.
"""

from django.db.models import Q


class InvoiceSearch:
    """Advanced search and filtering for invoices."""

    @staticmethod
    def search(invoices, query):
        """Search invoices by invoice ID, client name, or business name."""
        if not query:
            return invoices

        return invoices.filter(
            Q(invoice_id__icontains=query)
            | Q(client_name__icontains=query)
            | Q(business_name__icontains=query)
            | Q(client_email__icontains=query)
        )

    @staticmethod
    def filter_by_date_range(invoices, start_date, end_date):
        """Filter invoices by date range."""
        if start_date:
            invoices = invoices.filter(invoice_date__gte=start_date)
        if end_date:
            invoices = invoices.filter(invoice_date__lte=end_date)
        return invoices

    @staticmethod
    def filter_by_amount_range(invoices, min_amount, max_amount):
        """Filter invoices by amount range (in-memory filtering needed due to property)."""
        filtered = []
        for invoice in invoices:
            if min_amount and invoice.total < float(min_amount):
                continue
            if max_amount and invoice.total > float(max_amount):
                continue
            filtered.append(invoice)
        return filtered

    @staticmethod
    def filter_by_currency(invoices, currency):
        """Filter invoices by currency."""
        if not currency:
            return invoices
        return invoices.filter(currency=currency)

    @staticmethod
    def filter_by_client(invoices, client_email):
        """Filter invoices by client email."""
        if not client_email:
            return invoices
        return invoices.filter(client_email=client_email)


class InvoiceExport:
    """Utilities for exporting invoices in various formats."""

    @staticmethod
    def export_to_csv(invoices):
        """Export invoices to CSV format."""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["Invoice ID", "Client", "Business", "Amount", "Currency", "Status", "Date"]
        )

        for invoice in invoices:
            writer.writerow(
                [
                    invoice.invoice_id,
                    invoice.client_name,
                    invoice.business_name,
                    invoice.total,
                    invoice.currency,
                    invoice.status,
                    invoice.invoice_date,
                ]
            )

        return output.getvalue()

    @staticmethod
    def bulk_export_pdfs(invoices):
        """Prepare multiple invoices for bulk PDF export."""
        from weasyprint import HTML
        from django.template.loader import render_to_string
        from weasyprint.text.fonts import FontConfiguration
        import logging

        logger = logging.getLogger(__name__)
        pdfs = []
        for invoice in invoices:
            try:
                html_string = render_to_string("invoices/invoice_pdf.html", {"invoice": invoice})
                font_config = FontConfiguration()
                html = HTML(string=html_string)
                pdf = html.write_pdf(font_config=font_config)
                pdfs.append((invoice.invoice_id, pdf))
            except Exception as e:
                logger.error(f"Error generating PDF for invoice {invoice.invoice_id}: {str(e)}")

        return pdfs
