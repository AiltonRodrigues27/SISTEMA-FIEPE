from datetime import datetime, timedelta, timezone

BRASILIA = timezone(timedelta(hours=-3))


def format_api_datetime(moment: datetime) -> str:
    return moment.astimezone(BRASILIA).strftime("%Y-%m-%dT%H:%M:%S-03:00")
