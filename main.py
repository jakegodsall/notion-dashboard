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
logging.baseConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
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


def sync_whoop():
    """
    Sync Whoop data with Notion.
    """
    logger.info("Running Whoop sync...")
    try:
        workouts = whoop_service.get_workouts_for_given_date(datetime.now().isoformat())
        transformed_workouts = whoop_service.transform_workouts(workouts)
        for workout in transformed_workouts:
            notion_client.create_page("whoop", workout)
            logger.info(f"Pushed {workout['sport']} activity to Notion")            
        logger.info("Whoop sync completed.")
    except Exception as e:
        logger.error(f"Error during Whoop sync: {e}")


if __name__ == "__main__":
    # sync_lingq()
    sync_whoop()
