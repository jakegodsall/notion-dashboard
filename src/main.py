from pathlib import Path
from datetime import datetime
from src.integrations.lingq.fetcher import LingQFetcher
from src.integrations.whoop.fetcher import WhoopFetcher
from src.services.notion import NotionClient


def upload_lingq():
    lingq_client = LingQFetcher()
    word_counts = lingq_client.get_daily_word_counts()

    for word_count in word_counts:
        notion.create_page("lingq", word_count)


def upload_whoop():
    whoop_client = WhoopFetcher()
    workouts = whoop_client.get_workouts_for_given_date(datetime.now().isoformat())
    transformed_workouts = whoop_client.transform_workouts(workouts)
    print(transformed_workouts)

    for workout in transformed_workouts:
        notion.create_page("whoop", workout)


if __name__ == "__main__":
    config_path = Path.cwd() / "src" / "config" / "notion.config.yml"
    notion = NotionClient(config_path)

    # upload_lingq()
    upload_whoop()