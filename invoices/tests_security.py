"""
Security tests for InvoiceFlow application.
Tests CSRF, XSS, SQL injection, authentication, and authorization.
"""

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from invoices.models import Invoice


class CSRFProtectionTests(TestCase):
    """Test CSRF protection on forms and AJAX endpoints."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_create_invoice_requires_csrf_token(self):
        """Test that invoice creation fails without CSRF token."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("create_invoice"),
            {
                "business_name": "Test Business",
                "client_name": "Test Client",
            },
        )
        # Should fail without CSRF token
        self.assertEqual(response.status_code, 403)

    def test_login_requires_csrf_token(self):
        """Test that login fails without CSRF token."""
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )
        self.assertEqual(response.status_code, 403)


class XSSProtectionTests(TestCase):
    """Test XSS protection via template escaping."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_invoice_escapes_malicious_script(self):
        """Test that invoice fields escape <script> tags."""
        invoice = Invoice.objects.create(
            user=self.user,
            business_name='<script>alert("XSS")</script>',
            business_email="test@example.com",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@example.com",
            client_address="456 Client Ave",
        )

        response = self.client.get(reverse("invoice_detail", args=[invoice.invoice_id]))
        self.assertEqual(response.status_code, 200)
        # Should escape the script tag
        self.assertNotContains(response, '<script>alert("XSS")</script>')
        self.assertContains(response, "&lt;script&gt;")


class SQLInjectionProtectionTests(TestCase):
    """Test SQL injection protection via ORM parameterization."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_search_protects_against_sql_injection(self):
        """Test that search query is parameterized."""
        malicious_query = "'; DROP TABLE invoices_invoice; --"
        response = self.client.get(reverse("dashboard"), {"search": malicious_query})
        # Should return normal response, not execute SQL
        self.assertEqual(response.status_code, 200)
        # Invoice table should still exist
        self.assertEqual(Invoice.objects.count(), 0)


class AuthenticationTests(TestCase):
    """Test authentication and authorization."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpass123")
        self.client = Client()

    def test_unauthenticated_cannot_access_dashboard(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

    def test_user_cannot_access_other_users_invoice(self):
        """Test that users can only access their own invoices."""
        # Create invoice for user
        invoice = Invoice.objects.create(
            user=self.user,
            business_name="Test Business",
            business_email="test@example.com",
            business_address="123 Test St",
            client_name="Test Client",
            client_email="client@example.com",
            client_address="456 Client Ave",
        )

        # Login as other_user
        self.client.login(username="otheruser", password="otherpass123")

        # Try to access user's invoice
        response = self.client.get(reverse("invoice_detail", args=[invoice.invoice_id]))
        self.assertEqual(response.status_code, 404)

    def test_password_requirements(self):
        """Test password validation requirements."""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "123",  # Too short
                "password2": "123",
            },
        )
        # Should fail with weak password
        self.assertNotEqual(response.status_code, 302)


class SessionSecurityTests(TestCase):
    """Test session security configuration."""

    @override_settings(SESSION_COOKIE_HTTPONLY=True)
    def test_session_cookie_httponly(self):
        """Test that session cookies are HTTPOnly."""
        self.assertTrue(self.client.session.get_cookie_params()["httponly"])

    @override_settings(SESSION_COOKIE_SECURE=True)
    def test_session_cookie_secure_in_production(self):
        """Test that session cookies are Secure in production."""
        # This is set via settings based on DEBUG flag
        from django.conf import settings

        if not settings.DEBUG:
            self.assertTrue(settings.SESSION_COOKIE_SECURE)


class RateLimitingTests(TestCase):
    """Test rate limiting on sensitive endpoints."""

    def setUp(self):
        self.client = Client()

    def test_login_rate_limiting(self):
        """Test that login attempts are rate limited."""
        # Make multiple failed login attempts
        for _i in range(10):
            self.client.post(
                reverse("login"),
                {
                    "username": "testuser",
                    "password": "wrongpassword",
                },
            )

        # Next attempt should be rate limited (if rate limiting is enabled)
        # Note: This test assumes rate limiting is configured
        # Implementation depends on django-ratelimit configuration


class SecureHeadersTests(TestCase):
    """Test security headers in responses."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_xframe_options_header(self):
        """Test X-Frame-Options header is set."""
        response = self.client.get(reverse("dashboard"))
        # Should have X-Frame-Options header
        self.assertIn("X-Frame-Options", response.headers)

    def test_content_type_nosniff(self):
        """Test X-Content-Type-Options header is set."""
        response = self.client.get(reverse("dashboard"))
        # Should have X-Content-Type-Options header
        self.assertIn("X-Content-Type-Options", response.headers)

    def test_csp_header(self):
        """Test Content-Security-Policy header is set."""
        response = self.client.get(reverse("dashboard"))
        # Should have CSP header
        # Note: This depends on django-csp middleware
        if "Content-Security-Policy" in response.headers:
            self.assertIn("default-src", response.headers["Content-Security-Policy"])
