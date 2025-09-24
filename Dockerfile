FROM python:3.12

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/static

EXPOSE 8000

COPY --chown=appuser:appuser start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
