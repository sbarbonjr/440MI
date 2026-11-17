FROM python:3.12-slim

WORKDIR /app

COPY pasteurization/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY pasteurization/ ./

ENV PYTHONUNBUFFERED=1
EXPOSE 8001

CMD ["sh", "-c", "gunicorn --worker-class gevent --workers 1 --bind 0.0.0.0:${PORT:-8001} --timeout 0 serving:app"]
