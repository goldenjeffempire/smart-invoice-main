"""
InvoiceFlow Production Gunicorn Configuration
Optimized for https://invoiceflow.com.ng deployment on Render/Replit
Rebuilt from scratch for maximum performance and reliability
"""

import multiprocessing
import os

# =============================================================================
# SERVER SOCKET
# =============================================================================
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
backlog = 2048

# =============================================================================
# WORKER PROCESSES
# =============================================================================
workers = int(os.getenv("WEB_CONCURRENCY", min(multiprocessing.cpu_count() * 2 + 1, 17)))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
threads = int(os.getenv("GUNICORN_THREADS", 4))
worker_connections = 1000

# =============================================================================
# WORKER LIFECYCLE
# =============================================================================
max_requests = 1000
max_requests_jitter = 100
timeout = 60
graceful_timeout = 30
keepalive = 15

# =============================================================================
# PROCESS NAMING
# =============================================================================
proc_name = "invoiceflow"

# =============================================================================
# SERVER MECHANICS
# =============================================================================
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None
umask = 0
preload_app = True
reload = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"

# =============================================================================
# SECURITY LIMITS
# =============================================================================
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# =============================================================================
# LOGGING
# =============================================================================
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
capture_output = True
enable_stdio_inheritance = True

access_log_format = (
    '{"remote_ip": "%(h)s", "request_id": "%(r)s", '
    '"response_code": %(s)s, "request_method": "%(m)s", '
    '"request_path": "%(U)s", "request_querystring": "%(q)s", '
    '"request_time_ms": %(D)s, "response_length": %(B)s, '
    '"user_agent": "%(a)s"}'
)

# =============================================================================
# PROXY HEADERS (Render/Cloudflare/Nginx)
# =============================================================================
forwarded_allow_ips = "*"
proxy_allow_ips = "*"
proxy_protocol = False
secure_scheme_headers = {
    "X-FORWARDED-PROTO": "https",
    "X-FORWARDED-SSL": "on",
}

# =============================================================================
# SERVER HOOKS
# =============================================================================

def on_starting(server):
    """Called just before the master process is initialized."""
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info("InvoiceFlow Gunicorn server starting...")
    logger.info(f"Production domain: invoiceflow.com.ng")
    logger.info(f"Workers: {workers}, Threads: {threads}")


def when_ready(server):
    """Called just after the server is started."""
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info(f"InvoiceFlow server ready at {bind}")
    logger.info("All workers initialized and accepting connections")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.debug(f"Worker {worker.pid} spawned")


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass


def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info(f"Worker {worker.pid} received INT or QUIT signal")


def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.warning(f"Worker {worker.pid} aborted")


def child_exit(server, worker):
    """Called in the master process after a worker exits."""
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info(f"Worker {worker.pid} exited")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info("InvoiceFlow Gunicorn server shutting down...")
