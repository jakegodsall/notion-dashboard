import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()


class LingQFetcher:
    def __init__(self):
        self.api_key = os.getenv("LINGQ_API_KEY")
        self.base_url = "https://www.lingq.com/api/v2/"

    def make_api_request(self, endpoint):
        url = self.base_url + endpoint
        headers = {
            'Authorization': 'Token ' + self.api_key,
            'accept': 'application/json'
        }

        return requests.get(url, headers=headers)

    def fetch_languages(self, active=True):
        response = self.make_api_request("languages")

        if response.status_code == 200:
            data = response.json()
            return data

    def get_daily_word_counts(self):
        response = self.make_api_request("languages")

        if response.status_code == 200:
            data = response.json()
            active_languages = [language for language in data if language['knownWords'] > 0]
            return [{'date': datetime.now().isoformat(), 'language': language['title'],
                     'word-count': language['knownWords']} for language in active_languages]


if __name__ == '__main__':
    fetcher = LingQFetcher()
    languages = fetcher.get_daily_word_counts()
    print(languages)