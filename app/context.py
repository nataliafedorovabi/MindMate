from typing import Optional

from app.db.db import Database
from app.services.scheduler import SchedulerService


_db: Optional[Database] = None
_scheduler: Optional[SchedulerService] = None


def set_context(db: Database, scheduler: SchedulerService) -> None:
    global _db, _scheduler
    _db = db
    _scheduler = scheduler


def get_db() -> Database:
    if _db is None:
        raise RuntimeError("Database is not initialized")
    return _db


def get_scheduler() -> SchedulerService:
    if _scheduler is None:
        raise RuntimeError("Scheduler is not initialized")
    return _scheduler


