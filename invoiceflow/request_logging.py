"""Request logging middleware for structured logging with request context."""

import uuid
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from invoiceflow.logging_config import set_request_context, clear_request_context


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that adds request context to logs and logs request/response info.
    Uses thread-local storage to propagate request_id, user_id, and ip_address
    to all log records during the request lifecycle.
    """
    
    def get_client_ip(self, request):
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    def process_request(self, request):
        """Process incoming request and set up logging context."""
        request.request_id = str(uuid.uuid4())[:8]
        request.start_time = time.perf_counter()
        
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id
        
        ip_address = self.get_client_ip(request)
        
        set_request_context(
            request_id=request.request_id,
            user_id=user_id,
            ip_address=ip_address
        )
        
        logger.info(f"Request started: {request.method} {request.path}")
        
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Update user_id after authentication middleware has run."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_request_context(
                request_id=getattr(request, 'request_id', None),
                user_id=request.user.id,
                ip_address=self.get_client_ip(request)
            )
        return None
    
    def process_response(self, request, response):
        """Log response info after request is processed."""
        duration = 0
        if hasattr(request, 'start_time'):
            duration = (time.perf_counter() - request.start_time) * 1000
        
        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        
        logger.log(
            log_level,
            f"Request completed: {request.method} {request.path} -> {response.status_code} ({duration:.2f}ms)"
        )
        
        response['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions with request context."""
        logger.exception(f"Request exception: {request.method} {request.path}")
        
        return None
