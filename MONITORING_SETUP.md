
# Monitoring & Error Tracking Setup

## Error Tracking (Sentry)

### Installation
```bash
pip install sentry-sdk
```

### Configuration (settings.py)
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN', ''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=False,
    environment=os.environ.get('ENVIRONMENT', 'development'),
)
```

### Required Environment Variable
```bash
SENTRY_DSN=https://your-sentry-key@sentry.io/project-id
```

## Performance Monitoring

### Django Debug Toolbar (Development)
```bash
pip install django-debug-toolbar
```

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]
```

Add to `MIDDLEWARE`:
```python
MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
```

### Application Performance Monitoring (APM)

#### Health Check Endpoint
```python
# urls.py
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'database': check_database(),
    })

def check_database():
    """Check database connectivity"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return 'ok'
    except:
        return 'error'
```

### Logging Configuration

#### Structured Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## Metrics Collection

### Key Metrics to Monitor
1. **Request Latency**: P50, P95, P99
2. **Error Rate**: Errors per minute
3. **Database Query Time**: Avg, P95, P99
4. **Cache Hit Rate**: Hits vs misses
5. **Memory Usage**: Per worker
6. **CPU Usage**: Per worker
7. **Request Volume**: Requests per second

### Query Performance Monitoring
```python
# Track slow queries
from django.db import connection

def log_slow_queries(threshold_ms=100):
    for query in connection.queries:
        if float(query['time']) * 1000 > threshold_ms:
            logger.warning(f"Slow query: {query['sql'][:100]}... ({query['time']}s)")
```

## Alert Configuration

### Recommended Alerts
1. **Error Rate**: Alert if > 1% errors
2. **Response Time**: Alert if P95 > 2 seconds
3. **Database Connectivity**: Alert on connection loss
4. **Memory**: Alert if > 85% usage
5. **Disk**: Alert if > 90% usage
6. **Health Check**: Alert if endpoint returns error

### Render Dashboard Monitoring
- CPU Usage monitoring
- Memory usage tracking
- Active connections
- Deployment history
- Log streaming

## Custom Metrics (Optional: Prometheus)

### Installation
```bash
pip install prometheus-client
```

### Basic Setup
```python
from prometheus_client import Counter, Histogram, start_http_server

request_count = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')

# Middleware to track metrics
class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request_count.labels(method=request.method, endpoint=request.path).inc()
        
        with request_duration.time():
            response = self.get_response(request)
        
        return response
```

## Deployment Checks

### Pre-Deployment Verification
```bash
# Check database connectivity
python manage.py dbshell

# Run health check
curl https://your-domain.com/health/

# Verify static files
python manage.py collectstatic --dry-run

# Check configuration
python manage.py check --deploy
```

### Post-Deployment Verification
1. ✅ Health endpoint returns 200
2. ✅ Logs flowing to monitoring
3. ✅ Error tracking working
4. ✅ Performance metrics visible
5. ✅ Alerts configured and testing
6. ✅ Database backups running

## Troubleshooting

### High Memory Usage
- Check for memory leaks
- Monitor worker processes
- Reduce cache TTLs
- Profile with Django Debug Toolbar

### Slow Queries
- Check query logs
- Review N+1 queries
- Ensure indexes are created
- Use select_related/prefetch_related

### High Error Rate
- Check Sentry for error patterns
- Review recent deployments
- Check database connectivity
- Monitor external service integrations

## Maintenance Tasks

### Weekly
- Review error logs
- Check performance trends
- Monitor alert thresholds

### Monthly
- Database maintenance (VACUUM, ANALYZE)
- Review and optimize slow queries
- Update monitoring dashboards
- Test backup restoration

### Quarterly
- Security audit
- Performance optimization review
- Disaster recovery drill
- Capacity planning review
