import requests


class LingQFetcher:
    def __init__(self):
        self.api_key = os.getenv("LINGQ_API_KEY")
        self.base_url = "https://www.lingq.com/api/v2/"

    def fetch_languages(self, active = True):
        url = self.base_url + "languages"
        headers = {
            'Authorization': 'Token ' + self.api_key,
            'accept': 'application/json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data


if __name__ == '__main__':
    fetcher = LingQFetcher("MY KEY")
    languages = fetcher.fetch_languages()
    print(languages[0])