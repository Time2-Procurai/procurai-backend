FROM python:3.13.9-alpine3.21

WORKDIR /app
    
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev build-base openssl-dev

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY . .

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "procurai_backend.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3"]
