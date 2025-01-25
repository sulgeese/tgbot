from datetime import datetime


def datetime_to_str(date: datetime | None) -> str | None:
    if not date:
        return None
    return date.strftime("%d.%m.%Y %H:%M")


def str_to_datetime(date: str) -> datetime | None:
    if not date:
        return None
    return datetime.strptime(date, "%d.%m.%Y %H:%M")
