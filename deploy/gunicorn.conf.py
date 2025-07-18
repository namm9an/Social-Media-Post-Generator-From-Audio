# Gunicorn configuration file for AI Social Media Post Generator
import multiprocessing

bind = "127.0.0.1:5000"
workers = max(int(multiprocessing.cpu_count() * 2 + 1), 4)
worker_class = "sync"
keepalive = 2
timeout = 300
max_requests = 1000
max_requests_jitter = 100
loglevel = "info"
accesslog = "/var/log/ai-social-generator/access.log"
errorlog = "/var/log/ai-social-generator/error.log"
