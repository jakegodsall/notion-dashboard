import datetime

def get_datetimes_for_date(date_input):
    if isinstance(date_input, str):
        day = datetime.fromisoformat(date_input)
    elif isinstance(date_input, datetime.date):
        day = datetime.datetime.combine(date_input, datetime.time.min, tzinfo=datetime.timezone.utc)
    else:
        raise TypeError("date_input must be a string in ISO format, a datetime object, or a date object")

    start = datetime.datetime.combine(day.date(), datetime.time.min, tzinfo=datetime.timezone.utc).isoformat()
    end = datetime.datetime.combine(day.date(), datetime.time.max, tzinfo=datetime.timezone.utc).isoformat()

    return start, end
