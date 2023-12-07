from dataclasses import dataclass
from environs import Env


@dataclass
class Bots:
    token: str
    admin_id: int
    supergroup_id: int
    theme_id: int


@dataclass
class DataBase:
    drivername: str
    database: str
    username: str
    password: str
    host: str
    port: int


@dataclass
class Other:
    timezone: str


@dataclass
class Redis:
    port: int
    host: str


@dataclass
class Settings:
    bots: Bots
    db: DataBase
    other: Other
    redis: Redis


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            token=env.str("BOT_TOKEN"),
            admin_id=env.int("BOT_ADMIN_ID"),
            supergroup_id=env.int("BOT_SUPERGROUP_ID"),
            theme_id=env.int("BOT_THEME_ID"),
        ),
        db=DataBase(
            drivername=env.str("DB_DRIVERNAME"),
            database=env.str("DB_NAME"),
            username=env.str("DB_USERNAME"),
            password=env.str("DB_PASSWORD"),
            host=env.str("DB_HOST"),
            port=env.int("DB_PORT"),
        ),
        other=Other(
            timezone=env.str("OTHER_TIMEZONE"),
        ),
        redis=Redis(
            port=env.int("REDIS_PORT"),
            host=env.str("REDIS_HOST"),
        ),
    )


settings = get_settings('.env')
