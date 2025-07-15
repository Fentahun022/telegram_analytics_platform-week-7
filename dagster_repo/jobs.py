
from dagster import schedule, define_asset_job

# Define a job that will materialize all assets
full_pipeline_job = define_asset_job(
    name="end_to_end_telegram_pipeline",
    selection="*", # Selects all assets
)

# Define a schedule to run the job daily at 1 AM UTC
@schedule(
    job=full_pipeline_job,
    cron_schedule="0 1 * * *",
    execution_timezone="UTC",
)
def daily_telegram_pipeline_schedule(context):
    """A schedule to run the full data pipeline daily."""
    return {}