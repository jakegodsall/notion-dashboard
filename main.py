import argparse
import logging
from datetime import datetime
from pathlib import Path
from src.integrations.lingq.fetcher import LingQFetcher
from src.integrations.whoop.fetcher import WhoopFetcher
from src.services.notion import NotionClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
notion_config_path = Path(__file__).resolve().parent / "src" / "config" / "notion.config.yml"

# Initialize services
lingq_service = LingQFetcher()
whoop_service = WhoopFetcher()
notion_client = NotionClient(str(notion_config_path))

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

def sync_lingq():
    """
    Sync LingQ data with Notion.
    """
    logger.info("Running LingQ sync...")
    try:
        word_counts = lingq_service.get_daily_word_counts()
        for word_count in word_counts:
            notion_client.create_page("lingq", word_count)
        logger.info(f"[{datetime.now()}] LingQ sync completed.")
    except Exception as e:
        logger.error(f"Error during LingQ sync: {e}")

def sync_whoop_workouts(date=None):
    logger.info("Runing Whoop workouts sync...")
    try:
        if date is None:
            date = datetime.now().date()
        else:
            date = datetime.strptime(date, "%Y-%m-%d").date()

        workouts = whoop_service.get_workouts_for_given_date(date)
        transformed_workouts = whoop_service.transform_workouts(workouts)
        for workout in transformed_workouts:
            notion_client.create_page("whoop-exercise", workout)
            logger.info(f"Pushed {workout['sport']} activity to Notion")            
    except Exception as e:
        logger.error(f"Error during Whoop workout sync: {e}")
    logger.info("Whoop workout sync completed.")

def sync_whoop_sleep_and_recovery(date=None):
    logger.info("Running Whoop sleep and recovery sync...")
    try:
        if date is None:
            date = datetime.now().date().isoformat()

        sleep_and_recovery = whoop_service.get_sleep_and_recovery(date)
        notion_client.create_page("whoop-sleep-and-recovery", sleep_and_recovery)
    except Exception as e:
        logger.error(f"Error during Whoop sleep and recovery sync: {e}")
    logger.info("Whoop sleep and recovery sync completed.")

def main():
    parser = argparse.ArgumentParser(
        description="Notion dashboard CLI: Sync data from multiple sources with Notion database tables."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    lingq_parser = subparsers.add_parser("sync-lingq", help="Sync current known word counts with Notion.")
    
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

    args = parser.parse_args()

    if args.command == 'sync-lingq':
        sync_lingq()
    if args.command == 'sync-whoop-workouts':
        sync_whoop_workouts(date=args.date)
    if args.command == 'sync-whoop-sleep':
        sync_whoop_sleep_and_recovery(date=args.date)


if __name__ == "__main__":
    main()
