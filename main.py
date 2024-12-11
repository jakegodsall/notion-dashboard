import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from src.integrations.lingq.fetcher import LingQFetcher
from src.integrations.whoop.fetcher import WhoopFetcher
from src.services.notion import NotionClient

# Configuration
notion_config_path = Path(__file__).resolve().parent / "src" / "config" / "notion.config.yml"

# Initialize services
lingq_service = LingQFetcher()
whoop_service = WhoopFetcher()
notion_client = NotionClient(str(notion_config_path))


def sync_lingq():
    print(f"[{datetime.now()}] Running LingQ sync...")
    word_counts = lingq_service.get_daily_word_counts()
    for word_count in word_counts:
        notion_client.create_page("lingq", word_count)
    print(f"[{datetime.now()}] LingQ sync completed.")


def sync_whoop():
    print(f"[{datetime.now()}] Running WHOOP sync...")
    workouts = whoop_service.get_workouts_for_given_date((datetime.now() - timedelta(days=day)).isoformat())
    transformed_workouts = whoop_service.transform_workouts(workouts)
    for workout in transformed_workouts:
        notion_client.create_page("whoop", workout)
        print(f"Pushed {workout['sport']} activity to Notion.")
    print(f"[{datetime.now()}] WHOOP sync completed.")


if __name__ == "__main__":
    # sync_lingq()
    sync_whoop()
