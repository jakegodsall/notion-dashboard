import os
import sys
from pathlib import Path
from datetime import datetime
from src.integrations.lingq.fetcher import LingQFetcher
from src.integrations.whoop.fetcher import WhoopFetcher
from src.services.notion import NotionClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Configuration
notion_config_path = Path(__file__).resolve().parent / "src" / "config" / "notion.config.yml"

# Initialize services
lingq_service = LingQFetcher()
whoop_service = WhoopFetcher()
notion_client = NotionClient(notion_config_path)

# Tasks
def sync_lingq():
    print(f"[{datetime.now()}] Running LingQ sync...")
    word_counts = lingq_service.get_daily_word_counts()
    for word_count in word_counts:
        notion_client.create_page("lingq", word_count)
    print(f"[{datetime.now()}] LingQ sync completed.")

def sync_whoop():
    print(f"[{datetime.now()}] Running WHOOP sync...")
    workouts = whoop_service.get_workouts_for_given_date(datetime.now().isoformat())
    transformed_workouts = whoop_service.transform_workouts(workouts)
    for workout in transformed_workouts:
        notion_client.create_page("whoop", workout)
    print(f"[{datetime.now()}] WHOOP sync completed.")

# Run both tasks
sync_lingq()
sync_whoop()
