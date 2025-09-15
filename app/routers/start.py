from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.context import get_db
from app.keyboards import main_menu_kb
from app.keyboards.common import practice_actions_kb

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    db = get_db()
    await db.upsert_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
    await message.answer(
        "Привет! Это тренажёр практик осознанности и устойчивости. Выберите раздел ниже.",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "📚 Библиотека")
async def open_library(message: Message) -> None:
    await message.answer("Открываю библиотеку… /library")


@router.message(F.text == "📝 Дневник")
async def open_journal(message: Message) -> None:
    await message.answer("Открываю дневник… /journal")


@router.message(F.text == "✅ Чек-листы")
async def open_checklists(message: Message) -> None:
    await message.answer("Открываю чек-листы… /checklists")


@router.message(F.text == "🎲 Практика дня")
async def random_practice(message: Message) -> None:
    db = get_db()
    row = await db.random_practice()
    if not row:
        await message.answer("Пока нет доступных практик.")
        return
    await message.answer(format_practice(row), reply_markup=practice_actions_kb(int(row["id"])) )


def format_practice(row) -> str:
    import json

    steps = []
    if row["steps_json"]:
        try:
            steps = json.loads(row["steps_json"]) or []
        except Exception:
            steps = []
    steps_text = "\n".join([f"• {s}" for s in steps]) if steps else ""
    desc = row["description"] or ""
    timer = row["timer_seconds"]
    timer_text = f"\n⏱️ Таймер: {timer} сек." if timer else ""
    return f"<b>{row['title']}</b>\n\n{desc}\n\n{steps_text}{timer_text}"


