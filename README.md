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
Step 4: Run the Data Pipeline

Execute the following commands in order from the project root directory.

1.  **Install Python Dependencies (in a virtual environment):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  
    pip install -r requirements.txt
    ```

2.  **Run the Scraper (Task 1):**
    This script will connect to Telegram and populate the `./data/raw/` directory. The first time, it will ask for your phone number and a login code.
    ```bash
    python scripts/scrape_telegram.py
    ```

3.  **Load Raw Data into the Warehouse:**
    This script loads the new JSON files into the `raw` schema in PostgreSQL.
    ```bash
    python scripts/load_raw_to_postgres.py
    ```

4.  **Install dbt Dependencies:**
    This downloads the `dbt-utils` package required by our models.
    ```bash
    dbt deps --project-dir ./dbt_project
    ```

5.  **Run the dbt Transformations (Task 2):**
    This is the core transformation step. It builds all the staging and mart models.
    ```bash
    dbt run --project-dir ./dbt_project
    ```

6.  **Test the Data:**
    Run the data quality tests defined in the `dbt` project to ensure integrity.
    ```bash
    dbt test --project-dir ./dbt_project
    ```

🎉 **Success!** If all commands complete without error, you have successfully built the data warehouse. You can connect to the PostgreSQL database on port `5433` to explore the tables in the `marts` schema.

---

## 4. Project Structure Explained

A clear separation of concerns is used to keep the project organized and scalable.

```
.
├── api/              # (Future) FastAPI application
├── data/             # Raw data lake (ignored by Git)
├── dbt_project/      # All dbt models, tests, and configuration
│   ├── models/
│   │   ├── staging/  # Cleans and prepares raw data
│   │   └── marts/    # Final analytics-ready star schema
├── scripts/          # Standalone Python scripts (scraping, loading)
├── .env              # Local secrets (never commit)
├── .env.example      # Template for environment variables
├── docker-compose.yml# Orchestrates all services
└── README.md         # This documentation file