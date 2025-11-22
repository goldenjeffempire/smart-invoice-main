from django.core.management.base import BaseCommand
from invoices.email_utils import EmailConfig


class Command(BaseCommand):
    help = "Send a test email to verify SMTP configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Recipient email address for test'
        )

    def handle(self, *args, **options):
        email = options['email']
        success, message = EmailConfig.send_test_email(email)
        
        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))
