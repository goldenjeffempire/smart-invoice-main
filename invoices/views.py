from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import datetime
import calendar
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
import json
import urllib.parse
from decimal import Decimal
import threading
import os

from .models import Invoice, LineItem, UserProfile, InvoiceTemplate, RecurringInvoice
from .forms import SignUpForm, InvoiceForm, UserProfileForm, InvoiceTemplateForm, RecurringInvoiceForm, InvoiceSearchForm
from .search_filters import InvoiceSearch, InvoiceExport
from .sendgrid_service import send_invoice_email_sendgrid


def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    # Fetch all user's invoices with line_items prefetched (single query with join)
    all_user_invoices = list(
        Invoice.objects.filter(user=request.user).prefetch_related('line_items')
    )
    
    # Filter in Python to reuse prefetched data
    filter_status = request.GET.get("status", "all")
    if filter_status == "paid":
        invoices = [inv for inv in all_user_invoices if inv.status == "paid"]
    elif filter_status == "unpaid":
        invoices = [inv for inv in all_user_invoices if inv.status == "unpaid"]
    else:
        invoices = all_user_invoices

    # Calculate metrics from the in-memory list (no additional DB queries)
    total_invoices = len(all_user_invoices)
    paid_invoices = [inv for inv in all_user_invoices if inv.status == "paid"]
    unpaid_invoices = [inv for inv in all_user_invoices if inv.status == "unpaid"]
    paid_count = len(paid_invoices)
    unpaid_count = len(unpaid_invoices)

    # Calculate revenue from prefetched data
    revenue_value = sum(inv.total for inv in paid_invoices) if paid_invoices else Decimal("0")

    # Count unique clients from in-memory list
    unique_clients = len(set(inv.client_email for inv in all_user_invoices))

    context = {
        "invoices": invoices,
        "total_invoices": total_invoices,
        "paid_count": paid_count,
        "unpaid_count": unpaid_count,
        "total_revenue": revenue_value,
        "unique_clients": unique_clients,
        "filter_status": filter_status,
    }
    return render(request, "invoices/dashboard.html", context)


@login_required
def create_invoice(request):
    if request.method == "POST":
        invoice_form = InvoiceForm(request.POST, request.FILES)

        line_items_data = json.loads(request.POST.get("line_items", "[]"))

        if invoice_form.is_valid() and line_items_data:
            invoice = invoice_form.save(commit=False)
            invoice.user = request.user
            invoice.save()

            for item_data in line_items_data:
                LineItem.objects.create(
                    invoice=invoice,
                    description=item_data["description"],
                    quantity=Decimal(item_data["quantity"]),
                    unit_price=Decimal(item_data["unit_price"]),
                )

            messages.success(request, f"Invoice {invoice.invoice_id} created successfully!")
            return redirect("invoice_detail", invoice_id=invoice.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        invoice_form = InvoiceForm()

    return render(
        request,
        "invoices/create_invoice.html",
        {
            "invoice_form": invoice_form,
        },
    )


@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    return render(request, "invoices/invoice_detail.html", {"invoice": invoice})


@login_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)

    if request.method == "POST":
        invoice_form = InvoiceForm(request.POST, request.FILES, instance=invoice)
        line_items_data = json.loads(request.POST.get("line_items", "[]"))

        if invoice_form.is_valid() and line_items_data:
            invoice = invoice_form.save()

            invoice.line_items.all().delete()

            for item_data in line_items_data:
                LineItem.objects.create(
                    invoice=invoice,
                    description=item_data["description"],
                    quantity=Decimal(item_data["quantity"]),
                    unit_price=Decimal(item_data["unit_price"]),
                )

            messages.success(request, f"Invoice {invoice.invoice_id} updated successfully!")
            return redirect("invoice_detail", invoice_id=invoice.id)
    else:
        invoice_form = InvoiceForm(instance=invoice)

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
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)

    html_string = render_to_string("invoices/invoice_pdf.html", {"invoice": invoice})

    font_config = FontConfiguration()
    html = HTML(string=html_string)
    pdf = html.write_pdf(font_config=font_config)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Invoice_{invoice.invoice_id}.pdf"'

    return response


def _send_email_async(invoice_id, recipient_email):
    """Send invoice email in background thread using SendGrid."""
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        # Check if SendGrid API key is configured
        if os.environ.get("SENDGRID_API_KEY"):
            # Use SendGrid with dynamic templates
            send_invoice_email_sendgrid(invoice, recipient_email)
        else:
            # Fallback to Django email
            subject = f"Invoice #{invoice.invoice_id} from {invoice.business_name}"
            html_message = render_to_string("emails/invoice_email.html", {"invoice": invoice})
            
            payment_info = ""
            if invoice.bank_name:
                payment_info = f"\n\nPayment Information:\nBank: {invoice.bank_name}\nAccount Name: {invoice.account_name}\nAccount Number: {invoice.account_number}"
            
            notes_section = ""
            if invoice.notes:
                notes_section = f"\n\nNotes:\n{invoice.notes}"
            
            plain_message = f"""Dear {invoice.client_name},

Thank you for your business! Please find attached invoice #{invoice.invoice_id}.

Invoice Details:
- Invoice Number: {invoice.invoice_id}
- Invoice Date: {invoice.invoice_date.strftime('%B %d, %Y')}
- Total Amount: {invoice.currency} {invoice.total:.2f}
- Status: {invoice.get_status_display()}{payment_info}{notes_section}

If you have any questions, please contact us at {invoice.business_email}.

Best regards,
{invoice.business_name}
"""

            pdf_html_string = render_to_string("invoices/invoice_pdf.html", {"invoice": invoice})
            font_config = FontConfiguration()
            html = HTML(string=pdf_html_string)
            pdf = html.write_pdf(font_config=font_config)

            email = EmailMessage(
                subject,
                plain_message,
                invoice.business_email,
                [recipient_email],
            )
            email.content_subtype = "html"
            email.body = html_message
            email.attach(f"Invoice_{invoice.invoice_id}.pdf", pdf, "application/pdf")
            email.send()
    except Exception as e:
        print(f"Error sending invoice email: {str(e)}")


@login_required
def send_invoice_email(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)

    if request.method == "POST":
        recipient_email = request.POST.get("email", invoice.client_email)
        
        # Send email in background thread to avoid timeout
        thread = threading.Thread(
            target=_send_email_async,
            args=(invoice.id, recipient_email),
            daemon=True
        )
        thread.start()
        
        messages.success(request, f"Invoice is being sent to {recipient_email}. You'll receive a confirmation shortly.")
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
    phone = invoice.client_phone.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

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


def faq(request):
    return render(request, "pages/faq.html")


def support(request):
    return render(request, "pages/support.html")


def features(request):
    return render(request, "pages/features.html")


@login_required
def settings_view(request):
    """Handle user settings page with profile, security, and notification preferences."""
    from .forms import UserDetailsForm, UserProfileForm, PasswordChangeForm, NotificationPreferencesForm
    from django.contrib import messages
    from django.contrib.auth.hashers import check_password
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle form submissions
    message = None
    message_type = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            user_form = UserDetailsForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                message = "Profile updated successfully!"
                message_type = "success"
            else:
                message = "Please fix the errors below."
                message_type = "error"
                
        elif action == 'change_password':
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                current = password_form.cleaned_data.get('current_password')
                new = password_form.cleaned_data.get('new_password')
                
                if not check_password(current, request.user.password):
                    message = "Current password is incorrect."
                    message_type = "error"
                else:
                    request.user.set_password(new)
                    request.user.save()
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, request.user)
                    message = "Password changed successfully!"
                    message_type = "success"
            else:
                message = "Please fix the errors below."
                message_type = "error"
    
    # Prepare forms
    user_form = UserDetailsForm(instance=request.user)
    profile_form = UserProfileForm(instance=profile)
    password_form = PasswordChangeForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'message': message,
        'message_type': message_type,
    }
    
    return render(request, "pages/settings.html", context)


def about(request):
    return render(request, "pages/about.html")


def pricing(request):
    return render(request, "pages/pricing.html")


def terms(request):
    return render(request, "pages/terms.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def contact(request):
    return render(request, "pages/contact.html")


def careers(request):
    return render(request, "pages/careers.html")


def status(request):
    return render(request, "pages/status.html")


def changelog(request):
    return render(request, "pages/changelog.html")


@login_required
def analytics(request):
    invoices = Invoice.objects.filter(user=request.user).prefetch_related('line_items')

    total_invoices = invoices.count()
    paid_invoices = invoices.filter(status="paid").count()
    unpaid_invoices = invoices.filter(status="unpaid").count()

    # Calculate totals using invoice properties
    paid_invoice_list = list(invoices.filter(status="paid"))
    total_revenue = sum(inv.total for inv in paid_invoice_list) if paid_invoice_list else Decimal("0")

    unpaid_invoice_list = list(invoices.filter(status="unpaid"))
    outstanding_amount = sum(inv.total for inv in unpaid_invoice_list) if unpaid_invoice_list else Decimal("0")

    all_invoices = list(invoices)
    average_invoice = (
        sum(inv.total for inv in all_invoices) / len(all_invoices)
        if all_invoices
        else Decimal("0")
    )

    payment_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0

    now = datetime.now()
    current_month_invoices = invoices.filter(
        invoice_date__year=now.year, invoice_date__month=now.month
    ).count()

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

    # Calculate top clients manually since total is a property
    from collections import defaultdict
    client_data = defaultdict(lambda: {
        "client_name": "",
        "invoice_count": 0,
        "paid_count": 0,
        "total_revenue": Decimal("0"),
        "invoices": []
    })

    for invoice in all_invoices:
        client = client_data[invoice.client_name]
        client["client_name"] = invoice.client_name
        client["invoice_count"] += 1
        client["invoices"].append(invoice)
        if invoice.status == "paid":
            client["paid_count"] += 1
            client["total_revenue"] += invoice.total

    top_clients = sorted(
        [
            {
                "client_name": data["client_name"],
                "invoice_count": data["invoice_count"],
                "total_revenue": data["total_revenue"],
                "paid_count": data["paid_count"],
                "avg_invoice": sum(inv.total for inv in data["invoices"]) / len(data["invoices"]),
                "payment_rate": (data["paid_count"] / data["invoice_count"] * 100)
                if data["invoice_count"] > 0
                else 0,
            }
            for data in client_data.values()
        ],
        key=lambda x: x["total_revenue"],
        reverse=True,
    )[:10]

    recent_invoices = invoices.order_by("-created_at")[:10]

    context = {
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "unpaid_invoices": unpaid_invoices,
        "total_revenue": total_revenue,
        "outstanding_amount": outstanding_amount,
        "average_invoice": average_invoice,
        "payment_rate": payment_rate,
        "current_month_invoices": current_month_invoices,
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
        "top_clients": top_clients,
        "recent_invoices": recent_invoices,
    }

    return render(request, "invoices/analytics.html", context)


# Admin Views (Production-ready admin dashboard for platform management)
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("home")
    
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    total_invoices = Invoice.objects.count()
    
    # Optimize query with prefetch_related to avoid N+1
    paid_invoices_qs = Invoice.objects.filter(status="paid").prefetch_related('line_items')
    total_revenue = sum(inv.total for inv in paid_invoices_qs) if paid_invoices_qs.exists() else Decimal("0")
    paid_invoices = paid_invoices_qs.count()
    paid_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
    
    context = {
        "total_users": total_users,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "paid_rate": paid_rate,
    }
    return render(request, "admin/dashboard.html", context)


def admin_users(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request, "admin/users.html")


def admin_content(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request, "admin/content.html")


def admin_settings(request):
    if not request.user.is_superuser:
        return redirect("home")
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
    templates = InvoiceTemplate.objects.filter(user=request.user)
    
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
    
    return render(request, "invoices/templates.html", {
        "templates": templates,
        "form": form
    })


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
    recurring = RecurringInvoice.objects.filter(user=request.user)
    
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
    
    return render(request, "invoices/recurring.html", {
        "recurring_invoices": recurring,
        "form": form
    })


@login_required
def bulk_export(request):
    """Export multiple invoices at once."""
    invoice_ids = request.POST.getlist('invoice_ids')
    export_format = request.POST.get('format', 'csv')
    
    if not invoice_ids:
        messages.error(request, "Please select at least one invoice.")
        return redirect("dashboard")
    
    invoices = Invoice.objects.filter(id__in=invoice_ids, user=request.user).prefetch_related('line_items')
    
    if export_format == 'csv':
        csv_data = InvoiceExport.export_to_csv(invoices)
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invoices.csv"'
        return response
    elif export_format == 'pdf':
        pdfs = InvoiceExport.bulk_export_pdfs(invoices)
        if len(pdfs) == 1:
            response = HttpResponse(pdfs[0][1], content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdfs[0][0]}.pdf"'
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
        invoice_ids = request.POST.getlist('invoice_ids')
        if invoice_ids:
            deleted_count, _ = Invoice.objects.filter(id__in=invoice_ids, user=request.user).delete()
            messages.success(request, f"Deleted {deleted_count} invoice(s).")
        return redirect("dashboard")
    return redirect("dashboard")
