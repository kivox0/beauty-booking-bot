# Пошаговая запись: услуга → дата → время → подтверждение
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import database
from keyboards import BTN_BOOK, BTN_CANCEL, BTN_CONFIRM, main_menu, make_keyboard

# Отдельный «сортировщик» только для записи, подключается к главному в bot.py
router = Router()

SERVICES = ["Стрижка", "Маникюр", "Окрашивание"]
TIMES = ["10:00", "12:00", "14:00", "16:00", "18:00"]
WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


# Красивая подпись даты для человека, например «04.11 ср»
def date_label(day):
    return f"{day:%d.%m} {WEEKDAYS[day.weekday()]}"


# Ближайшие 7 дней, начиная с завтра.
# Ключ — текст кнопки «04.11 ср», значение — дата для базы «2026-11-04»
def upcoming_dates():
    today = date.today()
    result = {}
    for i in range(1, 8):
        day = today + timedelta(days=i)
        result[date_label(day)] = day.isoformat()
    return result


# Свободные времена на дату: все времена минус занятые в базе
def free_times(day):
    taken = database.taken_times(day)
    return [t for t in TIMES if t not in taken]


# Шаги диалога: бот помнит, на каком шаге сейчас каждый пользователь
class Booking(StatesGroup):
    service = State()
    date = State()
    time = State()
    confirm = State()


@router.message(F.text == BTN_BOOK)
async def start_booking(message: Message, state: FSMContext):
    await state.set_state(Booking.service)
    await message.answer("Выбери услугу:", reply_markup=make_keyboard(SERVICES))


# «Отмена» работает на любом шаге, поэтому стоит выше остальных шагов
@router.message(F.text == BTN_CANCEL)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Запись отменена.", reply_markup=main_menu)


@router.message(Booking.service)
async def choose_service(message: Message, state: FSMContext):
    if message.text not in SERVICES:
        await message.answer("Выбери услугу кнопкой ниже 👇")
        return
    await state.update_data(service=message.text)
    await state.set_state(Booking.date)
    await message.answer(
        "Выбери дату:", reply_markup=make_keyboard(list(upcoming_dates()), row_size=3)
    )


@router.message(Booking.date)
async def choose_date(message: Message, state: FSMContext):
    dates = upcoming_dates()
    if message.text not in dates:
        await message.answer("Выбери дату кнопкой ниже 👇")
        return

    day = dates[message.text]
    times = free_times(day)
    if not times:
        await message.answer("На этот день всё занято 😔 Выбери другую дату")
        return

    await state.update_data(date=day, date_label=message.text)
    await state.set_state(Booking.time)
    await message.answer("Выбери время:", reply_markup=make_keyboard(times, row_size=3))


@router.message(Booking.time)
async def choose_time(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in free_times(data["date"]):
        await message.answer("Выбери свободное время кнопкой ниже 👇")
        return
    await state.update_data(time=message.text)
    await state.set_state(Booking.confirm)

    data = await state.get_data()
    await message.answer(
        "Проверь запись:\n"
        f"💇 {data['service']}\n"
        f"📅 {data['date_label']}\n"
        f"🕙 {data['time']}",
        reply_markup=make_keyboard([BTN_CONFIRM]),
    )


@router.message(Booking.confirm)
async def confirm(message: Message, state: FSMContext):
    if message.text != BTN_CONFIRM:
        await message.answer(f"Нажми «{BTN_CONFIRM}» или «{BTN_CANCEL}»")
        return

    data = await state.get_data()
    saved = database.add_booking(
        user_id=message.from_user.id,
        name=message.from_user.first_name,
        service=data["service"],
        date=data["date"],
        time=data["time"],
    )

    # Пока человек думал, это время мог занять кто-то другой
    if not saved:
        await state.set_state(Booking.time)
        await message.answer(
            "Ой, это время только что заняли 😔 Выбери другое:",
            reply_markup=make_keyboard(free_times(data["date"]), row_size=3),
        )
        return

    await state.clear()
    await message.answer(
        f"Готово! Ты записан(а): {data['service']}, "
        f"{data['date_label']} в {data['time']} ✨",
        reply_markup=main_menu,
    )
