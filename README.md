# Shipping a Data Product: Telegram Analytical Platform

A robust, end-to-end data pipeline that ingests data from public Ethiopian medical Telegram channels, enriches it, and prepares it for analysis.

---

## 🚀 Overview & Business Need

This platform was built for Kara Solutions to generate insights about Ethiopian medical businesses. It answers key questions like:
- What are the most frequently mentioned medical products?
- How does product availability vary across channels?
- What are the trends in posting volume?

To achieve this, the project implements a modern ELT framework using Docker, Telethon, PostgreSQL, dbt, and Dagster.

## ✨ Key Features

- **Automated Scraping:** Collects messages and images from specified Telegram channels.
- **Layered Data Warehouse:** Builds a reliable data warehouse in PostgreSQL with a raw data lake and a clean analytical layer.
- **Dimensional Modeling:** Transforms raw data into a Star Schema optimized for BI tools and analysis.
- **Data Testing:** Uses dbt to ensure data quality and integrity.
- **Reproducible Environment:** Fully containerized with Docker for easy setup and consistent runs.

## 🛠️ Tech Stack & Architecture

- **Orchestration:** Dagster
- **Containerization:** Docker & Docker Compose
- **Data Extraction:** Python & Telethon
- **Data Warehouse:** PostgreSQL
- **Data Transformation:** dbt
- **Data Lake:** Local Filesystem (JSON & Images)


    ⚙️ Setup & Installation
  git clone https://github.com/Fentahun022/telegram_analytics_platform-week-7.git
 cd telegram_analytics_platform-week-7

  # Build and Run the Docker Containers
  docker-compose up --build -d

  🏃 How to Run the Pipeline (Tasks 1 & 2)
The pipeline steps are executed as commands inside the running app container.
Step 1: Scrape Telegram Data (Extract)
docker-compose exec app python scripts/scraper.py
 step 2. Load Raw Data into PostgreSQL (Load)
 docker-compose exec app python scripts/loader.py

Step 3: Transform Data with dbt (Transform)
docker-compose exec app dbt build --project-dir dbt_project