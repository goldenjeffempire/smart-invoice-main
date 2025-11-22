from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from invoices.models import RecurringInvoice, Invoice, LineItem
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


class Command(BaseCommand):
    help = "Generate invoices from recurring invoice configurations"

    def handle(self, *args, **options):
        today = timezone.now().date()
        recurring_invoices = RecurringInvoice.objects.filter(
            status='active',
            next_generation__lte=today
        )

        generated_count = 0
        for recurring in recurring_invoices:
            try:
                if recurring.end_date and today > recurring.end_date:
                    recurring.status = 'ended'
                    recurring.save()
                    continue

                base_invoice = Invoice.objects.filter(
                    user=recurring.user,
                    recurring_invoice=recurring
                ).first()

                if base_invoice:
                    invoice = Invoice(
                        user=recurring.user,
                        business_name=recurring.business_name,
                        business_email=recurring.business_email,
                        client_name=recurring.client_name,
                        client_email=recurring.client_email,
                        client_phone=recurring.client_phone,
                        client_address=recurring.client_address,
                        invoice_date=today,
                        currency=recurring.currency,
                        tax_rate=recurring.tax_rate,
                        recurring_invoice=recurring,
                    )
                    invoice.save()

                    for item in base_invoice.line_items.all():
                        LineItem.objects.create(
                            invoice=invoice,
                            description=item.description,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                        )

                    recurring.last_generated = timezone.now()
                    recurring.next_generation = recurring.generate_next_invoice_date()
                    recurring.save()

                    self.send_invoice_email(invoice)
                    generated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error generating invoice for {recurring.id}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully generated {generated_count} invoices")
        )

    def send_invoice_email(self, invoice):
        """Send generated invoice to client via email."""
        try:
            context = {'invoice': invoice}
            html_message = render_to_string('invoices/invoice_email.html', context)
            email = EmailMessage(
                f"Invoice {invoice.invoice_id}",
                html_message,
                from_email=invoice.business_email,
                to=[invoice.client_email],
            )
            email.content_subtype = "html"
            email.send()
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
