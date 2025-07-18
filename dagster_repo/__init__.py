# dagster_project/__init__.py
from dagster import Definitions, load_assets_from_modules
from . import assets, schedules

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    schedules=[schedules.daily_telegram_pipeline_schedule],
)