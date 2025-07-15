# dagster_project/assets.py
import os
from dagster import asset
from dagster_dbt import DbtCliResource, dbt_assets
from scripts.scraper import main as run_scraper
from scripts.loader import load_raw_data
from scripts.yolo_enricher import enrich_images
import asyncio

DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/app/dbt_project")
DBT_PROFILES_DIR = DBT_PROJECT_DIR # dbt recommends this to be in ~/.dbt

@asset(group_name="extraction", compute_kind="python")
def telegram_raw_files():
    """Scrapes new data from Telegram channels into the local data lake."""
    asyncio.run(run_scraper())

@asset(group_name="extraction", compute_kind="python", deps=[telegram_raw_files])
def loaded_raw_data_to_postgres():
    """Loads raw JSON files from the data lake into the PostgreSQL raw schema."""
    load_raw_data()

# Define the dbt assets
dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROFILES_DIR)

@dbt_assets(
    manifest=os.path.join(DBT_PROJECT_DIR, "target", "manifest.json"),
    deps=[loaded_raw_data_to_postgres]
)
def dbt_telegram_analytics(context, dbt: DbtCliResource):
    """Runs dbt build to create the star schema."""
    yield from dbt.cli(["build"], context=context).stream()

@asset(group_name="enrichment", compute_kind="python", deps=[dbt_telegram_analytics])
def yolo_enriched_data():
    """Runs YOLOv8 object detection on new images and loads results to the database."""
    enrich_images()

all_assets = [telegram_raw_files, loaded_raw_data_to_postgres, dbt_telegram_analytics, yolo_enriched_data]