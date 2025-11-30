"""
InvoiceFlow Production Gunicorn Configuration
Official deployment for https://invoiceflow.com.ng
Rebuilt from scratch - Production-ready, secure, and optimized
"""

import multiprocessing
import os

PRODUCTION_DOMAIN = "invoiceflow.com.ng"
PRODUCTION_URL = f"https://{PRODUCTION_DOMAIN}"

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
backlog = 2048

workers = int(os.getenv("WEB_CONCURRENCY", min(multiprocessing.cpu_count() * 2 + 1, 17)))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
threads = int(os.getenv("GUNICORN_THREADS", 4))
worker_connections = 1000

max_requests = 1000
max_requests_jitter = 100
timeout = 60
graceful_timeout = 30
keepalive = 15

proc_name = "invoiceflow"

daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None
umask = 0
preload_app = True
reload = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

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

forwarded_allow_ips = "*"
proxy_allow_ips = "*"
proxy_protocol = False
secure_scheme_headers = {
    "X-FORWARDED-PROTO": "https",
    "X-FORWARDED-SSL": "on",
}


def on_starting(server):
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info("InvoiceFlow Gunicorn server starting...")
    logger.info(f"Production domain: {PRODUCTION_DOMAIN}")
    logger.info(f"Production URL: {PRODUCTION_URL}")
    logger.info(f"Workers: {workers}, Threads: {threads}")


def when_ready(server):
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info(f"InvoiceFlow server ready at {bind}")
    logger.info(f"Serving: {PRODUCTION_URL}")
    logger.info("All workers initialized and accepting connections")


def pre_fork(server, worker):
    pass


def post_fork(server, worker):
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.debug(f"Worker {worker.pid} spawned")


def post_worker_init(worker):
    pass


def worker_int(worker):
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info(f"Worker {worker.pid} received INT or QUIT signal")


def worker_abort(worker):
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.warning(f"Worker {worker.pid} aborted")


def child_exit(server, worker):
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info(f"Worker {worker.pid} exited")


def on_exit(server):
    import logging
    logger = logging.getLogger("gunicorn.error")
    logger.info("InvoiceFlow Gunicorn server shutting down...")
    logger.info(f"Production domain: {PRODUCTION_DOMAIN}")
