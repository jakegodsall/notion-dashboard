import os
from datetime import datetime
from whoop import WhoopClient
from src.integrations.whoop.sport_map import sport_map

from src.utils.datetime_utils import get_datetimes_for_date
from src.utils.logger import get_logger

# Set up logging
logger = get_logger()

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
    
    def get_sleep(self, date):
        start, end = get_datetimes_for_date(date)
        sleep_collection = self.client.get_sleep_collection(start, end)
        return sleep_collection[0]
    
    def get_recovery(self, date):
        start, end = get_datetimes_for_date(date)
        recovery_data = self.client.get_recovery_collection(start, end)
        return recovery_data[0]
    
    from datetime import datetime, timedelta

    def get_sleep_and_recovery(self, date):
        try:
            sleep_data = self.get_sleep(date)
            recovery_data = self.get_recovery(date)
            result = {}

            try:
                # Parse sleep end time to adjust the date
                sleep_end_time = sleep_data["end"]
                sleep_end_datetime = datetime.fromisoformat(sleep_end_time)

                # Calculate the "effective date" based on sleep end time
                effective_date = sleep_end_datetime.date()

                result["id"] = sleep_data["id"]
                result["name"] = effective_date.isoformat()
                result["date"] = effective_date.isoformat()
                result["sleep_start_time"] = sleep_data["start"]
                result["sleep_end_time"] = sleep_end_time

                if sleep_data.get("score_state") == "SCORED":
                    result["sleep_performance_percentage"] = sleep_data["score"]["sleep_performance_percentage"]
                    result["sleep_consistency_percentage"] = sleep_data["score"]["sleep_consistency_percentage"]
                    result["sleep_efficiency_percentage"] = sleep_data["score"]["sleep_efficiency_percentage"]
                else:
                    result["sleep_performance_percentage"] = None
                    result["sleep_consistency_percentage"] = None
                    result["sleep_efficiency_percentage"] = None
            except KeyError as e:
                logger.error(f"Missing key in sleep data for date {date}: {e}")
                raise ValueError(f"Incomplete sleep data for date {date}")

            try:
                result["recovery_score"] = recovery_data["score"]["recovery_score"]
                result["resting_heart_rate"] = recovery_data["score"]["resting_heart_rate"]
            except KeyError as e:
                logger.error(f"Missing key in recovery data for date {date}: {e}")
                raise ValueError(f"Incomplete recovery data for date {date}")

            return result

        except Exception as e:
            logger.error(f"Error in get_sleep_and_recovery for date {date}: {e}")
            return None

    def get_workouts_for_given_date(self, date):
        start, end = get_datetimes_for_date(date)
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
                "id": entry["id"],
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
    logger.info(todays_workouts)
    todays_workouts_transformed = whoop_client.transform_workouts(todays_workouts)
    logger.info(todays_workouts_transformed)


if __name__ == '__main__':
    main()