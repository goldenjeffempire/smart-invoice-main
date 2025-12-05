from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from datetime import datetime
import calendar
import json
import urllib.parse
from decimal import Decimal

from .models import Invoice, UserProfile, InvoiceTemplate, RecurringInvoice, LineItem
from .forms import (
    SignUpForm,
    InvoiceForm,
    UserProfileForm,
    InvoiceTemplateForm,
    RecurringInvoiceForm,
)
from .search_filters import InvoiceExport


def get_client_ip(request):
    """Extract client IP address from request headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "unknown")
    return ip


def home(request):
    """Render the public landing page."""
    return render(request, "pages/home.html")


def signup(request):
    """Handle user registration with form validation and auto-login."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "auth/signup.html", {"form": form})


def login_view(request):
    """Authenticate user credentials and establish session with rate limiting and MFA support."""
    from django.core.cache import cache
    from django.conf import settings
    from .middleware import RequestResponseLoggingMiddleware
    from .models import LoginAttempt, MFAProfile

    if request.method == "POST":
        client_ip = RequestResponseLoggingMiddleware.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        username = request.POST.get("username", "")
        password = request.POST.get("password")

        lockout_threshold = getattr(settings, 'ACCOUNT_LOCKOUT_THRESHOLD', 5)
        lockout_duration = getattr(settings, 'ACCOUNT_LOCKOUT_DURATION', 900)

        ip_cache_key = f"login_attempt:ip:{client_ip}"
        user_cache_key = f"login_attempt:user:{username.lower()}" if username else None

        ip_attempts = cache.get(ip_cache_key, 0)
        user_attempts = cache.get(user_cache_key, 0) if user_cache_key else 0

        if ip_attempts >= lockout_threshold:
            messages.error(request, "Too many login attempts from this location. Please try again in 15 minutes.")
            return render(request, "auth/login.html")

        if user_attempts >= lockout_threshold:
            messages.error(request, "This account is temporarily locked due to too many failed attempts. Please try again in 15 minutes.")
            return render(request, "auth/login.html")

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            cache.delete(ip_cache_key)
            if user_cache_key:
                cache.delete(user_cache_key)
            
            LoginAttempt.objects.create(
                username=username,
                ip_address=client_ip,
                user_agent=user_agent,
                success=True
            )
            
            login(request, user)
            
            if getattr(settings, 'MFA_ENABLED', False):
                try:
                    mfa_profile = MFAProfile.objects.get(user=user)
                    if mfa_profile.is_enabled:
                        request.session['mfa_verified'] = False
                        return redirect("mfa_verify")
                except MFAProfile.DoesNotExist:
                    pass
            
            request.session['mfa_verified'] = True
            return redirect("dashboard")
        else:
            cache.set(ip_cache_key, ip_attempts + 1, lockout_duration)
            if user_cache_key:
                cache.set(user_cache_key, user_attempts + 1, lockout_duration)
            
            LoginAttempt.objects.create(
                username=username or "unknown",
                ip_address=client_ip,
                user_agent=user_agent,
                success=False,
                failure_reason="Invalid credentials"
            )
            
            messages.error(request, "Invalid username or password.")
    return render(request, "auth/login.html")


def logout_view(request):
    """End user session, clear MFA verification, and redirect to home page."""
    request.session.pop('mfa_verified', None)
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    """Display user dashboard with invoice statistics and filtered invoice list."""
    from invoices.services import AnalyticsService

    base_queryset = Invoice.objects.filter(user=request.user)  # type: ignore

    # Apply status filter at database level (not in Python)
    filter_status = request.GET.get("status", "all")
    if filter_status == "paid":
        invoices_queryset = base_queryset.filter(status="paid")
    elif filter_status == "unpaid":
        invoices_queryset = base_queryset.filter(status="unpaid")
    else:
        invoices_queryset = base_queryset

    # Fetch filtered invoices with prefetched line_items (efficient join)
    # Limit to recent 100 invoices for performance (pagination can be added later)
    invoices = list(invoices_queryset.prefetch_related("line_items").order_by("-created_at")[:100])

    # Use AnalyticsService for efficient stats calculation
    stats = AnalyticsService.get_user_dashboard_stats(request.user)

    context = {
        "invoices": invoices,
        "total_invoices": stats["total_invoices"],
        "paid_count": stats["paid_count"],
        "unpaid_count": stats["unpaid_count"],
        "total_revenue": stats["total_revenue"],
        "unique_clients": stats["unique_clients"],
        "filter_status": filter_status,
    }
    context["recent_invoices"] = invoices[:5]
    context["total_revenue"] = stats["total_revenue"]
    context["pending_invoices"] = stats["unpaid_count"]
    context["paid_invoices"] = stats["paid_count"]
    return render(request, "dashboard/main.html", context)


@login_required
def create_invoice(request):
    from invoices.services import InvoiceService

    if request.method == "POST":
        line_items_data = json.loads(request.POST.get("line_items", "[]"))

        if not line_items_data:
            messages.error(request, "Please add at least one line item.")
            return render(
                request,
                "invoices/create_invoice.html",
                {"invoice_form": InvoiceForm(request.POST, request.FILES)},
            )

        invoice, invoice_form = InvoiceService.create_invoice(
            user=request.user,
            invoice_data=request.POST,
            files_data=request.FILES,
            line_items_data=line_items_data,
        )

        if invoice:
            messages.success(request, f"Invoice {invoice.invoice_id} created successfully!")
            return redirect("invoice_detail", invoice_id=invoice.id)  # type: ignore[union-attr]
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, "invoices/create_invoice.html", {"invoice_form": invoice_form})

    return render(request, "invoices/create_invoice.html", {"invoice_form": InvoiceForm()})


@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(
        Invoice.objects.prefetch_related("line_items"), id=invoice_id, user=request.user
    )
    return render(request, "invoices/invoice_detail.html", {"invoice": invoice})


@login_required
def edit_invoice(request, invoice_id):
    from invoices.services import InvoiceService

    invoice = get_object_or_404(
        Invoice.objects.prefetch_related("line_items"), id=invoice_id, user=request.user
    )

    if request.method == "POST":
        line_items_data = json.loads(request.POST.get("line_items", "[]"))

        if not line_items_data:
            messages.error(request, "Please add at least one line item.")
            return render(
                request,
                "invoices/edit_invoice.html",
                {
                    "invoice_form": InvoiceForm(request.POST, request.FILES, instance=invoice),
                    "invoice": invoice,
                    "line_items_json": json.dumps([], default=str),
                },
            )

        updated_invoice, invoice_form = InvoiceService.update_invoice(
            invoice=invoice,
            invoice_data=request.POST,
            files_data=request.FILES,
            line_items_data=line_items_data,
        )

        if updated_invoice:
            messages.success(request, f"Invoice {updated_invoice.invoice_id} updated successfully!")
            return redirect("invoice_detail", invoice_id=updated_invoice.id)  # type: ignore[union-attr]
        else:
            messages.error(request, "Please correct the errors below.")
            line_items = list(invoice.line_items.values("description", "quantity", "unit_price"))
            return render(
                request,
                "invoices/edit_invoice.html",
                {
                    "invoice_form": invoice_form,
                    "invoice": invoice,
                    "line_items_json": json.dumps(line_items, default=str),
                },
            )

    line_items = list(invoice.line_items.values("description", "quantity", "unit_price"))

    return render(
        request,
        "invoices/edit_invoice.html",
        {
            "invoice_form": InvoiceForm(instance=invoice),
            "invoice": invoice,
            "line_items_json": json.dumps(line_items, default=str),
        },
    )


@login_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    if request.method == "POST":
        invoice.delete()
        messages.success(request, "Invoice deleted successfully!")
        return redirect("dashboard")
    return render(request, "invoices/delete_invoice.html", {"invoice": invoice})


@login_required
def update_invoice_status(request, invoice_id):
    if request.method == "POST":
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        new_status = request.POST.get("status")
        if new_status in ["paid", "unpaid"]:
            invoice.status = new_status
            invoice.save()
            messages.success(request, f"Invoice status updated to {new_status}!")
        return redirect("invoice_detail", invoice_id=invoice.id)
    return redirect("dashboard")


@login_required
def generate_pdf(request, invoice_id):
    from .services import PDFService

    invoice = get_object_or_404(
        Invoice.objects.prefetch_related("line_items"), id=invoice_id, user=request.user
    )

    pdf = PDFService.generate_pdf_bytes(invoice)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Invoice_{invoice.invoice_id}.pdf"'

    return response


@login_required
def send_invoice_email(request, invoice_id: int):
    from .email_service import EmailService

    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)

    if request.method == "POST":
        recipient_email = request.POST.get("email", invoice.client_email)

        EmailService.send_invoice_email_async(invoice.id, recipient_email)

        messages.success(
            request,
            f"Invoice #{invoice.invoice_id} is being sent to {recipient_email}. "
            "You'll be notified once delivered.",
        )
        return redirect("invoice_detail", invoice_id=invoice.id)

    return render(request, "invoices/send_email.html", {"invoice": invoice})


@login_required
def whatsapp_share(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)

    # Enhanced WhatsApp message with emojis and better formatting
    phone_line = f"📞 {invoice.business_phone}" if invoice.business_phone else ""
    due_line = f"⏰ Due: {invoice.due_date.strftime('%B %d, %Y')}" if invoice.due_date else ""

    payment_details = ""
    if invoice.bank_name:
        payment_details = f"\n\n🏦 *Payment Details:*\nBank: {invoice.bank_name}\nAccount: {invoice.account_name}\nAccount #: {invoice.account_number}"

    notes_line = ""
    if invoice.notes:
        notes_line = f"\n\n📝 Notes: {invoice.notes}"

    message = f"""📄 *Invoice #{invoice.invoice_id}*

👔 From: *{invoice.business_name}*
{invoice.business_email}
{phone_line}

👤 To: *{invoice.client_name}*

📅 Date: {invoice.invoice_date.strftime('%B %d, %Y')}
{due_line}

💰 *Total Amount: {invoice.currency} {invoice.total:.2f}*
Status: {invoice.get_status_display().upper()}{payment_details}{notes_line}

Thank you for your business! 🙏
- {invoice.business_name}
    """.strip()

    # Clean phone number for WhatsApp
    phone = (
        invoice.client_phone.replace("+", "")
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"

    return render(
        request,
        "invoices/whatsapp_share.html",
        {
            "invoice": invoice,
            "whatsapp_url": whatsapp_url,
            "message_preview": message,
        },
    )


# ============================================================================
# FOOTER PAGE VIEWS - Professional Public Pages
# ============================================================================


def features(request):
    """Features page showcasing platform capabilities."""
    return render(request, "pages/features.html")


def pricing(request):
    """Pricing page with subscription plans."""
    return render(request, "pages/pricing.html")


def templates_page(request):
    """Invoice templates coming soon page."""
    return render(request, "pages/templates.html")


def api_access(request):
    """API access coming soon page."""
    return render(request, "pages/api.html")


def about(request):
    """About Us page - company story and values."""
    return render(request, "pages/about.html")


def careers(request):
    """Careers page with open positions."""
    return render(request, "pages/careers.html")


def contact(request):
    """Contact page with contact form - handles form submission with rate limiting and CAPTCHA."""
    from django.core.mail import send_mail
    from django.core.cache import cache
    from django.conf import settings
    from .forms import ContactForm
    from .middleware import RequestResponseLoggingMiddleware
    import logging
    import requests

    logger = logging.getLogger(__name__)
    
    # Rate limiting for contact form (5 submissions per hour per IP)
    client_ip = get_client_ip(request)
    rate_limit_key = f"contact_form:{client_ip}"
    submission_count = cache.get(rate_limit_key, 0)

    if request.method == "POST":
        # Check rate limit
        if submission_count >= 5:
            messages.error(
                request,
                "Too many submissions. Please try again later.",
            )
            logger.warning(f"Contact form rate limit exceeded for IP: {client_ip}")
            return render(request, "pages/contact.html", {"form": ContactForm(), "rate_limited": True})
        
        form = ContactForm(request.POST)
        
        # Verify hCaptcha if enabled
        hcaptcha_valid = True
        if getattr(settings, 'HCAPTCHA_ENABLED', False):
            hcaptcha_response = request.POST.get('h-captcha-response', '')
            if not hcaptcha_response:
                hcaptcha_valid = False
                messages.error(request, "Please complete the CAPTCHA verification.")
            else:
                try:
                    verify_response = requests.post(
                        'https://api.hcaptcha.com/siteverify',
                        data={
                            'secret': settings.HCAPTCHA_SECRET,
                            'response': hcaptcha_response,
                            'remoteip': client_ip,
                        },
                        timeout=10
                    )
                    result = verify_response.json()
                    hcaptcha_valid = result.get('success', False)
                    if not hcaptcha_valid:
                        messages.error(request, "CAPTCHA verification failed. Please try again.")
                        logger.warning(f"hCaptcha verification failed for IP: {client_ip}")
                except Exception as e:
                    logger.error(f"hCaptcha verification error: {e}")
                    hcaptcha_valid = True  # Fail open to not block legitimate users
        
        if form.is_valid() and hcaptcha_valid:
            try:
                submission = form.save(commit=False)
                submission.ip_address = client_ip
                submission.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
                submission.save()

                full_message = f"""
New Contact Form Submission

From: {submission.name}
Email: {submission.email}
Subject: {submission.get_subject_display()}

Message:
{submission.message}

---
IP: {submission.ip_address}
Submitted: {submission.submitted_at}
"""
                send_mail(
                    subject=f"[InvoiceFlow Contact] {submission.get_subject_display()}",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=["support@invoiceflow.com.ng"],
                    fail_silently=True,
                )
                messages.success(
                    request,
                    "Thank you for your message! We'll get back to you within 24 hours.",
                )
                logger.info(f"Contact form submitted by {submission.email}")
                
                # Increment rate limit counter
                cache.set(rate_limit_key, submission_count + 1, 3600)  # 1 hour
                
                return redirect("contact")
            except Exception as e:
                logger.error(f"Contact form submission failed: {e}")
                messages.error(
                    request,
                    "Sorry, there was an issue submitting your message. Please try again.",
                )
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field != "__all__":
                            messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
                        else:
                            messages.error(request, error)
    else:
        form = ContactForm()

    return render(request, "pages/contact.html", {
        "form": form,
        "hcaptcha_enabled": getattr(settings, 'HCAPTCHA_ENABLED', False),
        "hcaptcha_sitekey": getattr(settings, 'HCAPTCHA_SITEKEY', ''),
    })


def changelog(request):
    """Changelog page with version history."""
    return render(request, "pages/changelog.html")


def system_status(request):
    """System status page showing service health."""
    return render(request, "pages/status.html")


def support(request):
    """Support/Help center page."""
    return render(request, "pages/support.html")


def faq(request):
    """FAQ page with common questions and answers."""
    return render(request, "pages/faq.html")


def terms(request):
    """Terms of Service page."""
    return render(request, "pages/terms.html")


def privacy(request):
    """Privacy Policy page."""
    return render(request, "pages/privacy.html")


def components_showcase(request):
    """Phase 1 Design System - Component showcase page."""
    return render(request, "components-showcase.html")


def newsletter_signup(request):
    """Handle newsletter signup form submissions."""
    from .models import Waitlist
    import logging

    logger = logging.getLogger(__name__)

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if email:
            try:
                waitlist_entry, created = Waitlist.objects.get_or_create(
                    email=email,
                    defaults={"feature": "general"}
                )
                if created:
                    messages.success(
                        request,
                        "Thanks for subscribing! You'll receive updates and tips soon.",
                    )
                    logger.info(f"Newsletter signup: {email}")
                else:
                    messages.info(
                        request,
                        "You're already subscribed! We'll keep you updated.",
                    )
            except Exception as e:
                logger.error(f"Newsletter signup failed: {e}")
                messages.error(
                    request,
                    "Something went wrong. Please try again later.",
                )
        else:
            messages.error(request, "Please enter a valid email address.")

    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer if referer else "home")


# ============================================================================
# SETTINGS PAGES
# ============================================================================


@login_required
def settings_view(request):
    """Redirect to profile settings page."""
    return redirect("settings_profile")


@login_required
def settings_profile(request):
    """Profile Information settings page."""
    from .forms import UserDetailsForm

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    message = None
    message_type = None

    if request.method == "POST":
        user_form = UserDetailsForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            message = "Profile information updated successfully!"
            message_type = "success"
        else:
            message = "Please fix the errors below."
            message_type = "error"
    else:
        user_form = UserDetailsForm(instance=request.user)

    context = {
        "user_form": user_form,
        "profile": profile,
        "message": message,
        "message_type": message_type,
        "active_tab": "profile",
    }

    return render(request, "pages/settings-profile.html", context)


@login_required
def settings_business(request):
    """Business Settings page."""
    from .forms import UserProfileForm

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    message = None
    message_type = None

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if profile_form.is_valid():
            profile_form.save()
            message = "Business settings updated successfully!"
            message_type = "success"
        else:
            message = "Please fix the errors below."
            message_type = "error"
    else:
        profile_form = UserProfileForm(instance=profile)

    context = {
        "profile_form": profile_form,
        "profile": profile,
        "message": message,
        "message_type": message_type,
        "active_tab": "business",
    }

    return render(request, "pages/settings-business.html", context)


@login_required
def settings_security(request):
    """Security & Password settings page with rate limiting on password changes."""
    from .forms import PasswordChangeForm
    from django.contrib.auth.hashers import check_password
    from django.contrib.auth import update_session_auth_hash
    from django.core.cache import cache
    from .middleware import RequestResponseLoggingMiddleware

    message = None
    message_type = None

    if request.method == "POST":
        client_ip = RequestResponseLoggingMiddleware.get_client_ip(request)
        cache_key = f"password_change_attempt:{client_ip}:{request.user.id}"
        attempt_count = cache.get(cache_key, 0)

        if attempt_count >= 5:
            message = "Too many password change attempts. Please try again in 1 hour."
            message_type = "error"
            password_form = PasswordChangeForm()
        else:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                current = password_form.cleaned_data.get("current_password")
                new = password_form.cleaned_data.get("new_password")

                if not check_password(current, request.user.password):
                    cache.set(cache_key, attempt_count + 1, 3600)
                    message = "Current password is incorrect."
                    message_type = "error"
                    password_form = PasswordChangeForm()
                else:
                    cache.delete(cache_key)
                    request.user.set_password(new)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    message = "Password updated successfully!"
                    message_type = "success"
                    password_form = PasswordChangeForm()
            else:
                message = "Please fix the errors below."
                message_type = "error"
    else:
        password_form = PasswordChangeForm()

    context = {
        "password_form": password_form,
        "message": message,
        "message_type": message_type,
        "active_tab": "security",
    }

    return render(request, "pages/settings-security.html", context)


@login_required
def settings_notifications(request):
    """Email Notifications settings page."""
    from .forms import NotificationPreferencesForm

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    message = None
    message_type = None

    if request.method == "POST":
        notification_form = NotificationPreferencesForm(request.POST, instance=profile)

        if notification_form.is_valid():
            notification_form.save()
            message = "Notification preferences updated successfully!"
            message_type = "success"
        else:
            message = "Please fix the errors below."
            message_type = "error"
    else:
        notification_form = NotificationPreferencesForm(instance=profile)

    context = {
        "notification_form": notification_form,
        "profile": profile,
        "message": message,
        "message_type": message_type,
        "active_tab": "notifications",
    }

    return render(request, "pages/settings-notifications.html", context)


@login_required
def settings_billing(request):
    """Billing & Account settings page with optimized database queries."""
    from django.db.models import Sum, F, DecimalField, Value
    from django.db.models.functions import Coalesce

    now = datetime.now()
    invoices = Invoice.objects.filter(user=request.user)

    stats = invoices.aggregate(
        invoice_count=Count('id', filter=Q(invoice_date__month=now.month, invoice_date__year=now.year)),
        paid_invoices=Count('id', filter=Q(status='paid')),
    )

    pending_amount = LineItem.objects.filter(
        invoice__user=request.user,
        invoice__status='unpaid'
    ).aggregate(
        total=Coalesce(
            Sum(F('quantity') * F('unit_price')),
            Value(Decimal('0')),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )['total'] or Decimal('0')

    context = {
        "active_tab": "billing",
        "invoice_count": stats['invoice_count'] or 0,
        "paid_invoices": stats['paid_invoices'] or 0,
        "pending_amount": f"${pending_amount:,.2f}" if pending_amount > 0 else "$0.00",
    }

    return render(request, "pages/settings-billing.html", context)


@login_required
def analytics(request):
    from invoices.services import AnalyticsService

    # Get optimized analytics stats
    stats = AnalyticsService.get_user_analytics_stats(request.user)
    top_clients = AnalyticsService.get_top_clients(request.user, limit=10)

    # Get monthly trend data
    invoices = Invoice.objects.filter(user=request.user)
    now = datetime.now()

    monthly_data_raw = (
        invoices.annotate(month=TruncMonth("invoice_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    data_by_month = {}
    for item in monthly_data_raw:
        if item["month"]:
            month_date = item["month"].date() if hasattr(item["month"], "date") else item["month"]
            key = (month_date.year, month_date.month)
            data_by_month[key] = item["count"]

    monthly_labels = []
    monthly_data = []

    for i in range(6, -1, -1):
        year = now.year
        month = now.month - i
        while month < 1:
            month += 12
            year -= 1

        month_name = calendar.month_name[month][:3] + " " + str(year)
        monthly_labels.append(month_name)

        count = data_by_month.get((year, month), 0)
        monthly_data.append(count)

    recent_invoices = invoices.prefetch_related("line_items").order_by("-created_at")[:10]

    context = {
        "total_invoices": stats["total_invoices"],
        "paid_invoices": stats["paid_invoices"],
        "unpaid_invoices": stats["unpaid_invoices"],
        "total_revenue": stats["total_revenue"],
        "outstanding_amount": stats["outstanding_amount"],
        "average_invoice": stats["average_invoice"],
        "payment_rate": stats["payment_rate"],
        "current_month_invoices": stats["current_month_invoices"],
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
        "top_clients": top_clients,
        "recent_invoices": recent_invoices,
    }

    return render(request, "invoices/analytics.html", context)


# Admin Views (Production-ready admin dashboard for platform management)
from functools import wraps

def staff_member_required(view_func):
    """Decorator requiring user to be logged in and have staff access (is_active and is_staff)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect("login")
        if not (request.user.is_active and request.user.is_staff):
            messages.error(request, "You do not have permission to access this page.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_member_required
def admin_dashboard(request):
    from django.contrib.auth.models import User

    total_users = User.objects.count()
    total_invoices = Invoice.objects.count()

    # Optimize query with prefetch_related to avoid N+1
    paid_invoices_qs = Invoice.objects.filter(status="paid").prefetch_related("line_items")  # type: ignore
    total_revenue = (
        sum(inv.total for inv in paid_invoices_qs) if paid_invoices_qs.exists() else Decimal("0")
    )
    paid_invoices = paid_invoices_qs.count()
    paid_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0

    context = {
        "total_users": total_users,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "paid_rate": paid_rate,
    }
    return render(request, "admin/dashboard.html", context)


@staff_member_required
def admin_users(request):
    return render(request, "admin/users.html")


@staff_member_required
def admin_content(request):
    return render(request, "admin/content.html")


@staff_member_required
def admin_settings(request):
    return render(request, "admin/settings.html")


@login_required
def profile(request):
    """User profile management view."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "invoices/profile.html", {"form": form, "profile": profile})


@login_required
def invoice_templates(request):
    """Manage invoice templates."""
    templates = InvoiceTemplate.objects.filter(user=request.user)  # type: ignore

    if request.method == "POST":
        form = InvoiceTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, "Template created successfully!")
            return redirect("invoice_templates")
    else:
        form = InvoiceTemplateForm()

    return render(request, "invoices/templates.html", {"templates": templates, "form": form})


@login_required
def delete_template(request, template_id):
    """Delete invoice template."""
    template = get_object_or_404(InvoiceTemplate, id=template_id, user=request.user)
    template.delete()
    messages.success(request, "Template deleted successfully!")
    return redirect("invoice_templates")


@login_required
def recurring_invoices(request):
    """Manage recurring invoices."""
    recurring = RecurringInvoice.objects.filter(user=request.user)  # type: ignore

    if request.method == "POST":
        form = RecurringInvoiceForm(request.POST)
        if form.is_valid():
            rec_invoice = form.save(commit=False)
            rec_invoice.user = request.user
            rec_invoice.save()
            messages.success(request, "Recurring invoice created successfully!")
            return redirect("recurring_invoices")
    else:
        form = RecurringInvoiceForm()

    return render(
        request, "invoices/recurring.html", {"recurring_invoices": recurring, "form": form}
    )


@login_required
def bulk_export(request):
    """Export multiple invoices at once."""
    invoice_ids = request.POST.getlist("invoice_ids")
    export_format = request.POST.get("format", "csv")

    if not invoice_ids:
        messages.error(request, "Please select at least one invoice.")
        return redirect("dashboard")

    invoices = Invoice.objects.filter(id__in=invoice_ids, user=request.user).prefetch_related("line_items")  # type: ignore

    if export_format == "csv":
        csv_data = InvoiceExport.export_to_csv(invoices)
        response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="invoices.csv"'
        return response
    elif export_format == "pdf":
        pdfs = InvoiceExport.bulk_export_pdfs(invoices)
        if not pdfs:
            messages.error(request, "No invoices could be exported.")
            return redirect("dashboard")
        if len(pdfs) == 1:
            response = HttpResponse(pdfs[0][1], content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{pdfs[0][0]}.pdf"'
            return response
        else:
            messages.info(request, f"Exported {len(pdfs)} invoices.")
            return redirect("dashboard")

    messages.error(request, "Invalid export format.")
    return redirect("dashboard")


@login_required
def bulk_delete(request):
    """Delete multiple invoices at once."""
    if request.method == "POST":
        invoice_ids = request.POST.getlist("invoice_ids")
        if invoice_ids:
            deleted_count, _ = Invoice.objects.filter(id__in=invoice_ids, user=request.user).delete()  # type: ignore
            messages.success(request, f"Deleted {deleted_count} invoice(s).")
        return redirect("dashboard")
    return redirect("dashboard")


def waitlist_subscribe(request):
    """Handle email capture from Coming Soon pages and landing page."""
    from .forms import WaitlistForm

    if request.method == "POST":
        form = WaitlistForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You're on the list! We'll notify you soon.")
            return redirect(request.META.get("HTTP_REFERER", "home"))
        else:
            if form.errors and "email" in form.errors and "already" in str(form.errors["email"][0]).lower():
                messages.info(request, "This email is already on our waitlist!")
            else:
                messages.error(request, "Please enter a valid email address.")
            return redirect(request.META.get("HTTP_REFERER", "home"))

    return redirect("home")


def custom_404(request, exception):
    """Custom 404 error handler."""
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    """Custom 500 error handler."""
    return render(request, "errors/500.html", status=500)


def robots_txt(request):
    """Dynamic robots.txt with proper sitemap URL."""
    scheme = request.scheme
    host = request.get_host()
    base_url = f"{scheme}://{host}"
    
    content = f"""User-agent: *
Allow: /
Allow: /features/
Allow: /pricing/
Allow: /about/
Allow: /contact/
Allow: /faq/
Allow: /terms/
Allow: /privacy/

Disallow: /admin/
Disallow: /settings/
Disallow: /api/
Disallow: /invoices/
Disallow: /profile/
Disallow: /recurring/
Disallow: /bulk/
Disallow: /my-templates/
Disallow: /health/
Disallow: /static/js/
Disallow: /static/css/

Sitemap: {base_url}/sitemap.xml

Crawl-delay: 1
"""
    return HttpResponse(content.encode("utf-8"), content_type="text/plain; charset=utf-8")
