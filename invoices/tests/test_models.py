import pytest
from django.contrib.auth.models import User
from invoices.models import Invoice, UserProfile, InvoiceTemplate, RecurringInvoice, LineItem
from datetime import date


@pytest.mark.django_db
class TestInvoiceModel:
    def test_invoice_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        invoice = Invoice.objects.create(
            user=user,
            business_name='Test Business',
            business_email='test@business.com',
            client_name='Test Client',
            client_email='client@test.com',
            currency='USD',
        )
        assert invoice.invoice_id.startswith('INV')
        assert invoice.status == 'unpaid'

    def test_invoice_total_calculation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        invoice = Invoice.objects.create(
            user=user,
            business_name='Test Business',
            business_email='test@business.com',
            client_name='Test Client',
            client_email='client@test.com',
            currency='USD',
            tax_rate=10,
        )
        LineItem.objects.create(invoice=invoice, description='Item 1', quantity=2, unit_price=50)
        
        assert invoice.subtotal == 100
        assert invoice.tax_amount == 10
        assert invoice.total == 110


@pytest.mark.django_db
class TestUserProfile:
    def test_profile_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        profile = UserProfile.objects.create(
            user=user,
            company_name='Test Company',
            default_currency='USD'
        )
        assert profile.company_name == 'Test Company'
        assert profile.user.username == 'testuser'


@pytest.mark.django_db
class TestInvoiceTemplate:
    def test_template_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        template = InvoiceTemplate.objects.create(
            user=user,
            name='Standard Template',
            business_name='Test Business',
            business_email='test@business.com',
            currency='USD'
        )
        assert template.name == 'Standard Template'
        assert template.is_default == False


@pytest.mark.django_db
class TestRecurringInvoice:
    def test_recurring_invoice_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        recurring = RecurringInvoice.objects.create(
            user=user,
            client_name='Recurring Client',
            client_email='recurring@test.com',
            client_address='123 Test St',
            business_name='Test Business',
            business_email='test@business.com',
            frequency='monthly',
            start_date=date.today(),
            next_generation=date.today(),
            currency='USD'
        )
        assert recurring.status == 'active'
        assert recurring.frequency == 'monthly'
