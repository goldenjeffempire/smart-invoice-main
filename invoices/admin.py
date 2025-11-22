from django.contrib import admin
from .models import Invoice, LineItem, UserProfile, InvoiceTemplate, RecurringInvoice


class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_id",
        "client_name",
        "business_name",
        "status",
        "total",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = ("invoice_id", "client_name", "business_name", "client_email")
    readonly_fields = ("invoice_id", "created_at", "updated_at")
    inlines = [LineItemInline]

    fieldsets = (
        (
            "Invoice Information",
            {"fields": ("invoice_id", "user", "status", "currency", "tax_rate")},
        ),
        (
            "Business Details",
            {"fields": ("business_name", "business_email", "business_phone", "business_address")},
        ),
        (
            "Client Details",
            {"fields": ("client_name", "client_email", "client_phone", "client_address")},
        ),
        ("Dates", {"fields": ("invoice_date", "due_date")}),
        ("Branding", {"fields": ("brand_name", "brand_color", "logo")}),
        ("Bank Details", {"fields": ("bank_name", "account_name", "account_number")}),
        ("Additional", {"fields": ("notes", "created_at", "updated_at")}),
    )


@admin.register(LineItem)
class LineItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "description", "quantity", "unit_price", "total")
    search_fields = ("description", "invoice__invoice_id")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "default_currency", "created_at")
    search_fields = ("user__username", "company_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "business_name", "currency", "is_default")
    list_filter = ("currency", "is_default", "created_at")
    search_fields = ("name", "business_name", "user__username")
    readonly_fields = ("created_at",)


@admin.register(RecurringInvoice)
class RecurringInvoiceAdmin(admin.ModelAdmin):
    list_display = ("client_name", "user", "frequency", "status", "next_generation")
    list_filter = ("frequency", "status", "created_at")
    search_fields = ("client_name", "user__username", "client_email")
    readonly_fields = ("created_at", "last_generated")
    fieldsets = (
        ("Client Information", {"fields": ("user", "client_name", "client_email", "client_phone", "client_address")}),
        ("Business Information", {"fields": ("business_name", "business_email", "currency", "tax_rate")}),
        ("Schedule", {"fields": ("frequency", "start_date", "end_date", "next_generation", "status")}),
        ("Metadata", {"fields": ("notes", "created_at", "last_generated")}),
    )
