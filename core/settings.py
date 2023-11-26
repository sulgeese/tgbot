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
class Settings:
    bots: Bots


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
        )
    )


settings = get_settings('input')
