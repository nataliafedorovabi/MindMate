from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.context import get_db
from app.keyboards.common import practice_actions_kb
from app.utils import format_practice


router = Router(name="state_strange")


def _kb_next(to_step: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Следующий шаг", callback_data=to_step)]])


def _kb_finish() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Завершить практику", callback_data="strg:finish")]])


def _kb_after_finish() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ещё одна практика", callback_data="strg:another")],
            [InlineKeyboardButton(text="Закончить на сегодня", callback_data="strg:end")],
        ]
    )


async def start_strange_flow(cb: CallbackQuery) -> None:
    text = (
        "Ты выбрал «Мне странно» 🌱\n"
        "Давай сделаем короткую практику, чтобы почувствовать тело и заземлиться.  \n"
        "Просто следуй шагам и двигайся в своём ритме.  \n"
        "⏱️ Это займёт всего 2–3 минуты."
    )
    await cb.message.edit_text(text, reply_markup=_kb_next("strg:step:1"))
    await cb.answer()


@router.callback_query(F.data == "strg:step:1")
async def step1(cb: CallbackQuery) -> None:
    text = (
        "1️⃣ Сканирование тела\n"
        "Сядь или встань удобно.  \n"
        "Закрой глаза, если хочется.  \n"
        "Проведи внимание от стоп до головы:\n"
        "• Стопы — чувствую, как они стоят на земле.\n"
        "• Ноги — есть ли напряжение или расслабление?\n"
        "• Таз и живот — лёгкое дыхание, мягкая осознанность.\n"
        "• Грудная клетка и плечи — как они себя чувствуют?\n"
        "• Руки и кисти — ощущение покоя или лёгкого напряжения.\n"
        "• Шея, челюсть, лицо — расслабляем, если есть скованность."
    )
    await cb.message.edit_text(text, reply_markup=_kb_next("strg:step:2"))
    await cb.answer()


@router.callback_query(F.data == "strg:step:2")
async def step2(cb: CallbackQuery) -> None:
    text = (
        "2️⃣ Заземление через ощущения\n"
        "Посмотри вокруг и найди:\n"
        "• 5 вещей, которые видишь 👀\n"
        "• 4 вещи, которые можешь потрогать ✋\n"
        "• 3 звука, которые слышишь 👂\n"
        "• 2 запаха, которые ощущаешь 👃\n"
        "• 1 вкус, который чувствуешь 👅\n\n"
        "Просто замечай, без оценки.  \n"
        "⏱️ Таймер: 90 секунд"
    )
    await cb.message.edit_text(text, reply_markup=_kb_next("strg:step:3"))
    await cb.answer()


@router.callback_query(F.data == "strg:step:3")
async def step3(cb: CallbackQuery) -> None:
    text = (
        "3️⃣ Дыхание и пауза\n"
        "Сделай 3 глубоких вдоха и выдоха:\n"
        "• Вдох — медленно через нос, наполняя живот.  \n"
        "• Выдох — мягко через рот, отпускание напряжения.  \n\n"
        "Просто наблюдай за ощущениями в теле. 🌿\n"
        "⏱️ Таймер: 60 секунд"
    )
    await cb.message.edit_text(text, reply_markup=_kb_finish())
    await cb.answer()


@router.callback_query(F.data == "strg:finish")
async def finish(cb: CallbackQuery) -> None:
    text = (
        "Отлично! Ты сделал небольшую паузу для себя 🌱  \n"
        "Хочешь сделать ещё одну короткую практику или заканчиваем на сегодня?"
    )
    await cb.message.edit_text(text, reply_markup=_kb_after_finish())
    await cb.answer()


@router.callback_query(F.data == "strg:another")
async def another(cb: CallbackQuery) -> None:
    db = get_db()
    row = await db.random_practice()
    if row:
        await cb.message.edit_text("Попробуем ещё одну 👉\n\n" + format_practice(row), reply_markup=practice_actions_kb(int(row["id"])) )
    await cb.answer()


@router.callback_query(F.data == "strg:end")
async def end(cb: CallbackQuery) -> None:
    await cb.message.edit_text("Хорошо. Если захочешь — я рядом 🌿")
    await cb.answer()


