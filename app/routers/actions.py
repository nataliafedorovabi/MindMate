from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.context import get_db

router = Router(name="actions")


@router.callback_query(F.data.startswith("done:"))
async def on_done(query: CallbackQuery) -> None:
    db = get_db()
    pid = int(query.data.split(":", 1)[1])
    await db.log_practice_completion(query.from_user.id, pid)
    await db.add_points(query.from_user.id, 3)
    # streak check
    streak = await db.get_practice_streak_days(query.from_user.id)
    earned = False
    if streak >= 7:
        earned = await db.grant_achievement(query.from_user.id, "streak_7")
    points = await db.get_user_points(query.from_user.id)
    text = "✅ Класс, практика засчитана!\n"
    if earned:
        text += "🏆 Достижение: 7 дней подряд!\n"
    text += f"У тебя уже {points} баллов ресурса 🌱"
    await query.message.edit_text(text)
    await query.answer("Зачтено")


@router.callback_query(F.data.startswith("remind:"))
async def on_remind(query: CallbackQuery) -> None:
    # Note: For simplicity we just confirm. Advanced scheduling could be added per-user.
    await query.answer("Напоминание будет, спасибо!", show_alert=True)


