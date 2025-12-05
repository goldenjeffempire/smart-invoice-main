"""
Unified middleware for InvoiceFlow - Consolidated for performance.
Combines request logging, performance monitoring, security headers, and caching.
Eliminates duplicate middleware processing for faster response times.
"""

import time
import json
import uuid
import logging
from typing import Callable, Any
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from django.core.cache import cache
from django.utils.cache import add_never_cache_headers, patch_cache_control

logger = logging.getLogger(__name__)

STATIC_MARKETING_PAGES = frozenset([
    '/features/', '/pricing/', '/templates/', '/api-access/',
    '/about/', '/careers/', '/contact/', '/changelog/',
    '/system-status/', '/support/', '/faq/', '/terms/', '/privacy/',
])

HEALTH_CHECK_PATHS = frozenset(['/health/', '/health/ready/', '/health/live/', '/health/detailed/'])


class UnifiedMiddleware:
    """
    Single consolidated middleware that handles:
    - Request/response logging with timing
    - Performance monitoring  
    - Security headers
    - Cache control
    - Rate limiting (optional per-path)
    
    This replaces multiple separate middleware for better performance.
    """
    
    SLOW_REQUEST_THRESHOLD = 1.0
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.is_production = getattr(settings, 'IS_PRODUCTION', False)
        self.is_replit = getattr(settings, 'IS_REPLIT', False)
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()
        
        is_health_check = request.path in HEALTH_CHECK_PATHS
        is_static = request.path.startswith('/static/')
        is_marketing = request.path in STATIC_MARKETING_PAGES
        
        response = self.get_response(request)
        
        duration = time.perf_counter() - start_time
        duration_ms = duration * 1000
        
        self._add_security_headers(request, response)
        self._add_cache_headers(request, response, is_static, is_marketing)
        self._add_timing_headers(response, duration_ms, request.request_id)
        
        if not is_health_check and not is_static:
            self._log_request(request, response, duration_ms)
        
        return response
    
    def _add_security_headers(self, request: HttpRequest, response: HttpResponse) -> None:
        """Add security headers in a single pass."""
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-Download-Options"] = "noopen"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), "
            "usb=(), magnetometer=(), accelerometer=(), gyroscope=()"
        )
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        
        if request.is_secure() or self.is_production or self.is_replit:
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    def _add_cache_headers(self, request: HttpRequest, response: HttpResponse, 
                           is_static: bool, is_marketing: bool) -> None:
        """Optimized cache control."""
        if is_static:
            patch_cache_control(response, public=True, max_age=31536000, immutable=True)
        elif is_marketing and not request.user.is_authenticated:
            patch_cache_control(response, public=True, max_age=300, stale_while_revalidate=60)
        elif response.get("Content-Type", "").startswith("text/html"):
            add_never_cache_headers(response)
    
    def _add_timing_headers(self, response: HttpResponse, duration_ms: float, 
                            request_id: str) -> None:
        """Add performance timing headers."""
        response["Server-Timing"] = f"total;dur={duration_ms:.0f}"
        response["X-Request-ID"] = request_id
        response["X-Response-Time"] = f"{duration_ms:.2f}ms"
    
    def _log_request(self, request: HttpRequest, response: HttpResponse, 
                     duration_ms: float) -> None:
        """Log request with appropriate level based on duration and status."""
        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "user": request.user.username if request.user.is_authenticated else "anonymous",
            "ip": self._get_client_ip(request),
        }
        
        log_level = logging.INFO
        log_prefix = "Request"
        
        if response.status_code >= 500:
            log_level = logging.ERROR
            log_prefix = "Error"
        elif response.status_code >= 400:
            log_level = logging.WARNING
            log_prefix = "Client Error"
        elif duration_ms > self.SLOW_REQUEST_THRESHOLD * 1000:
            log_level = logging.WARNING
            log_prefix = "Slow Request"
        
        logger.log(log_level, f"{log_prefix}: {json.dumps(log_data)}")
    
    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class OptimizedRateLimitMiddleware:
    """
    Efficient rate limiting with sliding window.
    Uses cache for O(1) lookups.
    """
    
    DEFAULT_LIMIT = 200
    DEFAULT_WINDOW = 3600
    
    EXEMPT_PATHS = HEALTH_CHECK_PATHS | {'/static/'}
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._is_exempt(request.path):
            return self.get_response(request)
        
        client_ip = self._get_client_ip(request)
        cache_key = f"ratelimit:{client_ip}"
        
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.DEFAULT_LIMIT:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse(
                {"error": "Rate limit exceeded. Please try again later."},
                status=429
            )
        
        cache.set(cache_key, current_count + 1, self.DEFAULT_WINDOW)
        
        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(self.DEFAULT_LIMIT)
        response["X-RateLimit-Remaining"] = str(max(0, self.DEFAULT_LIMIT - current_count - 1))
        
        return response
    
    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting."""
        if path.startswith('/static/'):
            return True
        return path in self.EXEMPT_PATHS
    
    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class CookieConsentMiddleware:
    """
    Streamlined cookie consent management.
    GDPR-compliant with minimal overhead.
    """
    
    CONSENT_COOKIE = "invoiceflow_consent"
    ESSENTIAL_COOKIES = frozenset(["csrftoken", "sessionid", "invoiceflow_consent"])
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        consent = self._parse_consent(request.COOKIES.get(self.CONSENT_COOKIE, ""))
        request.cookie_consent = consent
        
        response = self.get_response(request)
        
        if "text/html" not in response.get("Content-Type", ""):
            return response
        
        if not consent.get("analytics", False):
            for cookie_name in list(response.cookies.keys()):
                if cookie_name not in self.ESSENTIAL_COOKIES:
                    response.delete_cookie(cookie_name)
        
        return response
    
    def _parse_consent(self, consent_string: str) -> dict[str, Any]:
        """Parse consent cookie efficiently."""
        default = {"essential": True, "analytics": False, "marketing": False}
        
        if not consent_string:
            return default
        
        try:
            data = json.loads(consent_string)
            return {
                "essential": True,
                "analytics": bool(data.get("analytics")),
                "marketing": bool(data.get("marketing")),
            }
        except (json.JSONDecodeError, TypeError):
            return default
