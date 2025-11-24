"""
Advanced middleware for production: request logging, rate limiting, compression.
"""
import logging
import json
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from functools import wraps

logger = logging.getLogger(__name__)


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """Log all HTTP requests and responses with performance metrics."""
    
    def process_request(self, request):
        request._start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Don't log health checks (too noisy)
            if '/health/' not in request.path:
                log_data = {
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'user': request.user.username if request.user.is_authenticated else 'anonymous',
                    'ip': self.get_client_ip(request),
                }
                
                # Log slow requests at WARNING level
                if duration > 1.0:
                    logger.warning(f"Slow Request: {json.dumps(log_data)}")
                else:
                    logger.info(f"Request: {json.dumps(log_data)}")
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class RateLimitingMiddleware(MiddlewareMixin):
    """Rate limit by IP address."""
    
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    
    def process_request(self, request):
        # Skip rate limiting for health checks
        if '/health/' in request.path:
            return None
        
        client_ip = RequestResponseLoggingMiddleware.get_client_ip(request)
        cache_key = f'rate_limit:{client_ip}'
        
        request_count = cache.get(cache_key, 0)
        
        if request_count >= self.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )
        
        cache.set(cache_key, request_count + 1, self.RATE_LIMIT_WINDOW)
        return None


# Security headers are now handled by smart_invoice.security_middleware.SecurityHeadersMiddleware
# This duplicate middleware class has been removed to clean up codebase


def rate_limit_decorator(requests_per_hour=60):
    """Decorator for rate limiting specific views."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            client_ip = RequestResponseLoggingMiddleware.get_client_ip(request)
            cache_key = f'view_rate_limit:{view_func.__name__}:{client_ip}'
            
            request_count = cache.get(cache_key, 0)
            
            if request_count >= requests_per_hour:
                return JsonResponse(
                    {'error': 'Rate limit exceeded for this operation.'},
                    status=429
                )
            
            cache.set(cache_key, request_count + 1, 3600)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
