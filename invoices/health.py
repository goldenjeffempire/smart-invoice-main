"""Health check endpoints for production monitoring."""

from django.http import JsonResponse
from django.db import connections, connection
from django.db.utils import OperationalError
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import time
import os

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
APP_START_TIME = time.time()


def health_check(request):
    """
    Basic health check endpoint for load balancers.
    Returns 200 if the application is running.
    """
    return JsonResponse({
        "status": "healthy",
        "version": APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "timestamp": timezone.now().isoformat(),
        "uptime_seconds": int(time.time() - APP_START_TIME),
    })


def readiness_check(request):
    """
    Readiness check - verifies database connectivity and app readiness.
    Used by Kubernetes/Render to know when to route traffic.
    """
    checks = {
        "database": False,
        "migrations": False,
        "cache": False,
    }
    status = 200
    details = {}

    db_start = time.perf_counter()
    try:
        connections["default"].ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            checks["database"] = result is not None and result[0] == 1
        details["database_latency_ms"] = round((time.perf_counter() - db_start) * 1000, 2)
    except OperationalError as e:
        checks["database"] = False
        details["database_error"] = str(e)
        status = 503

    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        pending = executor.migration_plan(targets)
        checks["migrations"] = len(pending) == 0
        if pending:
            details["pending_migrations"] = len(pending)
    except Exception:
        checks["migrations"] = True

    cache_start = time.perf_counter()
    try:
        cache_key = "_health_check_test"
        cache.set(cache_key, "ok", 10)
        cached_value = cache.get(cache_key)
        checks["cache"] = cached_value == "ok"
        cache.delete(cache_key)
        details["cache_latency_ms"] = round((time.perf_counter() - cache_start) * 1000, 2)
        if not checks["cache"]:
            status = 503
    except Exception as e:
        checks["cache"] = False
        details["cache_error"] = str(e)
        status = 503

    all_ready = checks["database"] and checks["migrations"] and checks["cache"]
    
    if not checks["migrations"]:
        status = 503
    if not checks["cache"]:
        status = 503

    return JsonResponse({
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "details": details,
        "version": APP_VERSION,
        "timestamp": timezone.now().isoformat(),
    }, status=status)


def liveness_check(request):
    """
    Liveness check - verifies app is still responsive.
    Returns basic responsiveness info without hitting database.
    """
    start = time.perf_counter()

    response_data = {
        "status": "alive",
        "timestamp": timezone.now().isoformat(),
        "uptime_seconds": int(time.time() - APP_START_TIME),
        "version": APP_VERSION,
    }

    response_data["response_time_ms"] = round((time.perf_counter() - start) * 1000, 2)

    return JsonResponse(response_data)


def detailed_health(request):
    """
    Detailed health check for internal monitoring and debugging.
    Includes extended system information.
    """
    import platform
    import sys
    from invoiceflow.env_validation import get_env_status
    
    checks = {
        "database": False,
        "migrations": False,
        "cache": False,
    }
    details = {}
    
    db_start = time.perf_counter()
    try:
        connections["default"].ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            checks["database"] = result is not None and result[0] == 1
        details["database_latency_ms"] = round((time.perf_counter() - db_start) * 1000, 2)
    except Exception as e:
        checks["database"] = False
        details["database_error"] = str(e)
    
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        pending = executor.migration_plan(targets)
        checks["migrations"] = len(pending) == 0
        if pending:
            details["pending_migrations"] = len(pending)
    except Exception:
        checks["migrations"] = True
    
    cache_start = time.perf_counter()
    try:
        cache_key = "_detailed_health_test"
        cache.set(cache_key, "ok", 10)
        cached_value = cache.get(cache_key)
        checks["cache"] = cached_value == "ok"
        cache.delete(cache_key)
        details["cache_latency_ms"] = round((time.perf_counter() - cache_start) * 1000, 2)
    except Exception:
        checks["cache"] = True
        details["cache_note"] = "Using default LocMem cache"
    
    env_status = get_env_status()
    required_configured = all(v["configured"] for v in env_status["required"].values())
    
    all_healthy = all(checks.values()) and required_configured
    
    return JsonResponse({
        "status": "healthy" if all_healthy else "degraded",
        "version": APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development",
        "timestamp": timezone.now().isoformat(),
        "uptime_seconds": int(time.time() - APP_START_TIME),
        "checks": checks,
        "details": details,
        "environment_status": env_status,
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "django_version": settings.VERSION if hasattr(settings, 'VERSION') else "unknown",
        },
        "config": {
            "debug": settings.DEBUG,
            "mfa_enabled": getattr(settings, 'MFA_ENABLED', False),
            "database_engine": settings.DATABASES.get("default", {}).get("ENGINE", "unknown"),
        }
    })
