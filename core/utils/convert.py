from datetime import datetime


def datetime_to_str(date: datetime) -> str:
    return date.strftime("%d.%m.%Y %H:%M")


def str_to_datetime(date: str) -> datetime:
    return datetime.strptime(date, "%d.%m.%Y %H:%M")


def py_to_sql(obj: int | str | None) -> str:
    if obj is None:
        return f'null'
    elif isinstance(obj, int):
        return f"{obj}"
    elif isinstance(obj, str):
        return f"'{obj}'"
