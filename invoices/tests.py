"""Unit tests for the InvoiceFlow application."""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Invoice, LineItem, UserProfile


class InvoiceModelTest(TestCase):
    """Test cases for the Invoice model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_address="123 Test Street",
            client_name="Test Client",
            client_email="client@test.com",
            client_address="456 Client Avenue",
            currency="USD",
            tax_rate=Decimal("10.00"),
        )

    def test_invoice_creation(self):
        """Test that an invoice is created correctly."""
        self.assertIsNotNone(self.invoice.invoice_id)
        self.assertTrue(self.invoice.invoice_id.startswith("INV"))
        self.assertEqual(self.invoice.status, "unpaid")
        self.assertEqual(self.invoice.currency, "USD")

    def test_invoice_id_generation(self):
        """Test that invoice IDs are unique."""
        invoice2 = Invoice.objects.create(
            user=self.user,
            business_name="Test Business 2",
            business_email="business2@test.com",
            business_address="789 Test Boulevard",
            client_name="Test Client 2",
            client_email="client2@test.com",
            client_address="101 Client Drive",
        )
        self.assertNotEqual(self.invoice.invoice_id, invoice2.invoice_id)

    def test_invoice_str_representation(self):
        """Test the string representation of an invoice."""
        expected_str = f"{self.invoice.invoice_id} - {self.invoice.client_name}"
        self.assertEqual(str(self.invoice), expected_str)


class LineItemModelTest(TestCase):
    """Test cases for the LineItem model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_address="123 Test Street",
            client_name="Test Client",
            client_email="client@test.com",
            client_address="456 Client Avenue",
        )
        self.line_item = LineItem.objects.create(
            invoice=self.invoice,
            description="Test Service",
            quantity=Decimal("2"),
            unit_price=Decimal("100.00"),
        )

    def test_line_item_total(self):
        """Test line item total calculation."""
        expected_total = Decimal("2") * Decimal("100.00")
        self.assertEqual(self.line_item.total, expected_total)

    def test_line_item_str_representation(self):
        """Test the string representation of a line item."""
        expected_str = f"{self.line_item.description} - {self.invoice.invoice_id}"
        self.assertEqual(str(self.line_item), expected_str)


class InvoiceCalculationsTest(TestCase):
    """Test cases for invoice calculations."""

    def setUp(self):
        """Set up test data with line items."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="business@test.com",
            business_address="123 Test Street",
            client_name="Test Client",
            client_email="client@test.com",
            client_address="456 Client Avenue",
            tax_rate=Decimal("10.00"),
        )
        LineItem.objects.create(
            invoice=self.invoice,
            description="Service 1",
            quantity=Decimal("1"),
            unit_price=Decimal("100.00"),
        )
        LineItem.objects.create(
            invoice=self.invoice,
            description="Service 2",
            quantity=Decimal("2"),
            unit_price=Decimal("50.00"),
        )

    def test_invoice_subtotal(self):
        """Test invoice subtotal calculation."""
        expected_subtotal = Decimal("100.00") + (Decimal("2") * Decimal("50.00"))
        self.assertEqual(self.invoice.subtotal, expected_subtotal)

    def test_invoice_tax_amount(self):
        """Test invoice tax amount calculation."""
        subtotal = Decimal("200.00")
        expected_tax = (subtotal * Decimal("10.00")) / Decimal("100")
        self.assertEqual(self.invoice.tax_amount, expected_tax)

    def test_invoice_total(self):
        """Test invoice total calculation."""
        expected_total = Decimal("200.00") + Decimal("20.00")
        self.assertEqual(self.invoice.total, expected_total)


class UserProfileModelTest(TestCase):
    """Test cases for the UserProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            company_name="Test Company",
            default_currency="USD",
            invoice_prefix="TST",
        )

    def test_profile_creation(self):
        """Test that a user profile is created correctly."""
        self.assertEqual(self.profile.company_name, "Test Company")
        self.assertEqual(self.profile.default_currency, "USD")
        self.assertEqual(self.profile.invoice_prefix, "TST")

    def test_profile_str_representation(self):
        """Test the string representation of a user profile."""
        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.profile), expected_str)


class HomeViewTest(TestCase):
    """Test cases for the home view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_home_page_status_code(self):
        """Test that the home page returns a 200 status code."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        """Test that the home page uses the correct template."""
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")


class AuthenticationViewsTest(TestCase):
    """Test cases for authentication views."""

    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_login_page_status_code(self):
        """Test that the login page returns a 200 status code."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        """Test failed login with wrong password."""
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)


class DashboardViewTest(TestCase):
    """Test cases for the dashboard view."""

    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_dashboard_requires_login(self):
        """Test that the dashboard requires authentication."""
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_when_logged_in(self):
        """Test that the dashboard is accessible when logged in."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
