from datetime import datetime


def datetime_to_str(date: datetime):
    return date.strftime("%d.%m.%Y %H:%M")


def str_to_datetime(date: str):
    return datetime.strptime(date, "%d.%m.%Y %H:%M")
