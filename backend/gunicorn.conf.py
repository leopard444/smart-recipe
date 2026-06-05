"""Gunicorn configuration for production."""
import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv('WORKERS', '4'))
threads = int(os.getenv('THREADS', '2'))
worker_class = 'gthread'
timeout = 120
keepalive = 5

accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')

# Preload the app for faster worker startup
preload_app = True

# Maximum requests before worker restart (prevent memory leaks)
max_requests = 1000
max_requests_jitter = 100
