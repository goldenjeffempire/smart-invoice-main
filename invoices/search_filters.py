import csv
import io
from django.http import HttpResponse

class InvoiceExport:
    """Export utilities for invoices."""
    
    @staticmethod
    def export_to_csv(invoices):
        """Export invoices to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Invoice #', 'Client', 'Amount', 'Status', 
            'Issue Date', 'Due Date', 'Description'
        ])
        
        for invoice in invoices:
            writer.writerow([
                invoice.invoice_number,
                invoice.client_name,
                str(invoice.total_amount),
                invoice.status,
                invoice.issue_date.strftime('%Y-%m-%d'),
                invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                invoice.description or ''
            ])
        
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invoices.csv"'
        return response
    
    @staticmethod
    def bulk_export_pdfs(invoices):
        """Generate bulk PDF export for invoices."""
        return HttpResponse(
            "PDF export is currently being rebuilt.",
            content_type='text/plain'
        )
