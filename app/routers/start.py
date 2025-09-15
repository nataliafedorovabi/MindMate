from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.context import get_db
from app.keyboards import main_menu_kb
from app.keyboards.common import practice_actions_kb
from app.utils import format_practice

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


    


