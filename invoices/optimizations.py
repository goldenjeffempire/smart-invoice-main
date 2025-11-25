"""
Database and query optimizations for Smart Invoice.
Reduces N+1 queries and improves performance.
"""
from typing import Any
from django.db.models import Prefetch, Count, Sum, Q, QuerySet
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Invoice  # type: ignore


class QueryOptimizer:
    """Optimize common database queries"""
    
    @staticmethod
    def get_user_invoices_optimized(user: Any) -> QuerySet:  # type: ignore
        """Get user invoices with optimal queries"""
        return Invoice.objects.filter(user=user).select_related('user').only(  # type: ignore
            'id', 'invoice_id', 'client_name', 'amount', 'currency', 'status', 'created_at'
        )
    
    @staticmethod
    def get_dashboard_stats(user: Any) -> dict:  # type: ignore
        """Get dashboard statistics efficiently"""
        cache_key = f'dashboard_stats_{user.id}'
        stats = cache.get(cache_key)
        
        if stats is None:
            invoices = Invoice.objects.filter(user=user).aggregate(  # type: ignore
                total_invoices=Count('id'),
                total_amount=Sum('amount'),
                paid_amount=Sum('amount', filter=Q(status='paid')),
                unpaid_amount=Sum('amount', filter=Q(status='pending'))
            )
            stats = invoices
            cache.set(cache_key, stats, 300)  # 5 minutes cache
        
        return stats
    
    @staticmethod
    def get_recent_invoices(user: Any, limit: int = 10) -> QuerySet:  # type: ignore
        """Get recent invoices efficiently"""
        return Invoice.objects.filter(user=user).order_by(  # type: ignore
            '-created_at'
        )[:limit].select_related('user').values(
            'id', 'invoice_id', 'client_name', 'amount', 'status'
        )


class CachingStrategy:
    """Comprehensive caching strategy"""
    
    # Cache keys and timeouts
    CACHE_TIMEOUTS = {
        'dashboard_stats': 300,      # 5 minutes
        'user_invoices': 600,        # 10 minutes
        'invoice_detail': 3600,      # 1 hour
        'analytics_data': 1800,      # 30 minutes
        'static_content': 86400,     # 1 day
    }
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all caches for user"""
        pattern = f'*_{user_id}'
        cache_keys = [
            f'dashboard_stats_{user_id}',
            f'user_invoices_{user_id}',
            f'analytics_data_{user_id}',
        ]
        for key in cache_keys:
            cache.delete(key)
    
    @staticmethod
    def get_cached_or_compute(cache_key, compute_func, timeout=300):
        """Get from cache or compute and cache"""
        result = cache.get(cache_key)
        if result is None:
            result = compute_func()
            cache.set(cache_key, result, timeout)
        return result


class IndexOptimization:
    """Database index optimization guide"""
    
    RECOMMENDED_INDEXES = [
        # User-related
        ('Invoice', ['user', 'created_at']),
        ('Invoice', ['user', 'status']),
        
        # Status and filtering
        ('Invoice', ['status', 'created_at']),
        ('Invoice', ['currency', 'amount']),
        
        # Search optimization
        ('Invoice', ['invoice_id']),
        ('Invoice', ['client_name']),
        
        # Date range queries
        ('Invoice', ['created_at']),
        ('Invoice', ['updated_at']),
    ]
    
    @staticmethod
    def create_migration_sql():
        """Generate migration SQL for indexes"""
        return """
        CREATE INDEX idx_invoice_user_created ON invoices_invoice(user_id, created_at);
        CREATE INDEX idx_invoice_user_status ON invoices_invoice(user_id, status);
        CREATE INDEX idx_invoice_status_created ON invoices_invoice(status, created_at);
        CREATE INDEX idx_invoice_id ON invoices_invoice(invoice_id);
        CREATE INDEX idx_invoice_client ON invoices_invoice(client_name);
        """


class ViewOptimization:
    """View-level optimizations"""
    
    @staticmethod
    def optimize_dashboard_view(view_func):
        """Decorator for optimized dashboard view"""
        def wrapper(request, *args, **kwargs):
            # Use select_related and prefetch_related
            invoices = QueryOptimizer.get_user_invoices_optimized(request.user)
            stats = QueryOptimizer.get_dashboard_stats(request.user)
            
            # Pass optimized querysets to view
            return view_func(request, invoices, stats, *args, **kwargs)
        return wrapper


class PerformanceMetrics:
    """Track performance metrics"""
    
    @staticmethod
    def log_query_count(func):
        """Decorator to log query counts"""
        def wrapper(*args, **kwargs):
            from django.db import connection
            from django.test.utils import CaptureQueriesContext
            
            with CaptureQueriesContext(connection) as context:
                result = func(*args, **kwargs)
                print(f"{func.__name__} executed {len(context)} queries")
            
            return result
        return wrapper
    
    @staticmethod
    def get_slow_queries(threshold_ms=100):
        """Get queries slower than threshold"""
        from django.db import connection
        slow_queries = [q for q in connection.queries if float(q['time']) > threshold_ms / 1000]
        return slow_queries
