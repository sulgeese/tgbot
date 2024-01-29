from datetime import datetime


def datetime_to_str(date: datetime) -> str:
    return date.strftime("%d.%m.%Y %H:%M")


def str_to_datetime(date: str) -> datetime:
    return datetime.strptime(date, "%d.%m.%Y %H:%M")
