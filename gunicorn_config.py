wsgi_app = "b2b_balance_manager.wsgi"
bind = "0.0.0.0:8000"

# The number of worker processes (typically, (2 x number of cores) + 1)
workers = 9
threads = 1

timeout = 60

# Log level
loglevel = "info"

