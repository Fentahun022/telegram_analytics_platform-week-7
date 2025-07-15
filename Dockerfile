FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV DAGSTER_HOME "/opt/dagster/dagster_home"


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# This CMD can be overridden by docker-compose
CMD ["dagster", "dev"]