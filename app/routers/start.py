from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.context import get_db
from app.keyboards import main_menu_kb
from app.keyboards.common import practice_actions_kb, state_select_kb
from app.utils import format_practice

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    db = get_db()
    await db.upsert_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
    await message.answer(
        "Привет 👋 Я помогу сделать паузу и вернуться в ресурс.\nКак тебе сейчас?",
        reply_markup=state_select_kb(),
    )


@router.message(F.text == "📚 Библиотека")
async def open_library(message: Message) -> None:
    await message.answer("Открываю библиотеку… /library")


@router.message(F.text == "🌿 Я здесь")
async def open_journal(message: Message) -> None:
    await message.answer("Как тебе сейчас?", reply_markup=state_select_kb())


@router.message(F.text == "✅ Чек-листы")
async def open_checklists(message: Message) -> None:
    await message.answer("Открываю чек-листы… /checklists")


@router.message(F.text == "🌅 Практика дня")
async def random_practice(message: Message) -> None:
    db = get_db()
    row = await db.random_practice()
    if not row:
        await message.answer("Пока нет доступных практик.")
        return
    await message.answer("🌅 Практика дня\n\n" + format_practice(row), reply_markup=practice_actions_kb(int(row["id"])) )


@router.callback_query(F.data.startswith("st:"))
async def on_state_select(callback: 'CallbackQuery') -> None:
    from aiogram.types import CallbackQuery
    cb: CallbackQuery = callback
    code = cb.data.split(":",1)[1]
    # Simple mapping from state to preferred category
    mapping = {
        "angry": "attention",
        "confused": "mind",
        "strange": None,  # use custom guided flow
        "anxious": "attention",
        "sad": "emotion",
        "tired": "body",
        "calm": None,
    }
    db = get_db()
    pref = mapping.get(code)
    if code == "strange":
        from app.routers.state_strange import start_strange_flow
        await start_strange_flow(cb)
        return
    row = None
    if pref:
        # try category first
        import random
        practices = await db.list_practices_by_category(pref)
        if practices:
            import aiosqlite
            choice = random.choice(practices)
            row = await db.get_practice(int(choice["id"]))
    if row is None:
        row = await db.random_practice()
    if row:
        await cb.message.edit_text("Давай попробуем вот это 👉\n\n" + format_practice(row), reply_markup=practice_actions_kb(int(row["id"])) )
    await cb.answer()


    


