from aiogram import Bot

from app.config import load_settings
from app.db.db import Database
from app.services.scheduler import SchedulerService


def attach_context(bot: Bot, db: Database, scheduler: SchedulerService) -> None:
    bot["db"] = db
    bot["scheduler"] = scheduler


