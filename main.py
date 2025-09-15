import asyncio
import logging
import os
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from app.config import load_settings
from app.db.db import Database
from app.routers.start import router as start_router
from app.routers.library import router as library_router
from app.routers.journal import router as journal_router
from app.routers.checklists import router as checklists_router
from app.routers.actions import router as actions_router
from app.routers.stats import router as stats_router
from app.routers.minigame import router as minigame_router
from app.routers.state_strange import router as state_strange_router
from app.services.scheduler import SchedulerService
from app.bootstrap import attach_context


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Запуск и меню"),
        BotCommand(command="library", description="Библиотека практик"),
        BotCommand(command="journal", description="Дневник состояния"),
        BotCommand(command="checklists", description="Чек-листы"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(bot: Bot, db: Database, scheduler: SchedulerService) -> None:
    await set_commands(bot)
    await db.init()
    await scheduler.start()


async def on_shutdown(scheduler: SchedulerService, db: Database) -> None:
    await scheduler.stop()
    await db.close()


async def main() -> None:
    load_dotenv()  # load .env if present
    settings = load_settings()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    if not settings.bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    db = Database(db_path=settings.db_path)
    scheduler = SchedulerService(bot=bot, db=db, settings=settings)
    attach_context(bot, db, scheduler)

    dp.include_router(start_router)
    dp.include_router(library_router)
    dp.include_router(journal_router)
    dp.include_router(checklists_router)
    dp.include_router(actions_router)
    dp.include_router(stats_router)
    dp.include_router(minigame_router)
    dp.include_router(state_strange_router)

    # Startup and shutdown hooks
    async def _startup() -> None:
        await on_startup(bot, db, scheduler)

    async def _shutdown() -> None:
        await on_shutdown(scheduler, db)

    dp.startup.register(_startup)
    dp.shutdown.register(_shutdown)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        with suppress(Exception):
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())


