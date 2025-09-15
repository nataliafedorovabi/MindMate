from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.db.db import Database
from app.keyboards.common import checklist_items_kb

router = Router(name="checklists")


@router.message(Command("checklists"))
async def cmd_checklists(message: Message) -> None:
    db: Database = message.bot.get("db")
    cls = await db.list_checklists()
    if not cls:
        await message.answer("Пока нет чек-листов")
        return
    # пока 1 чек-лист, покажем его
    code = cls[0]["code"]
    items = await db.list_checklist_items(code)
    triples = [(int(i["id"]), i["title"], int(i["done"])) for i in items]
    await message.answer("Отмечайте пункты:", reply_markup=checklist_items_kb(triples))


@router.callback_query(F.data.startswith("cli:"))
async def on_toggle(query: CallbackQuery) -> None:
    db: Database = query.message.bot.get("db")
    item_id = int(query.data.split(":", 1)[1])
    await db.toggle_checklist_item(query.from_user.id, item_id)
    # re-render current list (assume same checklist)
    cls = await db.list_checklists()
    if not cls:
        await query.answer()
        return
    code = cls[0]["code"]
    items = await db.list_checklist_items(code)
    triples = [(int(i["id"]), i["title"], int(i["done"])) for i in items]
    await query.message.edit_text("Отмечайте пункты:", reply_markup=checklist_items_kb(triples))
    await query.answer()


