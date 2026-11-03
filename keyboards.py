# Клавиатуры (кнопки) бота
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# Тексты кнопок храним в одном месте, чтобы не ошибиться в буквах в разных файлах
BTN_BOOK = "📅 Записаться"
BTN_MY = "📋 Мои записи"
BTN_ABOUT = "ℹ️ О студии"
BTN_CANCEL = "❌ Отмена"
BTN_CONFIRM = "✅ Подтвердить"

# Главное меню: каждый вложенный список — это один ряд кнопок
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_BOOK)],
        [KeyboardButton(text=BTN_MY), KeyboardButton(text=BTN_ABOUT)],
    ],
    resize_keyboard=True,  # кнопки компактные, а не на пол-экрана
)


# Собирает клавиатуру из списка текстов: по row_size кнопок в ряд + «Отмена» внизу
def make_keyboard(texts, row_size=2):
    rows = []
    for i in range(0, len(texts), row_size):
        rows.append([KeyboardButton(text=t) for t in texts[i:i + row_size]])
    rows.append([KeyboardButton(text=BTN_CANCEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# Кнопка прямо под сообщением. При нажатии бот получит не текст,
# а скрытую метку callback_data, например «cancel:5», где 5 — номер записи
def cancel_booking_keyboard(booking_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"cancel:{booking_id}")]
    ])
