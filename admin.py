# Режим владельца: все записи на выбранный день
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import database
from booking import date_label
from config import ADMIN_IDS

router = Router()

# Пускаем в этот файл только тех, кто в списке. Остальным бот на /admin просто промолчит
router.message.filter(F.from_user.id.in_(ADMIN_IDS))
router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


# Кнопки с датами: сегодня и ещё 7 дней вперёд, по 4 в ряд
def days_keyboard():
    today = date.today()
    buttons = []
    for i in range(8):
        day = today + timedelta(days=i)
        buttons.append(
            InlineKeyboardButton(text=date_label(day), callback_data=f"admin:{day.isoformat()}")
        )
    rows = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer("👑 Режим владельца. Выбери день:", reply_markup=days_keyboard())


@router.callback_query(F.data.startswith("admin:"))
async def show_day(callback: CallbackQuery):
    day = callback.data.split(":")[1]  # «admin:2026-11-04» → «2026-11-04»
    rows = database.day_bookings(day)
    label = date_label(date.fromisoformat(day))

    if rows:
        lines = [f"🕙 {time} — {service}, {name}" for time, service, name in rows]
        text = f"📅 Записи на {label}:\n\n" + "\n".join(lines)
    else:
        text = f"📅 На {label} записей нет"

    await callback.message.answer(text)
    await callback.answer()
