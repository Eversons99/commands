FROM python:3.11

WORKDIR /app

COPY ws-requirements.txt /app/

RUN pip install --no-cache-dir -r ws-requirements.txt

COPY websocket_logs/ /app/websocket_logs/

COPY maintenance_core_app/ /app/maintenance_core_app/

COPY websocket_server/ /app/websocket_server/

EXPOSE 5678

CMD ["python3", "/app/websocket_server/app.py"]