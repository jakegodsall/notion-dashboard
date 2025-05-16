import typer
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from src.integrations.lingq.fetcher import LingQFetcher
from src.integrations.whoop.fetcher import WhoopFetcher
from src.utils.logger import get_logger
from src.services.notion import NotionClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = get_logger()

# Configuration
notion_config_path = Path(__file__).resolve().parent / "src" / "config" / "notion.config.yml"

# Initialize services
lingq_service = LingQFetcher()
whoop_service = WhoopFetcher()

app = typer.Typer(help="Notion dashboard CLI: Sync data from multiple sources with Notion database tables.")
whoop_app = typer.Typer(help="Whoop-related commands")
app.add_typer(whoop_app, name="whoop")

def sync_lingq():
    """
    Sync LingQ data with Notion.
    """
    notion_client = NotionClient(str(notion_config_path), "lingq")
    logger.info("Running LingQ sync...")
    try:
        word_counts = lingq_service.get_daily_word_counts()
        for word_count in word_counts:
            notion_client.create_page("lingq", word_count)
        logger.info(f"[{datetime.now()}] LingQ sync completed.")
    except Exception as e:
        logger.error(f"Error during LingQ sync: {e}")
        raise typer.Exit(code=1)

@whoop_app.command("workouts")
def sync_whoop_workouts(
    date: Optional[str] = typer.Option(
        None,
        "--date", "-d",
        help="Date for syncing Whoop data (in ISO8601 format, e.g. '2024-03-20'). Defaults to today."
    )
):
    """Sync Whoop workout activity with Notion."""
    notion_client = NotionClient(str(notion_config_path), "whoop-workout")
    logger.info("Running Whoop workouts sync...")
    try:
        if date is None:
            date = datetime.now().date()
        else:
            date = datetime.strptime(date, "%Y-%m-%d").date()

        workouts = whoop_service.get_workouts_for_given_date(date)
        transformed_workouts = whoop_service.transform_workouts(workouts)
        for workout in transformed_workouts:
            notion_client.update_or_create_page(date.isoformat(), workout, 'id', 'Whoop ID')
            logger.info(f"Pushed {workout['sport']} activity to Notion")            
        
    except Exception as e:
        logger.error(f"Error during Whoop workout sync: {e}")
        raise typer.Exit(code=1)
    logger.info("Whoop workout sync completed.")

@whoop_app.command("sleep")
def sync_whoop_sleep_and_recovery(
    date: Optional[str] = typer.Option(
        None,
        "--date", "-d",
        help="Date for syncing Whoop data (in ISO8601 format, e.g. '2024-03-20'). Defaults to today."
    ),
    loop_until_first: bool = typer.Option(
        False,
        "--loop-until-first", "-l",
        help="Loop through days, syncing data until the first day of available data is reached."
    )
):
    """Sync Whoop sleep and recovery data with Notion."""
    notion_client = NotionClient(str(notion_config_path), "whoop-sleep-and-recovery")
    logger.info("Running Whoop sleep and recovery sync...")
    try:
        if date is None:
            date = datetime.now().date().isoformat()

        while True:
            logger.info(f"Processing data for date: {date}")

            sleep_and_recovery = whoop_service.get_sleep_and_recovery(date)
            if sleep_and_recovery:
                logger.info(f"Found sleep and recovery data for {date}")
                logger.debug(f"Sleep and recovery data: {sleep_and_recovery}")
                notion_client.update_or_create_page(date, sleep_and_recovery, "id", "Whoop ID", use_two_day_period=True)
                logger.info(f"Data for {date} synced successfully.")
            else:
                logger.info(f"No sleep and recovery data found for {date}")

            if not loop_until_first or not sleep_and_recovery:
                break

            date_obj = datetime.fromisoformat(date).date()
            date_obj -= timedelta(days=1)
            date = date_obj.isoformat()

        logger.info("Whoop sleep and recovery sync completed.")
    except Exception as e:
        logger.error(f"Error during Whoop sleep and recovery sync: {e}")
        raise typer.Exit(code=1)

@app.command()
def lingq():
    """Sync LingQ data with Notion."""
    sync_lingq()

if __name__ == "__main__":
    app()
