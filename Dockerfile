FROM python:3.10-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# This CMD can be overridden by docker-compose
CMD ["dagster", "dev"]