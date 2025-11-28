"""Keep-alive mechanism to prevent Render free tier spin-down.

This module starts a background thread that pings the health endpoint
every 14 minutes to keep the server active on Render's free plan.
"""

import os
import threading
import time
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)

PING_INTERVAL = 14 * 60  # 14 minutes in seconds


def get_app_url():
    """Get the application URL from environment or construct from Render."""
    # Check for explicit URL first
    app_url = os.environ.get("RENDER_EXTERNAL_URL")
    if app_url:
        return app_url

    # Check for Render service name
    render_service = os.environ.get("RENDER_SERVICE_NAME")
    if render_service:
        return f"https://{render_service}.onrender.com"

    # Fallback for local development
    return None


def ping_health():
    """Ping the health endpoint to keep the server alive."""
    app_url = get_app_url()
    if not app_url:
        return

    health_url = f"{app_url}/health/"

    try:
        req = urllib.request.Request(health_url, method="GET")
        req.add_header("User-Agent", "SmartInvoice-KeepAlive/1.0")

        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.getcode()
            logger.info(f"Keep-alive ping successful: {status}")
    except urllib.error.URLError as e:
        logger.warning(f"Keep-alive ping failed: {e}")
    except Exception as e:
        logger.error(f"Keep-alive error: {e}")


def keep_alive_worker():
    """Background worker that pings the server periodically."""
    logger.info("Keep-alive worker started")

    # Wait a bit before first ping to let server fully start
    time.sleep(60)

    while True:
        try:
            ping_health()
        except Exception as e:
            logger.error(f"Keep-alive worker error: {e}")

        time.sleep(PING_INTERVAL)


def start_keep_alive():
    """Start the keep-alive background thread.

    Only starts on Render (when RENDER environment variable is set).
    """
    # Only run on Render
    if not os.environ.get("RENDER"):
        logger.debug("Not on Render, skipping keep-alive")
        return

    # Check if already started
    for thread in threading.enumerate():
        if thread.name == "keep-alive-worker":
            logger.debug("Keep-alive worker already running")
            return

    # Start background thread
    thread = threading.Thread(target=keep_alive_worker, name="keep-alive-worker", daemon=True)
    thread.start()
    logger.info("Keep-alive background thread started")
