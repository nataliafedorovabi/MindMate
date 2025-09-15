from aiogram import Bot

from app.db.db import Database
from app.services.scheduler import SchedulerService
from app.context import set_context


def attach_context(bot: Bot, db: Database, scheduler: SchedulerService) -> None:
    # Bot no longer supports item assignment in aiogram >=3.7. Use global context.
    set_context(db, scheduler)


