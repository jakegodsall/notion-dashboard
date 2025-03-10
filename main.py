import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
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

def sync_whoop_workouts(date=None):
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
            notion_client.update_or_create_page(workout, 'id', 'Whoop ID')
            logger.info(f"Pushed {workout['sport']} activity to Notion")            
        
    except Exception as e:
        logger.error(f"Error during Whoop workout sync: {e}")
    logger.info("Whoop workout sync completed.")

def sync_whoop_sleep_and_recovery(date=None, loop_until_first=False):
    notion_client = NotionClient(str(notion_config_path), "whoop-sleep-and-recovery")
    logger.info("Running Whoop sleep and recovery sync...")
    try:
        if date is None:
            date = datetime.now().date().isoformat()

        while True:
            logger.info(f"Processing data for date: {date}")

            sleep_and_recovery = whoop_service.get_sleep_and_recovery(date)
            logger.info(sleep_and_recovery)
            if sleep_and_recovery:
                notion_client.create_page("whoop-sleep-and-recovery", sleep_and_recovery)
                logger.info(f"Data for {date} synced successfully.")

            if not loop_until_first or not sleep_and_recovery:
                break

            date_obj = datetime.fromisoformat(date).date()
            date_obj -= timedelta(days=1)
            date = date_obj.isoformat()

        logger.info("Whoop sleep and recovery sync completed.")
    except Exception as e:
        logger.error(f"Error during Whoop sleep and recovery sync: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Notion dashboard CLI: Sync data from multiple sources with Notion database tables."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # TO IMPLEMENT (MAYBE)
    # lingq_parser = subparsers.add_parser("sync-lingq", help="Sync current known word counts with Notion.")
    
    whoop_workout_parser = subparsers.add_parser("sync-whoop-workouts", help="Sync Whoop workout activity with Notion.")
    whoop_workout_parser.add_argument(
        "--date",
        type=str,
        help="Date for syncing Whoop data (in ISO8601 format, e.g. '2025-01-01'). Defaults to today."
    )

    whoop_recovery_parser = subparsers.add_parser("sync-whoop-sleep", help="Sync Whoop sleep and recovery data with Notion.")
    whoop_recovery_parser.add_argument(
        "--date",
        type=str,
        help="Date for syncing Whoop data (in ISO8601 format, e.g. '2025-01-01'). Defaults to today."
    )
    whoop_recovery_parser.add_argument(
        "--loop-until-first",
        action="store_true",
        help="Loop through days, syncing data until the first day of available data is reached."
    )

    args = parser.parse_args()

    if args.command == 'sync-lingq':
        sync_lingq()
    if args.command == 'sync-whoop-workouts':
        sync_whoop_workouts(date=args.date)
    if args.command == 'sync-whoop-sleep':
        sync_whoop_sleep_and_recovery(date=args.date, loop_until_first=args.loop_until_first)

if __name__ == "__main__":
    main()
