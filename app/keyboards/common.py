from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📚 Библиотека"),
                KeyboardButton(text="🌿 Я здесь"),
            ],
            [
                KeyboardButton(text="🌅 Практика дня"),
                KeyboardButton(text="✅ Чек-листы"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел",
    )


def categories_kb(categories: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = []
    for code, title in categories:
        rows.append([InlineKeyboardButton(text=title, callback_data=f"cat:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def practices_kb(practices: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = []
    for pid, title in practices:
        rows.append([InlineKeyboardButton(text=title, callback_data=f"pr:{pid}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def checklist_items_kb(items: list[tuple[int, str, int]]) -> InlineKeyboardMarkup:
    rows = []
    for item_id, title, done in items:
        prefix = "✅" if done else "☑️"
        rows.append([InlineKeyboardButton(text=f"{prefix} {title}", callback_data=f"cli:{item_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def practice_actions_kb(practice_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done:{practice_id}")],
            [
                InlineKeyboardButton(text="⏰ Напомнить 15 мин", callback_data=f"remind:{practice_id}:900"),
                InlineKeyboardButton(text="⏰ 1 час", callback_data=f"remind:{practice_id}:3600"),
                InlineKeyboardButton(text="⏰ 3 часа", callback_data=f"remind:{practice_id}:10800"),
            ],
        ]
    )


def state_select_kb() -> InlineKeyboardMarkup:
    # Base states with emojis
    buttons = [
        ("😡 Я зол", "angry"),
        ("😕 Я растерян", "confused"),
        ("🤔 Мне странно", "strange"),
        ("😰 Тревожно", "anxious"),
        ("😔 Грусть", "sad"),
        ("😴 Устал", "tired"),
        ("🙂 Спокоен", "calm"),
    ]
    rows = []
    for text, code in buttons:
        rows.append([InlineKeyboardButton(text=text, callback_data=f"st:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


