# Главный файл: запускает бота
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import admin
import booking
import database
import my_bookings
import reminders
from config import BOT_TOKEN
from keyboards import BTN_ABOUT, BTN_BOOK, BTN_MY, main_menu

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(booking.router)  # подключаем шаги записи из booking.py
dp.include_router(my_bookings.router)  # подключаем «Мои записи» из my_bookings.py
dp.include_router(admin.router)  # подключаем режим владельца из admin.py


# Срабатывает, когда пользователь отправляет /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()  # если человек был посреди записи — начинаем с чистого листа
    name = message.from_user.first_name
    await message.answer(
        f"Привет, {name}! 👋\n"
        "Я бот студии красоты «Лотос». Выбери, что нужно, в меню ниже.",
        reply_markup=main_menu,  # показываем кнопки меню
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Как пользоваться ботом:\n"
        f"• {BTN_BOOK} — записаться на услугу\n"
        f"• {BTN_MY} — посмотреть или отменить запись\n"
        f"• {BTN_ABOUT} — адрес и часы работы\n\n"
        "Если меню пропало, отправь /start",
        reply_markup=main_menu,
    )


# Показывает человеку его Telegram ID — нужен, чтобы вписать владельца в .env
@dp.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(f"Твой Telegram ID: {message.from_user.id}")


# Нажатие на кнопку присылает боту её текст, поэтому ловим по тексту
@dp.message(F.text == BTN_ABOUT)
async def about(message: Message):
    await message.answer(
        "Студия красоты «Лотос» 🌸\n"
        "📍 ул. Примерная, 1\n"
        "🕙 Ежедневно с 10:00 до 20:00\n"
        "Услуги: стрижка, маникюр, окрашивание"
    )


async def main():
    database.init_db()  # создаём таблицу, если её ещё нет
    # Запускаем проверку напоминаний «в фоне», параллельно с ответами на сообщения
    reminder_task = asyncio.create_task(reminders.reminder_loop(bot))
    print("Бот запущен. Чтобы остановить, нажми Ctrl+C")
    # Бот постоянно спрашивает у Telegram: «есть новые сообщения?»
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
