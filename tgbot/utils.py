import logging

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped

logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%d.%m.%Y %H:%M"


def format_datetime(date: Mapped[datetime] | datetime | None) -> Optional[datetime]:
    if date is None:
        return None
    try:
        return date.strftime(DATETIME_FORMAT) if date else None
    except AttributeError as err:
        logger.debug("Failed to convert datetime to str: %s", err)

def parse_datetime(date_string: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_string, DATETIME_FORMAT)
    except ValueError as err:
        logger.debug("Failed to convert str to datetime: %s", err)
