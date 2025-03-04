import logging

from datetime import datetime
from typing import Optional

from dateutil import parser

logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%d.%m.%Y %H:%M"


def format_datetime(date: Optional[datetime]) -> Optional[str]:
    if date is None:
        return None
    try:
        return date.strftime(DATETIME_FORMAT) if date else None
    except AttributeError as err:
        logger.debug("Failed to convert datetime to str: %s", err)
        return None

def parse_datetime(date: Optional[str]) -> Optional[datetime]:
    if date is None:
        return None
    try:
        return parser.parse(date, dayfirst=True)
    except ValueError as err:
        logger.debug("Failed to convert str to datetime: %s", err)
        return None

def normalize_datetime(date: Optional[str]) -> Optional[str]:
    return format_datetime(parse_datetime(date))
