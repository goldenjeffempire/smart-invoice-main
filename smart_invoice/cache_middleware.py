"""
Cache control middleware for optimal static asset caching.
"""
from django.utils.cache import add_never_cache_headers, patch_cache_control


class CacheControlMiddleware:
    """
    Adds appropriate cache headers to responses.
    
    - Static assets: Long-term caching (1 year)
    - HTML pages: No caching (always fresh)
    - API endpoints: Short-term caching
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Don't cache for authenticated users' dynamic content
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.path.startswith('/invoices/') or request.path.startswith('/dashboard'):
                add_never_cache_headers(response)
                return response
        
        # Long-term caching for static assets
        if request.path.startswith('/static/'):
            # 1 year cache for versioned static files
            patch_cache_control(
                response,
                public=True,
                max_age=31536000,  # 1 year
                immutable=True
            )
        
        # No caching for HTML pages (ensure fresh content)
        elif response.get('Content-Type', '').startswith('text/html'):
            add_never_cache_headers(response)
        
        # Short-term caching for API endpoints
        elif request.path.startswith('/api/'):
            patch_cache_control(
                response,
                public=True,
                max_age=300  # 5 minutes
            )
        
        return response
