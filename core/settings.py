from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    supergroup_id: int
    theme_id: int
    time_zone: str


@dataclass
class DataBase:
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int


@dataclass
class Settings:
    bots: Bots
    db: DataBase


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TOKEN"),
            admin_id=env.int("ADMIN_ID"),
            supergroup_id=env.int("SUPERGROUP_ID"),
            theme_id=env.int("THEME_ID"),
            time_zone=env.str("TIME_ZONE")
        ),
        db=DataBase(
            db_name=env.str("DB_NAME"),
            db_user=env.str("DB_USER"),
            db_password=env.str("DB_PASSWORD"),
            db_host=env.str("DB_HOST"),
            db_port=env.int("DB_PORT"),
        )
    )


settings = get_settings('input_test')
