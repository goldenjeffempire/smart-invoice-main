import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from invoices.models import Invoice, LineItem, RecurringInvoice
from invoices.sendgrid_service import SendGridEmailService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate invoices from recurring invoice configurations"

    def handle(self, *args, **options):
        today = timezone.now().date()
        recurring_invoices = RecurringInvoice.objects.filter(
            status="active", next_generation__lte=today
        )

        generated_count = 0
        email_sent_count = 0

        for recurring in recurring_invoices:
            try:
                if recurring.end_date and today > recurring.end_date:
                    recurring.status = "ended"
                    recurring.save()
                    self.stdout.write(
                        self.style.WARNING(f"Recurring invoice {recurring.id} has ended")
                    )
                    continue

                base_invoice = Invoice.objects.filter(
                    user=recurring.user, recurring_invoice=recurring
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

                    if self.send_invoice_email(invoice):
                        email_sent_count += 1
                    generated_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Generated invoice {invoice.invoice_id} for {recurring.client_name}"
                        )
                    )

            except Exception as e:
                logger.exception(f"Error generating invoice for recurring {recurring.id}")
                self.stdout.write(
                    self.style.ERROR(f"Error generating invoice for {recurring.id}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated {generated_count} invoices, sent {email_sent_count} emails"
            )
        )

    def send_invoice_email(self, invoice):
        """Send generated invoice to client via email using SendGrid service."""
        try:
            service = SendGridEmailService()

            if not service.is_configured:
                logger.warning(
                    f"SendGrid not configured. Skipping email for invoice {invoice.invoice_id}"
                )
                self.stdout.write(
                    self.style.WARNING(
                        f"Email skipped for {invoice.invoice_id} - SendGrid not configured"
                    )
                )
                return False

            result = service.send_invoice_ready(invoice, invoice.client_email)

            if result.get("status") == "sent":
                logger.info(f"Email sent for recurring invoice {invoice.invoice_id}")
                return True
            else:
                logger.error(
                    f"Failed to send email for invoice {invoice.invoice_id}: {result.get('message')}"
                )
                self.stdout.write(
                    self.style.ERROR(
                        f"Email failed for {invoice.invoice_id}: {result.get('message')}"
                    )
                )
                return False

        except Exception as e:
            logger.exception(f"Error sending email for invoice {invoice.invoice_id}")
            self.stdout.write(self.style.ERROR(f"Email error for {invoice.invoice_id}: {str(e)}"))
            return False
