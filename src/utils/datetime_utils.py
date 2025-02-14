from datetime import datetime, timezone, time

def get_datetimes_for_date(date):
    day = datetime.fromisoformat(date)
    start = datetime.combine(day.date(), time.min, tzinfo=timezone.utc).isoformat()
    end = datetime.combine(day.date(), time.max, tzinfo=timezone.utc).isoformat()

    return start, end