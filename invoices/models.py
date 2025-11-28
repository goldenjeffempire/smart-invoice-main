from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
from datetime import timedelta


class Waitlist(models.Model):
    """Email waitlist for upcoming features (Templates, API, etc)."""

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

    def __str__(self):
        return f"{self.email} - {self.get_feature_display()}"


class UserProfile(models.Model):
    """Extended user profile with business preferences and settings."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
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

    def __str__(self):
        return f"{self.user.username}'s Profile"


class InvoiceTemplate(models.Model):
    """Reusable invoice templates for quick invoice creation."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoice_templates")
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

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class RecurringInvoice(models.Model):
    """Recurring invoice configuration for automated invoicing."""

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recurring_invoices")
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

    def __str__(self):
        return f"Recurring - {self.client_name} ({self.frequency})"

    def generate_next_invoice_date(self):
        """Calculate next invoice generation date based on frequency."""
        from dateutil.relativedelta import relativedelta

        if self.frequency == "weekly":
            return self.next_generation + timedelta(weeks=1)
        elif self.frequency == "biweekly":
            return self.next_generation + timedelta(weeks=2)
        elif self.frequency == "monthly":
            return self.next_generation + relativedelta(months=1)
        elif self.frequency == "quarterly":
            return self.next_generation + relativedelta(months=3)
        elif self.frequency == "yearly":
            return self.next_generation + relativedelta(years=1)
        return self.next_generation


class Invoice(models.Model):
    """Invoice model for storing invoice data and metadata."""

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
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

    def save(self, *args, **kwargs):
        """Override save to auto-generate invoice_id if not set."""
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        super().save(*args, **kwargs)

    def generate_invoice_id(self):
        """Generate a unique invoice ID with prefix and random hex suffix."""
        prefix = "INV"
        random_part = secrets.token_hex(3).upper()
        invoice_id = f"{prefix}{random_part}"

        while Invoice.objects.filter(invoice_id=invoice_id).exists():
            random_part = secrets.token_hex(3).upper()
            invoice_id = f"{prefix}{random_part}"

        return invoice_id

    @property
    def subtotal(self):
        """Calculate subtotal from all line items."""
        return sum((item.total for item in self.line_items.all()), Decimal("0"))

    @property
    def tax_amount(self):
        """Calculate tax amount based on subtotal and tax rate."""
        return (self.subtotal * self.tax_rate) / Decimal("100")

    @property
    def total(self):
        """Calculate total amount including tax."""
        return self.subtotal + self.tax_amount

    def __str__(self):
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

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        """Calculate total for this line item."""
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_id}"
