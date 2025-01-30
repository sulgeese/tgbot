import logging

from datetime import datetime

logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%d.%m.%Y %H:%M"


def format_datetime(date: datetime | None) -> str | None:
    if date is None:
        return None
    try:
        return date.strftime(DATETIME_FORMAT) if date else None
    except AttributeError as err:
        logger.warning("Failed to convert datetime to str: %s", err)

def parse_datetime(date_string: str) -> datetime | None:
    try:
        return datetime.strptime(date_string, DATETIME_FORMAT)
    except ValueError as err:
        logger.warning("Failed to convert str to datetime: %s", err)
