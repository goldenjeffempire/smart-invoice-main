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
        elif is_marketing and not getattr(request, 'user', None) or (is_marketing and hasattr(request, 'user') and not request.user.is_authenticated):
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
        user = getattr(request, 'user', None)
        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "user": user.username if user and user.is_authenticated else "anonymous",
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


class SlidingWindowRateLimiter:
    """
    Advanced rate limiting with true sliding window algorithm.
    
    Features:
    - Sliding window for accurate rate limiting (not fixed windows)
    - Per-endpoint rate limits
    - User-tier based limits (anonymous, authenticated, premium)
    - Proper rate limit headers including reset time
    - Efficient O(1) cache operations
    """
    
    WINDOW_SIZE = 60
    
    TIER_LIMITS: dict[str, dict[str, int]] = {
        "anonymous": {
            "requests_per_minute": 30,
            "requests_per_hour": 200,
        },
        "authenticated": {
            "requests_per_minute": 60,
            "requests_per_hour": 500,
        },
        "premium": {
            "requests_per_minute": 120,
            "requests_per_hour": 2000,
        },
    }
    
    ENDPOINT_LIMITS: dict[str, dict[str, int]] = {
        "/api/": {"per_minute": 60, "per_hour": 300},
        "/api/v1/invoices/": {"per_minute": 30, "per_hour": 200},
        "/api/v1/invoices/generate-pdf/": {"per_minute": 10, "per_hour": 50},
        "/api/v1/invoices/send-email/": {"per_minute": 5, "per_hour": 30},
        "/login/": {"per_minute": 10, "per_hour": 30},
        "/signup/": {"per_minute": 5, "per_hour": 20},
        "/password-reset/": {"per_minute": 3, "per_hour": 10},
    }
    
    EXEMPT_PATHS = HEALTH_CHECK_PATHS | {'/static/', '/favicon.ico'}
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._is_exempt(request.path):
            return self.get_response(request)
        
        client_key = self._get_client_key(request)
        user_tier = self._get_user_tier(request)
        endpoint_key = self._get_endpoint_key(request.path)
        
        current_time = int(time.time())
        minute_window = current_time // 60
        hour_window = current_time // 3600
        
        is_limited, limit_info = self._check_rate_limit(
            client_key, user_tier, endpoint_key, minute_window, hour_window
        )
        
        if is_limited:
            logger.warning(
                f"Rate limit exceeded: client={client_key[:16]}..., "
                f"tier={user_tier}, endpoint={endpoint_key}, "
                f"type={limit_info['type']}"
            )
            response = JsonResponse(
                {
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Try again in {limit_info['retry_after']} seconds.",
                        "retry_after": limit_info["retry_after"],
                    }
                },
                status=429
            )
            self._add_rate_limit_headers(response, limit_info)
            return response
        
        self._increment_counters(client_key, endpoint_key, minute_window, hour_window)
        
        response = self.get_response(request)
        self._add_rate_limit_headers(response, limit_info)
        
        return response
    
    def _get_client_key(self, request: HttpRequest) -> str:
        """Generate a unique client key combining IP and user ID if authenticated."""
        ip = self._get_client_ip(request)
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}:{ip}"
        return f"ip:{ip}"
    
    def _get_user_tier(self, request: HttpRequest) -> str:
        """Determine user tier for rate limiting."""
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return "anonymous"
        
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            if hasattr(profile, 'subscription_tier'):
                if profile.subscription_tier in ('premium', 'enterprise'):
                    return "premium"
        
        if request.user.is_staff or request.user.is_superuser:
            return "premium"
        
        return "authenticated"
    
    def _get_endpoint_key(self, path: str) -> str:
        """Match path to endpoint rate limit key."""
        for endpoint in sorted(self.ENDPOINT_LIMITS.keys(), key=len, reverse=True):
            if path.startswith(endpoint):
                return endpoint
        return "default"
    
    def _check_rate_limit(
        self, 
        client_key: str, 
        user_tier: str, 
        endpoint_key: str,
        minute_window: int,
        hour_window: int
    ) -> tuple[bool, dict[str, Any]]:
        """
        Check if request should be rate limited using sliding window.
        Returns (is_limited, limit_info).
        
        Uses separate counters for:
        - Global tier-based limits (all endpoints combined)
        - Per-endpoint specific limits (if endpoint has custom limits)
        """
        tier_limits = self.TIER_LIMITS.get(user_tier, self.TIER_LIMITS["anonymous"])
        endpoint_limits = self.ENDPOINT_LIMITS.get(endpoint_key, {})
        has_endpoint_limits = bool(endpoint_limits)
        
        tier_minute_limit = tier_limits["requests_per_minute"]
        tier_hour_limit = tier_limits["requests_per_hour"]
        
        endpoint_minute_limit = endpoint_limits.get("per_minute", tier_minute_limit)
        endpoint_hour_limit = endpoint_limits.get("per_hour", tier_hour_limit)
        
        current_time = int(time.time())
        seconds_into_window = current_time % 60
        weight = (60 - seconds_into_window) / 60
        
        global_minute_key = f"rl:m:g:{client_key}:{minute_window}"
        global_hour_key = f"rl:h:g:{client_key}:{hour_window}"
        global_prev_minute_key = f"rl:m:g:{client_key}:{minute_window - 1}"
        
        try:
            global_minute_count = cache.get(global_minute_key, 0)
            global_prev_minute_count = cache.get(global_prev_minute_key, 0)
            global_sliding_minute = global_minute_count + (global_prev_minute_count * weight)
            global_hour_count = cache.get(global_hour_key, 0)
        except Exception:
            global_minute_count = 0
            global_prev_minute_count = 0
            global_sliding_minute = 0
            global_hour_count = 0
        
        endpoint_sliding_minute = 0.0
        endpoint_hour_count = 0
        
        if has_endpoint_limits:
            ep_safe_key = endpoint_key.replace("/", "_")
            endpoint_minute_key = f"rl:m:e:{ep_safe_key}:{client_key}:{minute_window}"
            endpoint_hour_key = f"rl:h:e:{ep_safe_key}:{client_key}:{hour_window}"
            endpoint_prev_minute_key = f"rl:m:e:{ep_safe_key}:{client_key}:{minute_window - 1}"
            
            try:
                ep_minute_count = cache.get(endpoint_minute_key, 0)
                ep_prev_minute_count = cache.get(endpoint_prev_minute_key, 0)
                endpoint_sliding_minute = ep_minute_count + (ep_prev_minute_count * weight)
                endpoint_hour_count = cache.get(endpoint_hour_key, 0)
            except Exception:
                ep_minute_count = 0
                ep_prev_minute_count = 0
                endpoint_sliding_minute = 0.0
                endpoint_hour_count = 0
        
        global_remaining_minute = max(0, tier_minute_limit - int(global_sliding_minute) - 1)
        global_remaining_hour = max(0, tier_hour_limit - global_hour_count - 1)
        
        if has_endpoint_limits:
            endpoint_remaining_minute = max(0, endpoint_minute_limit - int(endpoint_sliding_minute) - 1)
            endpoint_remaining_hour = max(0, endpoint_hour_limit - endpoint_hour_count - 1)
            effective_remaining_minute = min(global_remaining_minute, endpoint_remaining_minute)
            effective_remaining_hour = min(global_remaining_hour, endpoint_remaining_hour)
            effective_minute_limit = min(tier_minute_limit, endpoint_minute_limit)
            effective_hour_limit = min(tier_hour_limit, endpoint_hour_limit)
        else:
            effective_remaining_minute = global_remaining_minute
            effective_remaining_hour = global_remaining_hour
            effective_minute_limit = tier_minute_limit
            effective_hour_limit = tier_hour_limit
        
        limit_info = {
            "limit_minute": effective_minute_limit,
            "limit_hour": effective_hour_limit,
            "remaining_minute": effective_remaining_minute,
            "remaining_hour": effective_remaining_hour,
            "reset_minute": (minute_window + 1) * 60,
            "reset_hour": (hour_window + 1) * 3600,
            "type": None,
            "retry_after": 0,
            "endpoint_key": endpoint_key,
        }
        
        if has_endpoint_limits and endpoint_sliding_minute >= endpoint_minute_limit:
            limit_info["type"] = "endpoint_minute"
            limit_info["retry_after"] = 60 - seconds_into_window
            return True, limit_info
        
        if global_sliding_minute >= tier_minute_limit:
            limit_info["type"] = "global_minute"
            limit_info["retry_after"] = 60 - seconds_into_window
            return True, limit_info
        
        if has_endpoint_limits and endpoint_hour_count >= endpoint_hour_limit:
            limit_info["type"] = "endpoint_hour"
            limit_info["retry_after"] = 3600 - (current_time % 3600)
            return True, limit_info
        
        if global_hour_count >= tier_hour_limit:
            limit_info["type"] = "global_hour"
            limit_info["retry_after"] = 3600 - (current_time % 3600)
            return True, limit_info
        
        return False, limit_info
    
    def _increment_counters(
        self, 
        client_key: str, 
        endpoint_key: str,
        minute_window: int, 
        hour_window: int
    ) -> None:
        """Increment rate limit counters for both global and endpoint-specific buckets."""
        global_minute_key = f"rl:m:g:{client_key}:{minute_window}"
        global_hour_key = f"rl:h:g:{client_key}:{hour_window}"
        
        try:
            try:
                cache.incr(global_minute_key)
            except ValueError:
                cache.set(global_minute_key, 1, 120)
            
            try:
                cache.incr(global_hour_key)
            except ValueError:
                cache.set(global_hour_key, 1, 7200)
            
            if endpoint_key in self.ENDPOINT_LIMITS:
                ep_safe_key = endpoint_key.replace("/", "_")
                endpoint_minute_key = f"rl:m:e:{ep_safe_key}:{client_key}:{minute_window}"
                endpoint_hour_key = f"rl:h:e:{ep_safe_key}:{client_key}:{hour_window}"
                
                try:
                    cache.incr(endpoint_minute_key)
                except ValueError:
                    cache.set(endpoint_minute_key, 1, 120)
                
                try:
                    cache.incr(endpoint_hour_key)
                except ValueError:
                    cache.set(endpoint_hour_key, 1, 7200)
        except Exception:
            pass
    
    def _add_rate_limit_headers(self, response: HttpResponse, limit_info: dict[str, Any]) -> None:
        """Add standard rate limit headers to response."""
        response["X-RateLimit-Limit"] = str(limit_info["limit_minute"])
        response["X-RateLimit-Remaining"] = str(limit_info["remaining_minute"])
        response["X-RateLimit-Reset"] = str(limit_info["reset_minute"])
        
        response["X-RateLimit-Limit-Hour"] = str(limit_info["limit_hour"])
        response["X-RateLimit-Remaining-Hour"] = str(limit_info["remaining_hour"])
        response["X-RateLimit-Reset-Hour"] = str(limit_info["reset_hour"])
        
        if limit_info.get("retry_after"):
            response["Retry-After"] = str(limit_info["retry_after"])
    
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


class OptimizedRateLimitMiddleware(SlidingWindowRateLimiter):
    """
    Backward-compatible alias for SlidingWindowRateLimiter.
    Keeps existing middleware references working.
    """
    pass


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
