"""
InvoiceFlow Production Gunicorn Configuration
Clean, production-ready server setup
"""

import multiprocessing
import os

bind = "0.0.0.0:5000"
workers = int(os.getenv("WEB_CONCURRENCY", min(multiprocessing.cpu_count() * 2 + 1, 9)))
worker_class = "gthread"
threads = 4
timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
capture_output = True

forwarded_allow_ips = "*"
proxy_allow_ips = "*"
secure_scheme_headers = {
    "X-FORWARDED-PROTO": "https",
}
