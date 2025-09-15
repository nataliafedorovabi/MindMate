from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.context import get_db
from app.keyboards.common import categories_kb, practices_kb, practice_actions_kb
from app.routers.start import format_practice

router = Router(name="library")


@router.message(Command("library"))
async def cmd_library(message: Message) -> None:
    db = get_db()
    cats = await db.list_categories()
    data = [(c["code"], c["title"]) for c in cats]
    await message.answer("Выберите категорию:", reply_markup=categories_kb(data))


@router.callback_query(F.data.startswith("cat:"))
async def on_category(query: CallbackQuery) -> None:
    db = get_db()
    code = query.data.split(":", 1)[1]
    practices = await db.list_practices_by_category(code)
    data = [(int(p["id"]), p["title"]) for p in practices]
    if not data:
        await query.message.edit_text("В этой категории пока нет практик")
    else:
        await query.message.edit_text("Выберите практику:", reply_markup=practices_kb(data))
    await query.answer()


@router.callback_query(F.data.startswith("pr:"))
async def on_practice(query: CallbackQuery) -> None:
    db = get_db()
    pid = int(query.data.split(":", 1)[1])
    row = await db.get_practice(pid)
    if not row:
        await query.answer("Не найдено", show_alert=True)
        return
    await query.message.edit_text(format_practice(row), reply_markup=practice_actions_kb(pid))
    await query.answer()


