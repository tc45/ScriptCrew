"""Gunicorn development configuration."""
import multiprocessing
import os

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "scriptcrew.wsgi:application"

# The granularity of Error log outputs
loglevel = "debug"

# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1

# The socket to bind
bind = "0.0.0.0:8000"

# Write access and error info to /var/log
accesslog = "/var/log/gunicorn/dev_access.log"
errorlog = "/var/log/gunicorn/dev_error.log"

# Redirect stdout/stderr to log file
capture_output = True

# PID file so you can easily stop/start the server
pidfile = "/var/run/gunicorn/dev.pid"

# Daemonize the Gunicorn process (detach & enter background)
daemon = False

# Environment variables
raw_env = [
    f"DJANGO_SETTINGS_MODULE=scriptcrew.settings.dev",
] 