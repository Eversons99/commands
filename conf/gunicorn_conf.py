import multiprocessing

command = '/home/nmultifibra/commands/virtual-env/bin/gunicorn'
pythonpath = '/home/nmultifibra/commands'
bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/var/log/commands/stdout.log'
errorlog = '/var/log/commands/stderr.log'
timeout = 120
