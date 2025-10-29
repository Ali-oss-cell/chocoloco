# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Optimal: (2 x CPU cores) + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/django/ecomarce_choco/logs/gunicorn_access.log"
errorlog = "/home/django/ecomarce_choco/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "ecomarce_choco"

# Server mechanics
daemon = False
pidfile = "/home/django/ecomarce_choco/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed later)
# keyfile = None
# certfile = None

