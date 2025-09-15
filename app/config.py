import os
from dataclasses import dataclass
from typing import List


def _parse_admin_ids(value: str) -> List[int]:
    ids: List[int] = []
    for part in (value or "").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            continue
    return ids


@dataclass
class Settings:
    bot_token: str
    admin_ids: List[int]
    tz: str
    db_path: str
    daily_default_time: str


def load_settings() -> Settings:
    default_db = "/data/bot.db" if os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_ENVIRONMENT") else "bot.db"
    return Settings(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
        tz=os.getenv("TZ", "Europe/Moscow"),
        db_path=os.getenv("DB_PATH", default_db),
        daily_default_time=os.getenv("DAILY_DEFAULT_TIME", "09:00"),
    )


