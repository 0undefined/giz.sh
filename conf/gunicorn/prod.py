# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "giz.wsgi:application"

# The granularity of Error log outputs
loglevel = "info"

# The number of worker processes for handling requests
workers = 2

# The socket to bind
bind = "0.0.0.0:8000"

# Write access and error info to stdout
accesslog = "-"
errorlog = "-"

# Redirect stdout/stderr to log file
capture_output = True

# PID file so you can easily fetch process ID
pidfile = "/var/run/gunicorn.pid"
