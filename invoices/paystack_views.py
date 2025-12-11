"""
Paystack Payment Views for InvoiceFlow.
Handles payment initiation, callbacks, and webhooks.
"""

import json
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Invoice
from .paystack_service import get_paystack_service


@login_required
@require_POST
def initiate_invoice_payment(request, invoice_id):
    """Initiate payment for an invoice."""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    
    if invoice.status == "paid":
        messages.info(request, "This invoice has already been paid.")
        return redirect("invoice_detail", invoice_id=invoice.id)
    
    paystack = get_paystack_service()
    
    if not paystack.is_configured:
        messages.error(request, "Payment processing is not configured. Please contact support.")
        return redirect("invoice_detail", invoice_id=invoice.id)
    
    callback_url = request.build_absolute_uri(f"/payments/callback/{invoice.id}/")
    if callback_url.startswith("http://") and "localhost" not in callback_url:
        callback_url = callback_url.replace("http://", "https://", 1)
    
    reference = f"INV-{invoice.invoice_id}-{uuid.uuid4().hex[:8]}"
    
    result = paystack.initialize_payment(
        email=invoice.client_email or invoice.business_email,
        amount=invoice.total,
        currency=invoice.currency if invoice.currency in ["NGN", "USD", "GHS", "ZAR", "KES"] else "NGN",
        reference=reference,
        callback_url=callback_url,
        metadata={
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_id,
            "client_name": invoice.client_name,
            "business_name": invoice.business_name,
        },
    )
    
    if result["status"] == "success":
        invoice.payment_reference = reference
        invoice.save(update_fields=["payment_reference"])
        return redirect(result["authorization_url"])
    else:
        messages.error(request, f"Could not initialize payment: {result.get('message', 'Unknown error')}")
        return redirect("invoice_detail", invoice_id=invoice.id)


@require_GET
def payment_callback(request, invoice_id):
    """Handle Paystack payment callback."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    reference = request.GET.get("reference")
    
    if not reference:
        messages.error(request, "Invalid payment callback.")
        return redirect("invoice_detail", invoice_id=invoice.id)
    
    if invoice.payment_reference and invoice.payment_reference != reference:
        messages.error(request, "Invalid payment reference.")
        return redirect("invoice_detail", invoice_id=invoice.id)
    
    paystack = get_paystack_service()
    result = paystack.verify_payment(reference)
    
    if result["status"] == "success" and result.get("verified"):
        metadata = result.get("raw_data", {}).get("metadata", {})
        if str(metadata.get("invoice_id")) != str(invoice.id):
            messages.error(request, "Payment verification failed: Invoice mismatch.")
            return redirect("invoice_detail", invoice_id=invoice.id)
        
        invoice.status = "paid"
        invoice.payment_reference = reference
        invoice.save(update_fields=["status", "payment_reference"])
        
        messages.success(request, "Payment successful! Thank you for your payment.")
    else:
        messages.error(request, f"Payment verification failed: {result.get('message', 'Unknown error')}")
    
    return redirect("invoice_detail", invoice_id=invoice.id)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhook events."""
    paystack = get_paystack_service()
    
    signature = request.headers.get("X-Paystack-Signature", "")
    
    if not paystack.verify_webhook_signature(request.body, signature):
        return HttpResponse(status=400)
    
    try:
        payload = json.loads(request.body)
        event = payload.get("event")
        data = payload.get("data", {})
        
        if event == "charge.success":
            reference = data.get("reference")
            metadata = data.get("metadata", {})
            invoice_id = metadata.get("invoice_id")
            
            if invoice_id:
                try:
                    invoice = Invoice.objects.get(id=invoice_id)
                    if invoice.status != "paid":
                        invoice.status = "paid"
                        invoice.payment_reference = reference
                        invoice.save(update_fields=["status", "payment_reference"])
                except Invoice.DoesNotExist:  # type: ignore[attr-defined]
                    pass
        
        return HttpResponse(status=200)
    
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=500)


@login_required
def payment_status(request, invoice_id):
    """Check payment status for an invoice."""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    
    if not invoice.payment_reference:
        return JsonResponse({
            "status": "no_payment",
            "message": "No payment initiated for this invoice.",
        })
    
    paystack = get_paystack_service()
    result = paystack.verify_payment(invoice.payment_reference)
    
    return JsonResponse({
        "status": result.get("status"),
        "verified": result.get("verified", False),
        "invoice_status": invoice.status,
        "paid_at": result.get("paid_at"),
    })
