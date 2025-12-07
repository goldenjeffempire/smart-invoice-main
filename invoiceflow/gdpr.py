"""
GDPR Compliance Endpoints for InvoiceFlow.
Implements Subject Access Request (SAR), data export, and deletion.
"""

import json
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)
User = get_user_model()


@login_required
@require_GET
def export_user_data(request):
    """
    GDPR Article 20 - Right to Data Portability.
    Export all user data in machine-readable format (JSON).
    """
    try:
        user = request.user

        # Collect user profile data
        user_data = {
            "personal_information": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_joined": user.date_joined.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format_version": "1.0",
                "platform": "InvoiceFlow",
            },
        }

        # Get user profile if exists
        try:
            from invoices.models import Invoice, UserProfile

            profile = UserProfile.objects.filter(user=user).first()
            if profile:
                user_data["business_profile"] = {
                    "company_name": profile.company_name or "",
                    "company_address": profile.company_address or "",
                    "phone": profile.phone or "",
                    "website": profile.website or "",
                    "tax_number": profile.tax_number or "",
                }

            # Get invoice data
            invoices = Invoice.objects.filter(user=user)
            user_data["invoices"] = [
                {
                    "invoice_number": inv.invoice_number,
                    "client_name": inv.client_name,
                    "client_email": inv.client_email,
                    "amount": str(inv.total_amount) if hasattr(inv, "total_amount") else "0",
                    "status": inv.status,
                    "created_at": inv.created_at.isoformat(),
                }
                for inv in invoices
            ]

        except ImportError:
            pass

        # Create downloadable JSON file
        response = HttpResponse(
            json.dumps(user_data, indent=2).encode("utf-8"),
            content_type="application/json; charset=utf-8",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="invoiceflow_data_export_{user.username}_{datetime.now().strftime("%Y%m%d")}.json"'
        )

        logger.info(f"Data export requested by user: {user.username}")

        return response

    except Exception as e:
        logger.error(f"Data export error: {e}")
        return JsonResponse(
            {
                "success": False,
                "error": "An error occurred exporting your data.",
            },
            status=500,
        )


@login_required
@csrf_protect
@require_POST
def request_data_deletion(request):
    """
    GDPR Article 17 - Right to Erasure (Right to be Forgotten).
    Submit a request to delete all user data.
    """
    try:
        user = request.user

        # Send confirmation email to user
        send_mail(
            subject="[InvoiceFlow] Data Deletion Request Received",
            message=f"""
Dear {user.first_name or user.username},

We have received your request to delete your InvoiceFlow account and associated data.

Request Details:
- Account: {user.email}
- Requested: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

We will process your request within 30 days as required by GDPR. You will receive a confirmation email once the deletion is complete.

If you did not make this request, please contact us immediately at privacy@invoiceflow.com.ng

Best regards,
The InvoiceFlow Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        # Send notification to admin
        send_mail(
            subject=f"[InvoiceFlow Admin] Data Deletion Request - {user.username}",
            message=f"""
Data Deletion Request Received

User: {user.username}
Email: {user.email}
Requested: {datetime.utcnow().isoformat()}

Please process this request within 30 days as required by GDPR.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["privacy@invoiceflow.com.ng"],
            fail_silently=True,
        )

        logger.info(f"Data deletion requested by user: {user.username}")

        return JsonResponse(
            {
                "success": True,
                "message": "Your data deletion request has been submitted. You will receive a confirmation email shortly.",
            }
        )

    except Exception as e:
        logger.error(f"Data deletion request error: {e}")
        return JsonResponse(
            {
                "success": False,
                "error": "An error occurred submitting your request.",
            },
            status=500,
        )


@login_required
@csrf_protect
@require_POST
def submit_sar(request):
    """
    GDPR Article 15 - Right of Access (Subject Access Request).
    Submit a formal SAR for comprehensive data disclosure.
    """
    try:
        user = request.user
        data = json.loads(request.body) if request.body else {}

        request_details = data.get("details", "Full data access request")

        # Send confirmation to user
        send_mail(
            subject="[InvoiceFlow] Subject Access Request Received",
            message=f"""
Dear {user.first_name or user.username},

We have received your Subject Access Request (SAR) under GDPR Article 15.

Request Details:
- Account: {user.email}
- Request: {request_details}
- Submitted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

We will respond to your request within 30 days. If you need immediate access to your data, you can use the "Export My Data" feature in your account settings.

Best regards,
The InvoiceFlow Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        # Notify privacy team
        send_mail(
            subject=f"[InvoiceFlow Admin] SAR Request - {user.username}",
            message=f"""
Subject Access Request Received

User: {user.username}
Email: {user.email}
Request: {request_details}
Submitted: {datetime.utcnow().isoformat()}

Please respond within 30 days as required by GDPR Article 15.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["privacy@invoiceflow.com.ng"],
            fail_silently=True,
        )

        logger.info(f"SAR submitted by user: {user.username}")

        return JsonResponse(
            {
                "success": True,
                "message": "Your Subject Access Request has been submitted. You will receive a response within 30 days.",
            }
        )

    except Exception as e:
        logger.error(f"SAR submission error: {e}")
        return JsonResponse(
            {
                "success": False,
                "error": "An error occurred submitting your request.",
            },
            status=500,
        )
