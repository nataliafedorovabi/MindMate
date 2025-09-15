from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.db.db import Database

router = Router(name="stats")


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    db: Database = message.bot.get("db")
    points = await db.get_user_points(message.from_user.id)
    total_pr = await db.count_practice_completions(message.from_user.id)
    total_j = await db.count_journal_entries(message.from_user.id)
    streak = await db.get_practice_streak_days(message.from_user.id)
    ach = await db.list_user_achievements(message.from_user.id)
    achievements = ", ".join([a["title"] for a in ach]) if ach else "—"
    await message.answer(
        f"Очки: {points}\nВыполнено практик: {total_pr}\nЗаписей в дневнике: {total_j}\nСерия дней: {streak}\nДостижения: {achievements}"
    )


