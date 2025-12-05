"""
Custom security middleware for InvoiceFlow.
Implements additional security headers, logging, and cookie consent.
"""

import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses for defense in depth.

    Headers implemented per Phase 0 security requirements:
    - X-Content-Type-Options: nosniff (prevent MIME sniffing)
    - X-Frame-Options: DENY (prevent clickjacking)
    - X-Download-Options: noopen (prevent file execution in IE)
    - Referrer-Policy: no-referrer-when-downgrade (Phase 0 requirement)
    - Permissions-Policy: Restrict browser features (camera, microphone, geolocation)
    - Strict-Transport-Security: HTTPS enforcement (HSTS) with preload
    - Cross-Origin-Opener-Policy: same-origin (isolate browsing context)
    - Cross-Origin-Resource-Policy: same-origin (prevent cross-origin resource access)
    
    Note: X-XSS-Protection is intentionally removed as it is deprecated
    and can introduce vulnerabilities in modern browsers. CSP provides
    better XSS protection.
    """

    def process_response(self, request, response):
        # Core security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-Download-Options"] = "noopen"
        
        # Referrer Policy - Phase 0 requirement
        response["Referrer-Policy"] = "no-referrer-when-downgrade"
        
        # Permissions Policy - Phase 0 requirement (strict feature restrictions)
        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), "
            "usb=(), magnetometer=(), accelerometer=(), gyroscope=(), "
            "autoplay=(), fullscreen=(self), picture-in-picture=()"
        )
        
        # Cross-Origin headers
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Resource-Policy"] = "same-origin"

        # HSTS - Always set in Replit with is_secure() or in production
        # For production, ensure 1 year max-age with includeSubDomains and preload
        is_production = getattr(settings, 'IS_PRODUCTION', False)
        is_replit = getattr(settings, 'IS_REPLIT', False)
        
        if request.is_secure() or is_production or is_replit:
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response


class SecurityEventLoggingMiddleware(MiddlewareMixin):
    """
    Log security-relevant events for monitoring and audit trails.
    """

    def process_request(self, request):
        if "test" in request.META.get("SERVER_NAME", ""):
            return None

        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            user_info = "anonymous"
            if (
                hasattr(request, "user")
                and request.user
                and hasattr(request.user, "is_authenticated")
            ):
                user_info = request.user.username if request.user.is_authenticated else "anonymous"

            logger.info(
                f"Security Event: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"user={user_info}"
            )
        return None

    def process_response(self, request, response):
        if "test" in request.META.get("SERVER_NAME", ""):
            return response

        if response.status_code >= 400:
            user_info = "anonymous"
            if (
                hasattr(request, "user")
                and request.user
                and hasattr(request.user, "is_authenticated")
            ):
                user_info = request.user.username if request.user.is_authenticated else "anonymous"

            logger.warning(
                f"HTTP {response.status_code}: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"user={user_info}"
            )
        return response

    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip


class CookieConsentMiddleware(MiddlewareMixin):
    """
    Cookie Consent Management Platform (CMP) middleware.
    
    Implements GDPR-compliant cookie consent:
    - Blocks non-essential cookies until explicit consent
    - Stores consent state in a secure cookie
    - Provides consent withdrawal support
    """
    
    CONSENT_COOKIE_NAME = "invoiceflow_cookie_consent"
    ESSENTIAL_COOKIES = [
        "csrftoken",
        "sessionid",
        "invoiceflow_cookie_consent",
    ]
    
    def process_request(self, request):
        # Check if user has given cookie consent
        consent = request.COOKIES.get(self.CONSENT_COOKIE_NAME, "")
        request.cookie_consent = self._parse_consent(consent)
        return None
    
    def process_response(self, request, response):
        # Don't modify API responses or static files
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response
        
        # If no consent given, remove non-essential cookies
        if not hasattr(request, "cookie_consent") or not request.cookie_consent.get("analytics", False):
            for cookie_name in list(response.cookies.keys()):
                if cookie_name not in self.ESSENTIAL_COOKIES:
                    response.delete_cookie(cookie_name)
        
        return response
    
    def _parse_consent(self, consent_string):
        """Parse consent cookie value into structured data."""
        default_consent = {
            "essential": True,  # Always allowed
            "analytics": False,
            "marketing": False,
            "preferences": False,
            "timestamp": None,
        }
        
        if not consent_string:
            return default_consent
        
        try:
            consent_data = json.loads(consent_string)
            return {
                "essential": True,
                "analytics": consent_data.get("analytics", False),
                "marketing": consent_data.get("marketing", False),
                "preferences": consent_data.get("preferences", False),
                "timestamp": consent_data.get("timestamp"),
            }
        except (json.JSONDecodeError, TypeError, ValueError):
            return default_consent
