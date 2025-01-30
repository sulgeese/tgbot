import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import AnyStr, List, Optional, Tuple

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import GroupUsersModel, EventsModel
from db.redis_instance import redis
from utils import format_datetime, parse_datetime


async def add_user(): ...

async def delete_user(): ...

async def add_event(): ...

async def delete_event(): ...