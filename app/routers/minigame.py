from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.context import get_db


class MiniGameStates(StatesGroup):
    ask = State()


router = Router(name="minigame")


@router.message(Command("minigame"))
async def cmd_minigame(message: Message, state: FSMContext) -> None:
    await state.set_state(MiniGameStates.ask)
    await message.answer(
        "Ситуация: коллега резко ответил вам в чате. Что вы сделаете?\n"
        "1) Ответить тем же тоном.\n2) Сделать паузу и уточнить, что именно его раздражает.\n3) Игнорировать.\nОтправьте 1, 2 или 3."
    )


@router.message(MiniGameStates.ask)
async def on_answer(message: Message, state: FSMContext) -> None:
    choice = (message.text or "").strip()
    db = get_db()
    if choice == "2":
        await db.add_points(message.from_user.id, 2)
        await message.answer("Верно. Пауза и уточнение помогают снизить напряжение. +2 очка")
    else:
        await message.answer("Есть варианты лучше. Попробуйте в следующий раз сделать паузу и уточнить.")
    await state.clear()


