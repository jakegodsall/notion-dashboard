import os
from datetime import datetime, time, timezone
from dotenv import load_dotenv
from whoop import WhoopClient
from sport_map import sport_map

load_dotenv()


def get_sport_by_id(id):
    if id not in sport_map:
        raise KeyError(f"Sport Id {id} does not represent a sport")
    return sport_map.get(id)


class WhoopFetcher:
    def __init__(self):
        username = os.getenv('WHOOP_USERNAME')
        password = os.getenv('WHOOP_PASSWORD')

        if not username or not password:
            raise ValueError("Please set WHOOP_USERNAME and WHOOP_PASSWORD in the .env file.")

        self.client = WhoopClient(username, password)

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.__exit__(exc_type, exc_value, traceback)

    def get_profile(self):
        return self.client.get_profile()

    def get_workouts_for_given_date(self, iso_date):
        day = datetime.fromisoformat(iso_date)
        start = datetime.combine(day.date(), time.min, tzinfo=timezone.utc).isoformat()  # 00:00 UTC
        end = datetime.combine(day.date(), time.max, tzinfo=timezone.utc).isoformat()  # 23:59 UTC
        workouts = self.client.get_workout_collection(start, end)
        for workout in workouts:
            workout['sport'] = get_sport_by_id(workout['sport_id'])
        return workouts


def main():
    whoop_client = WhoopFetcher()

    todays_workouts = whoop_client.get_workouts_for_given_date('2024-11-26')
    print(todays_workouts)


if __name__ == '__main__':
    main()