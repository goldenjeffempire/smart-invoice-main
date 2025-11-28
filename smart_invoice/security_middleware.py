"""
Custom security middleware for Smart Invoice.
Implements additional security headers and logging.
"""

import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses for defense in depth.

    Headers implemented:
    - X-Content-Type-Options: nosniff (prevent MIME sniffing)
    - X-Frame-Options: DENY (prevent clickjacking)
    - X-XSS-Protection: 1; mode=block (legacy XSS protection)
    - X-Download-Options: noopen (prevent file execution in IE)
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: Restrict browser features
    - Strict-Transport-Security: HTTPS enforcement (HSTS)
    """

    def process_response(self, request, response):
        # MIME type sniffing protection
        response["X-Content-Type-Options"] = "nosniff"

        # Clickjacking protection
        response["X-Frame-Options"] = "DENY"

        # Legacy XSS protection (for older browsers)
        response["X-XSS-Protection"] = "1; mode=block"

        # Prevent file execution in IE (legacy)
        response["X-Download-Options"] = "noopen"

        # Referrer policy for privacy
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (restrict browser features)
        response["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), "
            "usb=(), magnetometer=(), accelerometer=(), gyroscope=()"
        )

        # HSTS for HTTPS enforcement (only on secure connections)
        if request.is_secure() and not request.get_host().startswith("localhost"):
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response


class SecurityEventLoggingMiddleware(MiddlewareMixin):
    """
    Log security-relevant events for monitoring and audit trails.
    """

    def process_request(self, request):
        # Skip logging for test environment
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
        # Skip logging for test environment
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
