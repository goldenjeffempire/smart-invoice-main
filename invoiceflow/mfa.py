"""
Multi-Factor Authentication (MFA/2FA) Module for InvoiceFlow.
Implements TOTP (Time-based One-Time Password) support.
"""

import base64
import io
import logging
import secrets
import string
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

logger = logging.getLogger(__name__)


def generate_secret_key():
    """Generate a secure random secret key for TOTP."""
    try:
        import pyotp

        return pyotp.random_base32()
    except ImportError:
        logger.warning("pyotp not available, generating fallback secret")
        chars = string.ascii_uppercase + "234567"
        return "".join(secrets.choice(chars) for _ in range(32))


def generate_recovery_codes(count=None):
    """Generate recovery codes for MFA backup."""
    if count is None:
        count = getattr(settings, "MFA_RECOVERY_CODES_COUNT", 10)

    codes = []
    for _ in range(count):
        code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes


def verify_totp(secret, token):
    """Verify a TOTP token against the secret."""
    try:
        import pyotp

        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    except ImportError:
        logger.error("pyotp not available for TOTP verification")
        return False
    except Exception as e:
        logger.error(f"TOTP verification error: {e}")
        return False


def get_totp_uri(secret, email, issuer=None):
    """Generate TOTP provisioning URI for authenticator apps."""
    if issuer is None:
        issuer = getattr(settings, "MFA_ISSUER_NAME", "InvoiceFlow")

    try:
        import pyotp

        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)
    except ImportError:
        logger.error("pyotp not available for URI generation")
        return None


def generate_qr_code(uri):
    """Generate QR code image for TOTP URI."""
    try:
        import qrcode

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()
    except ImportError:
        logger.error("qrcode library not available")
        return None


def mfa_required(view_func):
    """
    Decorator that requires MFA verification for a view.
    If MFA is enabled for the user but not verified in session, redirects to MFA verification.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        if not getattr(settings, "MFA_ENABLED", False):
            return view_func(request, *args, **kwargs)

        mfa_profile = getattr(request.user, "mfa_profile", None)
        if mfa_profile and mfa_profile.is_enabled:
            if not request.session.get("mfa_verified"):
                return redirect("mfa_verify")

        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@require_http_methods(["GET", "POST"])
def mfa_setup(request):
    """Set up MFA for the current user."""
    from invoices.models import MFAProfile

    mfa_profile, created = MFAProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        token = request.POST.get("token", "").strip()

        if not mfa_profile.secret_key:
            return JsonResponse({"error": "MFA setup not initialized"}, status=400)

        if verify_totp(mfa_profile.secret_key, token):
            mfa_profile.is_enabled = True
            mfa_profile.recovery_codes = generate_recovery_codes()
            mfa_profile.save()
            request.session["mfa_verified"] = True

            logger.info(f"MFA enabled for user: {request.user.username}")

            return render(
                request,
                "auth/mfa_setup_complete.html",
                {"recovery_codes": mfa_profile.recovery_codes},
            )
        else:
            return render(
                request,
                "auth/mfa_setup.html",
                {
                    "error": "Invalid verification code. Please try again.",
                    "qr_code": generate_qr_code(
                        get_totp_uri(mfa_profile.secret_key, request.user.email)
                    ),
                    "secret_key": mfa_profile.secret_key,
                },
            )

    if not mfa_profile.secret_key or not mfa_profile.is_enabled:
        mfa_profile.secret_key = generate_secret_key()
        mfa_profile.save()

    uri = get_totp_uri(mfa_profile.secret_key, request.user.email)
    qr_code = generate_qr_code(uri) if uri else None

    return render(
        request,
        "auth/mfa_setup.html",
        {
            "qr_code": qr_code,
            "secret_key": mfa_profile.secret_key,
            "is_enabled": mfa_profile.is_enabled,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def mfa_verify(request):
    """Verify MFA token during login."""
    from invoices.models import MFAProfile

    try:
        mfa_profile = MFAProfile.objects.get(user=request.user)
    except MFAProfile.DoesNotExist:
        return redirect("dashboard")

    if not mfa_profile.is_enabled:
        return redirect("dashboard")

    if request.method == "POST":
        token = request.POST.get("token", "").strip()

        if verify_totp(mfa_profile.secret_key, token):
            request.session["mfa_verified"] = True
            logger.info(f"MFA verified for user: {request.user.username}")
            return redirect("dashboard")

        recovery_code = request.POST.get("recovery_code", "").strip().upper()
        if recovery_code:
            if mfa_profile.recovery_codes and recovery_code in mfa_profile.recovery_codes:
                mfa_profile.recovery_codes.remove(recovery_code)
                mfa_profile.save()
                request.session["mfa_verified"] = True
                logger.info(f"MFA verified via recovery code for user: {request.user.username}")
                return redirect("dashboard")

        return render(
            request,
            "auth/mfa_verify.html",
            {"error": "Invalid verification code. Please try again."},
        )

    return render(request, "auth/mfa_verify.html")


@login_required
@require_POST
def mfa_disable(request):
    """Disable MFA for the current user. Requires MFA verification and password."""
    from invoices.models import MFAProfile

    if not request.session.get("mfa_verified", False):
        return JsonResponse({"error": "MFA verification required"}, status=403)

    password = request.POST.get("password", "")
    totp_code = request.POST.get("totp_code", "").strip()

    if not request.user.check_password(password):
        return JsonResponse({"error": "Invalid password"}, status=400)

    try:
        mfa_profile = MFAProfile.objects.get(user=request.user)

        if mfa_profile.is_enabled and mfa_profile.secret_key:
            if not totp_code or not verify_totp(mfa_profile.secret_key, totp_code):
                return JsonResponse({"error": "Invalid TOTP code"}, status=400)

        mfa_profile.is_enabled = False
        mfa_profile.secret_key = ""
        mfa_profile.recovery_codes = []
        mfa_profile.save()

        request.session.pop("mfa_verified", None)
        logger.info(f"MFA disabled for user: {request.user.username}")

        return JsonResponse({"success": True, "message": "MFA has been disabled"})
    except MFAProfile.DoesNotExist:
        return JsonResponse({"error": "MFA not configured"}, status=400)


@login_required
@require_POST
def mfa_regenerate_recovery(request):
    """Regenerate recovery codes for the current user. Requires MFA verification."""
    from invoices.models import MFAProfile

    if not request.session.get("mfa_verified", False):
        return JsonResponse({"error": "MFA verification required"}, status=403)

    password = request.POST.get("password", "")

    if not request.user.check_password(password):
        return JsonResponse({"error": "Invalid password"}, status=400)

    try:
        mfa_profile = MFAProfile.objects.get(user=request.user)
        if not mfa_profile.is_enabled:
            return JsonResponse({"error": "MFA not enabled"}, status=400)

        mfa_profile.recovery_codes = generate_recovery_codes()
        mfa_profile.save()

        logger.info(f"Recovery codes regenerated for user: {request.user.username}")

        return JsonResponse({"success": True, "recovery_codes": mfa_profile.recovery_codes})
    except MFAProfile.DoesNotExist:
        return JsonResponse({"error": "MFA not configured"}, status=400)
