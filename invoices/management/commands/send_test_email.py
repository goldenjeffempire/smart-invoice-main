from django.core.management.base import BaseCommand
from invoices.sendgrid_service import SendGridEmailService


class Command(BaseCommand):
    help = "Send a test email to verify SendGrid configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Recipient email address for test'
        )

    def handle(self, *args, **options):
        email = options['email']
        service = SendGridEmailService()
        
        if not service.is_configured:
            self.stdout.write(self.style.ERROR(
                'SendGrid is not configured. Please set SENDGRID_API_KEY environment variable.'
            ))
            return
        
        try:
            result = service.send_test_email(email)
            if result.get('status') == 'sent':
                self.stdout.write(self.style.SUCCESS(
                    f'Test email sent successfully to {email}'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'Failed to send test email: {result.get("message", "Unknown error")}'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
