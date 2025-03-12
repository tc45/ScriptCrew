"""Gunicorn production configuration."""
import multiprocessing
import os

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "scriptcrew.wsgi:application"

# The granularity of Error log outputs
loglevel = "info"

# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1

# The socket to bind
bind = "unix:/run/gunicorn/scriptcrew_prod.sock"

# Write access and error info to /var/log
accesslog = "/var/log/gunicorn/prod_access.log"
errorlog = "/var/log/gunicorn/prod_error.log"

# Redirect stdout/stderr to log file
capture_output = True

# PID file so you can easily stop/start the server
pidfile = "/var/run/gunicorn/prod.pid"

# Daemonize the Gunicorn process (detach & enter background)
daemon = True

# SSL configuration
keyfile = "/etc/ssl/private/scriptcrew.key"
certfile = "/etc/ssl/certs/scriptcrew.crt"

# Environment variables
raw_env = [
    f"DJANGO_SETTINGS_MODULE=scriptcrew.settings.prod",
]

# Timeout configuration
timeout = 120
keepalive = 5

# Security configurations
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 