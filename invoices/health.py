"""Health check endpoints for production monitoring."""

from django.http import JsonResponse
from django.db import connections
from django.conf import settings


def health_check(request):
    """Basic health check endpoint."""
    return JsonResponse({"status": "healthy", "version": "1.0.0", "debug": settings.DEBUG})


def readiness_check(request):
    """Readiness check - verifies database connectivity."""
    try:
        connections["default"].ensure_connection()
        return JsonResponse({"status": "ready", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "not_ready", "error": str(e)}, status=503)


def liveness_check(request):
    """Liveness check - verifies app is still running."""
    return JsonResponse(
        {
            "status": "alive",
            "timestamp": str(__import__("django.utils.timezone", fromlist=["now"]).now()),
        }
    )
