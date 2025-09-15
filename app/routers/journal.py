from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.context import get_db


class JournalStates(StatesGroup):
    choosing_state = State()
    writing_note = State()


router = Router(name="journal")


@router.message(Command("journal"))
async def cmd_journal(message: Message, state: FSMContext) -> None:
    await state.set_state(JournalStates.choosing_state)
    await message.answer("Какое у вас состояние сейчас? (например: тревога, ресурс, усталость, злость)")


@router.message(JournalStates.choosing_state)
async def on_choose_state(message: Message, state: FSMContext) -> None:
    await state.update_data(current_state=message.text.strip())
    await state.set_state(JournalStates.writing_note)
    await message.answer("Добавьте короткую заметку (или отправьте '-' чтобы пропустить)")


@router.message(JournalStates.writing_note)
async def on_note(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    st = data.get("current_state", "")
    note = None if message.text.strip() == "-" else message.text.strip()
    db = get_db()
    await db.add_journal_entry(message.from_user.id, st, note)
    # Award for first journal entry
    total = await db.count_journal_entries(message.from_user.id)
    if total == 1:
        if await db.grant_achievement(message.from_user.id, "first_journal"):
            await db.add_points(message.from_user.id, 5)
    await message.answer("Записано. Я подберу практику под состояние:")
    row = await db.random_practice()
    if row:
        from app.routers.start import format_practice

        await message.answer(format_practice(row))
    await state.clear()


