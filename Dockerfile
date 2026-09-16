FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && pip install \
        "flask>=3.0.0" \
        "pymysql>=1.1.1" \
        "sqlalchemy>=2.0.43" \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Sao_Paulo
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

CMD ["python", "-u", "server.py"]
