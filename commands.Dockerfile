FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/log/commands && chmod -R 777 /var/log/commands

RUN mkdir -p /app/public/files && chmod -R 777 /app/public/files

COPY . .

EXPOSE 8000

CMD ["python3", "-m", "gunicorn", "-c", "/app/conf/gunicorn_conf.py", "network_automation.wsgi"]