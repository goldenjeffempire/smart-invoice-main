from __future__ import annotations

from decimal import Decimal
from datetime import date, timedelta
from typing import Any, TYPE_CHECKING

from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class Waitlist(models.Model):
    """Email waitlist for upcoming features (Templates, API, etc)."""

    objects: "models.Manager[Waitlist]"

    FEATURE_CHOICES = [
        ("templates", "Invoice Templates"),
        ("api", "API Access"),
        ("general", "General Updates"),
    ]

    email = models.EmailField(unique=True)
    feature = models.CharField(max_length=20, choices=FEATURE_CHOICES, default="general")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name_plural = "Waitlist entries"

    def __str__(self) -> str:
        return f"{self.email} - {self.get_feature_display()}"


class ContactSubmission(models.Model):
    """Store contact form submissions for follow-up and audit."""

    objects: "models.Manager[ContactSubmission]"

    SUBJECT_CHOICES = [
        ("sales", "Sales Inquiry"),
        ("support", "Technical Support"),
        ("billing", "Billing Question"),
        ("feature", "Feature Request"),
        ("bug", "Bug Report"),
        ("general", "General Inquiry"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default="general")
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name_plural = "Contact submissions"

    def __str__(self) -> str:
        return f"{self.name} - {self.get_subject_display()} ({self.status})"


class UserProfile(models.Model):
    """Extended user profile with business preferences and settings."""

    objects: "models.Manager[UserProfile]"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    company_name = models.CharField(max_length=200, blank=True)
    company_logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    business_email = models.EmailField(blank=True)
    business_phone = models.CharField(max_length=50, blank=True)
    business_address = models.TextField(blank=True)
    default_currency = models.CharField(
        max_length=3,
        choices=[
            ("USD", "US Dollar"),
            ("EUR", "Euro"),
            ("GBP", "British Pound"),
            ("NGN", "Nigerian Naira"),
            ("CAD", "Canadian Dollar"),
            ("AUD", "Australian Dollar"),
        ],
        default="USD",
    )
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    invoice_prefix = models.CharField(max_length=10, default="INV")
    timezone = models.CharField(max_length=63, default="UTC")

    notify_invoice_created = models.BooleanField(default=True)
    notify_payment_received = models.BooleanField(default=True)
    notify_invoice_viewed = models.BooleanField(default=True)
    notify_invoice_overdue = models.BooleanField(default=True)
    notify_weekly_summary = models.BooleanField(default=False)
    notify_security_alerts = models.BooleanField(default=True)
    notify_password_changes = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"


class InvoiceTemplate(models.Model):
    """Reusable invoice templates for quick invoice creation."""

    objects: "models.Manager[InvoiceTemplate]"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoice_templates"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    business_name = models.CharField(max_length=200)
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=50, blank=True)
    business_address = models.TextField()
    currency = models.CharField(max_length=3, default="USD")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bank_name = models.CharField(max_length=200, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.user.username}"


class RecurringInvoice(models.Model):
    """Recurring invoice configuration for automated invoicing."""

    objects: "models.Manager[RecurringInvoice]"

    FREQUENCY_CHOICES = [
        ("weekly", "Weekly"),
        ("biweekly", "Bi-weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("ended", "Ended"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurring_invoices"
    )
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=50, blank=True)
    client_address = models.TextField()

    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="monthly")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    business_name = models.CharField(max_length=200)
    business_email = models.EmailField()
    currency = models.CharField(max_length=3, default="USD")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    last_generated = models.DateTimeField(null=True, blank=True)
    next_generation = models.DateField()

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Recurring - {self.client_name} ({self.frequency})"

    def generate_next_invoice_date(self) -> date:
        """Calculate next invoice generation date based on frequency."""
        from dateutil.relativedelta import relativedelta

        current_date: date = self.next_generation
        if self.frequency == "weekly":
            return current_date + timedelta(weeks=1)
        elif self.frequency == "biweekly":
            return current_date + timedelta(weeks=2)
        elif self.frequency == "monthly":
            return current_date + relativedelta(months=1)
        elif self.frequency == "quarterly":
            return current_date + relativedelta(months=3)
        elif self.frequency == "yearly":
            return current_date + relativedelta(years=1)
        return current_date


class Invoice(models.Model):
    """Invoice model for storing invoice data and metadata."""

    objects: "models.Manager[Invoice]"

    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("GBP", "British Pound"),
        ("NGN", "Nigerian Naira"),
        ("CAD", "Canadian Dollar"),
        ("AUD", "Australian Dollar"),
    ]

    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices"
    )
    invoice_id = models.CharField(max_length=20, unique=True, editable=False)
    recurring_invoice = models.ForeignKey(
        RecurringInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_invoices",
    )
    template = models.ForeignKey(
        InvoiceTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    business_name = models.CharField(max_length=200)
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=50, blank=True)
    business_address = models.TextField()

    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=50, blank=True)
    client_address = models.TextField()

    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    brand_name = models.CharField(max_length=100, blank=True)
    brand_color = models.CharField(max_length=7, default="#6366f1")
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)

    bank_name = models.CharField(max_length=200, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unpaid")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to auto-generate invoice_id if not set."""
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        super().save(*args, **kwargs)

    def generate_invoice_id(self) -> str:
        """Generate a unique invoice ID with prefix and random hex suffix."""
        prefix = "INV"
        random_part = secrets.token_hex(3).upper()
        invoice_id = f"{prefix}{random_part}"

        while Invoice.objects.filter(invoice_id=invoice_id).exists():
            random_part = secrets.token_hex(3).upper()
            invoice_id = f"{prefix}{random_part}"

        return invoice_id

    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal from all line items."""
        return sum((item.total for item in self.line_items.all()), Decimal("0"))

    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount based on subtotal and tax rate."""
        tax_rate_decimal = Decimal(str(self.tax_rate))
        return (self.subtotal * tax_rate_decimal) / Decimal("100")

    @property
    def total(self) -> Decimal:
        """Calculate total amount including tax."""
        return self.subtotal + self.tax_amount

    def __str__(self) -> str:
        return f"{self.invoice_id} - {self.client_name}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="idx_user_status"),
            models.Index(fields=["user", "-created_at"], name="idx_user_created"),
            models.Index(fields=["user", "invoice_date"], name="idx_user_date"),
            models.Index(fields=["invoice_id"], name="idx_invoice_id"),
            models.Index(fields=["user", "client_email"], name="idx_user_client"),
        ]


class LineItem(models.Model):
    """Line item model for invoice line items."""

    objects: "models.Manager[LineItem]"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self) -> Decimal:
        """Calculate total for this line item."""
        return Decimal(str(self.quantity)) * Decimal(str(self.unit_price))

    def __str__(self) -> str:
        return f"{self.description} - {self.invoice.invoice_id}"


class MFAProfile(models.Model):
    """Multi-Factor Authentication profile for enhanced security."""

    objects: "models.Manager[MFAProfile]"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mfa_profile"
    )
    is_enabled = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=64, blank=True)
    recovery_codes = models.JSONField(default=list, blank=True)
    backup_phone = models.CharField(max_length=20, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MFA Profile"
        verbose_name_plural = "MFA Profiles"

    def __str__(self) -> str:
        status = "enabled" if self.is_enabled else "disabled"
        return f"{self.user.username}'s MFA ({status})"

    @property
    def recovery_codes_remaining(self) -> int:
        """Return count of remaining recovery codes."""
        return len(self.recovery_codes) if self.recovery_codes else 0


class LoginAttempt(models.Model):
    """Track login attempts for security and rate limiting."""

    objects: "models.Manager[LoginAttempt]"

    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["username", "created_at"], name="idx_login_user_time"),
            models.Index(fields=["ip_address", "created_at"], name="idx_login_ip_time"),
        ]

    def __str__(self) -> str:
        status = "success" if self.success else "failed"
        return f"{self.username} - {self.ip_address} ({status})"
