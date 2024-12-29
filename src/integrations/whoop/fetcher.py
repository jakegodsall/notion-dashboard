import os
from datetime import datetime, time, timezone
from whoop import WhoopClient
from src.integrations.whoop.sport_map import sport_map


class WhoopFetcher:
    def __init__(self):
        username = os.environ.get('WHOOP_USERNAME')
        password = os.environ.get('WHOOP_PASSWORD')

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
        return workouts

    def transform_workouts(self, workouts):
        transformed_workouts = []

        for entry in workouts:
            # Parse start and end times to calculate duration in minutes
            start_time = datetime.fromisoformat(entry['start'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(entry['end'].replace('Z', '+00:00'))
            duration = round((end_time - start_time).total_seconds() / 60)
            distance = round(entry['score'].get('distance_meter', 0) / 1000, 1)
            calories = round((entry['score'].get('kilojoule', 0) * 0.239006))

            # Map sport_id to sport type
            sport_type = sport_map.get(entry.get('sport_id', 0), "Unknown")

            # Transform data
            transformed_entry = {
                "title": sport_type,
                "date": start_time.isoformat(),
                "duration": duration,
                "distance": distance,
                "sport": sport_type,
                "calories": calories,
                "hr_avg": entry['score'].get('average_heart_rate', 0),
                "hr_max": entry['score'].get('max_heart_rate', 0),
            }

            transformed_workouts.append(transformed_entry)

        return transformed_workouts


def main():
    whoop_client = WhoopFetcher()

    todays_workouts = whoop_client.get_workouts_for_given_date(datetime.now().isoformat())
    print(todays_workouts)
    todays_workouts_transformed = whoop_client.transform_workouts(todays_workouts)
    print(todays_workouts_transformed)


if __name__ == '__main__':
    main()