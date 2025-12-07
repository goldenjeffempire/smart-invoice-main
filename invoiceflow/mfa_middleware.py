"""
MFA Enforcement Middleware for InvoiceFlow.
Ensures users with MFA enabled complete verification before accessing protected views.
"""

import logging

from django.conf import settings
from django.shortcuts import redirect
from django.urls import Resolver404, resolve
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class MFAEnforcementMiddleware(MiddlewareMixin):
    """
    Middleware to enforce MFA verification for authenticated users.
    Blocks access to protected views until MFA is verified.
    """

    EXEMPT_URL_NAMES = [
        "mfa_setup",
        "mfa_verify",
        "logout",
        "login",
        "signup",
        "home",
        "password_reset",
        "password_reset_done",
        "password_reset_confirm",
        "password_reset_complete",
        "health_check",
        "readiness_check",
        "liveness_check",
        "set_cookie_consent",
        "get_cookie_consent",
        "withdraw_cookie_consent",
        "robots_txt",
        "django.contrib.sitemaps.views.sitemap",
        "privacy",
        "terms",
        "about",
        "features",
        "pricing",
        "contact",
        "faq",
        "support",
        "careers",
        "changelog",
        "status",
    ]

    EXEMPT_PATH_PREFIXES = [
        "/static/",
        "/media/",
        "/api/consent/",
    ]

    def process_request(self, request):
        if not getattr(settings, "MFA_ENABLED", False):
            return None

        if not request.user.is_authenticated:
            return None

        if self._is_exempt_path(request.path):
            return None

        if self._is_exempt_url(request):
            return None

        if request.session.get("mfa_verified", False):
            return None

        try:
            from invoices.models import MFAProfile

            mfa_profile = MFAProfile.objects.get(user=request.user)

            if mfa_profile.is_enabled:
                logger.warning(
                    f"MFA verification required for user {request.user.username} "
                    f"attempting to access {request.path}"
                )
                return redirect("mfa_verify")
        except MFAProfile.DoesNotExist:
            pass

        return None

    def _is_exempt_path(self, path):
        """Check if path is in exempt prefixes."""
        for prefix in self.EXEMPT_PATH_PREFIXES:
            if path.startswith(prefix):
                return True
        return False

    def _is_exempt_url(self, request):
        """Check if URL name is in exempt list."""
        try:
            resolved = resolve(request.path)
            return resolved.url_name in self.EXEMPT_URL_NAMES
        except Resolver404:
            return False
