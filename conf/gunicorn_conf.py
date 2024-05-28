import multiprocessing
import os
from dotenv import load_dotenv
load_dotenv(os.getenv("PROJECT_DIR"))

command = f'{os.getenv("PROJECT_DIR")}/virtual-env/bin/gunicorn'
pythonpath = os.getenv('PROJECT_DIR')
bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = f'{os.getenv("DIR_COMMANDS_LOGS")}/stdout.log'
errorlog = f'{os.getenv("DIR_COMMANDS_LOGS")}/stderr.log'
timeout = 120
