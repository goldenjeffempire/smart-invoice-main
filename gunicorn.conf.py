"""
Gunicorn configuration file for Smart Invoice production deployment.
This configuration is optimized for Render and Replit environments.
"""

import multiprocessing
import os

# Bind
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")

# Worker processes
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
threads = 2

# Timeouts
timeout = 30
graceful_timeout = 30
keepalive = 5

# Request handling
max_requests = 1000
max_requests_jitter = 50

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "smart_invoice"

# Forwarded headers
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-FORWARDED-PROTO": "https"}

# Preload app for faster worker startup
preload_app = True

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    pass

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    pass

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    pass

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    pass

def pre_exec(server):
    """Called just before a new master process is forked."""
    pass

def child_exit(server, worker):
    """Called in the master process after a worker exits."""
    pass

def worker_exit(server, worker):
    """Called in the worker process just after a worker exits."""
    pass

def nworkers_changed(server, new_value, old_value):
    """Called whenever the number of workers is changed."""
    pass

def on_exit(server):
    """Called just before exiting Gunicorn."""
    pass
