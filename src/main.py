from pathlib import Path
from integrations.lingq.fetcher import LingQFetcher
from services.notion import NotionClient

if __name__ == "__main__":
    config_path = Path.cwd() / "src" / "config" / "notion.config.yml"
    lingq_client = LingQFetcher()
    word_counts = lingq_client.get_daily_word_counts()

    notion = NotionClient(config_path)

    for word_count in word_counts:
        notion.create_page( "lingq", word_count)