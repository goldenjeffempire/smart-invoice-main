"""Email service using AsyncTaskService for background processing."""

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .async_tasks import AsyncTaskService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class EmailService:
    """Email service with async background processing via thread pool."""

    @staticmethod
    def get_base_url() -> str:
        """Get the base URL for email links."""
        return getattr(settings, "PRODUCTION_URL", "https://invoiceflow.com.ng")

    @classmethod
    def send_verification_email(cls, user: "User", token: str) -> bool:
        """Send email verification link to user."""
        base_url = cls.get_base_url()
        verification_url = f"{base_url}/verify-email/{token}/"

        context = {
            "user": user,
            "verification_url": verification_url,
            "site_name": "InvoiceFlow",
            "expires_hours": 24,
        }

        try:
            html_content = render_to_string("emails/verify_email.html", context)
            text_content = f"""
Hello {user.first_name or user.username},

Thank you for signing up for InvoiceFlow!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The InvoiceFlow Team
            """.strip()

            send_mail(
                subject="Verify your InvoiceFlow account",
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False,
            )
            logger.info(f"Verification email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            return False

    @classmethod
    def send_password_reset_email(cls, user: "User", token: str) -> bool:
        """Send password reset link to user."""
        base_url = cls.get_base_url()
        reset_url = f"{base_url}/reset-password/{token}/"

        context = {
            "user": user,
            "reset_url": reset_url,
            "site_name": "InvoiceFlow",
            "expires_hours": 1,
        }

        try:
            html_content = render_to_string("emails/password_reset.html", context)
            text_content = f"""
Hello {user.first_name or user.username},

You requested a password reset for your InvoiceFlow account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email.

Best regards,
The InvoiceFlow Team
            """.strip()

            send_mail(
                subject="Reset your InvoiceFlow password",
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {e}")
            return False

    @staticmethod
    def send_invoice_email_async(invoice_id: int, recipient_email: str) -> None:
        """Send invoice email in background using thread pool.

        Uses AsyncTaskService for proper thread pool management.
        """
        AsyncTaskService.send_invoice_email_async(invoice_id, recipient_email)
        logger.debug(f"Queued invoice email for invoice {invoice_id} to {recipient_email}")

    @staticmethod
    def send_payment_reminder_async(invoice_id: int) -> None:
        """Send payment reminder email in background using thread pool."""
        AsyncTaskService.send_payment_reminder_async(invoice_id)
        logger.debug(f"Queued payment reminder for invoice {invoice_id}")
