from __future__ import annotations

import asyncio
import datetime as dt
from dataclasses import dataclass
from typing import Optional

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import Settings
from app.db.db import Database
from app.utils import format_practice


@dataclass
class SchedulerService:
    bot: Bot
    db: Database
    settings: Settings
    _scheduler: Optional[AsyncIOScheduler] = None

    async def start(self) -> None:
        if self._scheduler is not None:
            return
        self._scheduler = AsyncIOScheduler(timezone=self.settings.tz)
        # daily practice push (default time from env)
        hh, mm = (self.settings.daily_default_time or "09:00").split(":", 1)
        self._scheduler.add_job(self._send_daily_practice, CronTrigger(hour=int(hh), minute=int(mm)))
        self._scheduler.start()

    async def stop(self) -> None:
        if self._scheduler is not None:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None

    async def _send_daily_practice(self) -> None:
        rows = await self.db.list_users_for_daily()
        if not rows:
            return
        practice = await self.db.random_practice()
        if not practice:
            return
        text = "🎲 Практика дня\n\n" + format_practice(practice)
        today = dt.date.today().isoformat()
        for uid in rows:
            try:
                await self.bot.send_message(uid, text)
                await self.db.set_last_daily_sent(uid, today)
            except Exception:
                continue


