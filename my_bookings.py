# «Мои записи»: показать свои записи и отменить ненужную
from datetime import date

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

import database
from booking import date_label
from keyboards import BTN_BOOK, BTN_MY, cancel_booking_keyboard

router = Router()


@router.message(F.text == BTN_MY)
async def show_my_bookings(message: Message):
    rows = database.user_bookings(message.from_user.id, date.today().isoformat())
    if not rows:
        await message.answer(f"У тебя пока нет записей. Нажми «{BTN_BOOK}» 🙂")
        return

    # Каждая запись — отдельное сообщение со своей кнопкой «Отменить»
    for booking_id, service, day, time in rows:
        label = date_label(date.fromisoformat(day))
        await message.answer(
            f"💇 {service}\n📅 {label} в {time}",
            reply_markup=cancel_booking_keyboard(booking_id),
        )


# Срабатывает на нажатие кнопки под сообщением с меткой «cancel:...»
@router.callback_query(F.data.startswith("cancel:"))
async def cancel_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split(":")[1])  # «cancel:5» → 5

    if database.delete_booking(booking_id, callback.from_user.id):
        # Меняем текст сообщения, кнопка при этом исчезает
        await callback.message.edit_text(callback.message.text + "\n\n❌ Запись отменена")
    else:
        await callback.message.edit_text("Эта запись уже отменена")

    await callback.answer()  # убираем «часики» на кнопке
