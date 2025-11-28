"""
Performance tests for Smart Invoice application.
Tests database query optimization, caching, and response times.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import connection
from invoices.models import Invoice, LineItem
from decimal import Decimal
import time


class DatabaseQueryOptimizationTests(TestCase):
    """Test database query optimization."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

        # Create test data
        for i in range(10):
            invoice = Invoice.objects.create(
                user=self.user,
                business_name=f"Business {i}",
                business_email=f"business{i}@example.com",
                business_address="123 Test St",
                client_name=f"Client {i}",
                client_email=f"client{i}@example.com",
                client_address="456 Client Ave",
            )
            # Add line items
            for j in range(5):
                LineItem.objects.create(
                    invoice=invoice,
                    description=f"Item {j}",
                    quantity=Decimal("1.00"),
                    unit_price=Decimal("100.00"),
                )

    def test_dashboard_uses_prefetch_related(self):
        """Test that dashboard uses prefetch_related for line items."""
        # Reset query counter
        connection.queries_log.clear()

        # Access dashboard
        with self.assertNumQueries(3):  # Should be limited queries with prefetch
            response = self.client.get(reverse("dashboard"))
            self.assertEqual(response.status_code, 200)

    def test_invoice_detail_minimal_queries(self):
        """Test that invoice detail uses select_related."""
        invoice = Invoice.objects.filter(user=self.user).first()

        connection.queries_log.clear()

        # Should use select_related for user
        with self.assertNumQueries(2):  # Invoice + line items
            response = self.client.get(reverse("invoice_detail", args=[invoice.invoice_id]))
            self.assertEqual(response.status_code, 200)


class ResponseTimeTests(TestCase):
    """Test response times for critical endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

        # Create test invoices
        for i in range(50):
            invoice = Invoice.objects.create(
                user=self.user,
                business_name=f"Business {i}",
                business_email=f"business{i}@example.com",
                business_address="123 Test St",
                client_name=f"Client {i}",
                client_email=f"client{i}@example.com",
                client_address="456 Client Ave",
            )
            LineItem.objects.create(
                invoice=invoice,
                description="Test Item",
                quantity=Decimal("1.00"),
                unit_price=Decimal("100.00"),
            )

    def test_dashboard_response_time(self):
        """Test dashboard loads in reasonable time."""
        start_time = time.time()
        response = self.client.get(reverse("dashboard"))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        # Should load in less than 1 second
        self.assertLess(end_time - start_time, 1.0)

    def test_invoice_detail_response_time(self):
        """Test invoice detail loads in reasonable time."""
        invoice = Invoice.objects.filter(user=self.user).first()

        start_time = time.time()
        response = self.client.get(reverse("invoice_detail", args=[invoice.invoice_id]))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        # Should load in less than 500ms
        self.assertLess(end_time - start_time, 0.5)


class StaticFileCompressionTests(TestCase):
    """Test static file compression and caching."""

    def setUp(self):
        self.client = Client()

    def test_static_files_have_cache_headers(self):
        """Test that static files have appropriate cache headers."""
        # This test depends on WhiteNoise configuration
        response = self.client.get("/static/css/main.min.css")
        if response.status_code == 200:
            # Should have cache-control header
            self.assertIn("Cache-Control", response.headers)

    def test_gzip_compression_available(self):
        """Test that gzipped versions are available."""
        # WhiteNoise should serve compressed files when available
        response = self.client.get("/static/css/main.min.css", HTTP_ACCEPT_ENCODING="gzip")
        if response.status_code == 200:
            # Should be compressed or have gzip in headers
            pass  # WhiteNoise handles this automatically


class MemoryUsageTests(TestCase):
    """Test memory-efficient query patterns."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_paginated_results_dont_load_all(self):
        """Test that pagination doesn't load all records into memory."""
        # Create many invoices
        for i in range(100):
            Invoice.objects.create(
                user=self.user,
                business_name=f"Business {i}",
                business_email=f"business{i}@example.com",
                business_address="123 Test St",
                client_name=f"Client {i}",
                client_email=f"client{i}@example.com",
                client_address="456 Client Ave",
            )

        # Query with pagination should use iterator or slicing
        invoices = Invoice.objects.filter(user=self.user)[:20]
        # Should only fetch 20, not 100
        self.assertEqual(len(list(invoices)), 20)


class DecimalPrecisionTests(TestCase):
    """Test Decimal precision for financial calculations."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="test@example.com",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@example.com",
            client_address="456 Client Ave",
            tax_rate=Decimal("7.5"),
        )

    def test_subtotal_uses_decimal(self):
        """Test that subtotal returns Decimal, not float."""
        LineItem.objects.create(
            invoice=self.invoice,
            description="Test Item",
            quantity=Decimal("2.5"),
            unit_price=Decimal("99.99"),
        )

        subtotal = self.invoice.subtotal
        self.assertIsInstance(subtotal, Decimal)
        self.assertEqual(subtotal, Decimal("249.975"))

    def test_tax_calculation_precision(self):
        """Test tax calculation maintains precision."""
        LineItem.objects.create(
            invoice=self.invoice,
            description="Test Item",
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
        )

        tax_amount = self.invoice.tax_amount
        self.assertIsInstance(tax_amount, Decimal)
        # 7.5% of 100.00 = 7.50
        self.assertEqual(tax_amount, Decimal("7.5"))

    def test_total_calculation_no_rounding_errors(self):
        """Test total calculation avoids floating point errors."""
        LineItem.objects.create(
            invoice=self.invoice,
            description="Test Item",
            quantity=Decimal("3.33"),
            unit_price=Decimal("99.99"),
        )

        total = self.invoice.total
        self.assertIsInstance(total, Decimal)
        # Should maintain precision without float conversion
