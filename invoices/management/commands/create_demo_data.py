"""Management command to create demo data for testing."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from invoices.models import Invoice, UserProfile
from decimal import Decimal
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Create demo data for Smart Invoice testing"

    def handle(self, *args, **options):
        # Create demo user
        user, created = User.objects.get_or_create(
            username="demo_user",
            defaults={"email": "demo@smartinvoice.com", "first_name": "Demo", "last_name": "User"},
        )

        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user"))

        # Create profile
        UserProfile.objects.get_or_create(
            user=user, defaults={"company_name": "Demo Company", "default_currency": "USD"}
        )

        # Create sample invoices
        for i in range(5):
            Invoice.objects.get_or_create(
                user=user,
                invoice_id=f"INV-DEMO-{i+1:03d}",
                defaults={
                    "business_name": "Smart Solutions LLC",
                    "business_email": "hello@smartinvoice.com",
                    "business_phone": "+1 (555) 123-4567",
                    "business_address": "123 Business St, City, State 12345",
                    "client_name": f"Client {i+1}",
                    "client_email": f"client{i+1}@example.com",
                    "client_address": f"{i+1}00 Customer Ave, City, State 12345",
                    "invoice_date": date.today() - timedelta(days=i * 10),
                    "due_date": date.today() + timedelta(days=30),
                    "total": Decimal("1000.00") * (i + 1),
                    "status": "paid" if i % 2 == 0 else "unpaid",
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully"))
