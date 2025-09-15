from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.common import state_select_kb


router = Router(name="journal")


@router.message(Command("journal"))
async def cmd_journal(message: Message) -> None:
    await message.answer("Как тебе сейчас?", reply_markup=state_select_kb())


