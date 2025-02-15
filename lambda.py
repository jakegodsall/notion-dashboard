import logging
import os
from pathlib import Path
from datetime import datetime
from src.integrations.lingq.fetcher import LingQFetcher
from src.integrations.whoop.fetcher import WhoopFetcher
from src.services.notion import NotionClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

# Configuration
notion_config_path = Path(__file__).resolve().parent / "src" / "config" / "notion.config.yml"

# Initialize services
lingq_service = LingQFetcher()
whoop_service = WhoopFetcher()
notion_client = NotionClient(str(notion_config_path))

def sync_lingq():
    logger.info("Running LingQ sync...")
    word_counts = lingq_service.get_daily_word_counts()
    for word_count in word_counts:
        notion_client.create_page("lingq", word_count)
    logger.info("LingQ sync completed.")

def sync_whoop_workout():
    logger.info("Running Whoop workout sync...")
    workouts = whoop_service.get_workouts_for_given_date(datetime.now().isoformat())
    transformed_workouts = whoop_service.transform_workouts(workouts)
    for workout in transformed_workouts:
        notion_client.create_page("whoop-workout", workout)
    logger.info("Whoop workout sync completed.")

def sync_whoop_sleep_and_recovery():
    logger.info("Running Whoop sleep and recovery sync...")
    sleep_and_recovery = whoop_service.get_sleep_and_recovery(datetime.now().isoformat())
    notion_client.create_page("whoop-sleep-and-recovery", sleep_and_recovery)
    logger.info("Whoop sleep and recovery sync completed.")

def mode_handler(mode):
    match mode:
        case 'lingq':
            sync_lingq()
        case 'whoop-workout':
            sync_whoop_workout()
        case 'whoop-sleep-and-recovery':
            sync_whoop_sleep_and_recovery()
        case _:
            raise RuntimeError("Provided mode does not match a defined mode.")

def lambda_handler(event, context):
    mode = os.getenv('MODE').lower()
    if mode is None:
        logger.error("Envrionment variable MODE is None.")
        return {"status": "error", "message": "Environment variable MODE is None."}
    
    logger.info(f"Starting the synchronization tasks in mode: {mode}")
    try:
        mode_handler(mode)
    except RuntimeError as e:
        logger.error(f"Mode error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "message": f"Unexpected error occurred: {str(e)}"}

    return {"status": "success"}
