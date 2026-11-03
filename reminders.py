# Напоминания: бот сам пишет клиенту, когда до записи осталось меньше суток
import asyncio
from datetime import date, datetime, timedelta

import database
from booking import date_label

REMIND_BEFORE = timedelta(hours=24)  # за сколько до визита напоминать
CHECK_EVERY = 60  # как часто проверять, в секундах


async def send_reminders(bot):
    now = datetime.now()
    for booking_id, user_id, service, day, time in database.not_reminded(now.date().isoformat()):
        start = datetime.fromisoformat(f"{day} {time}")  # «2026-11-04» + «12:00»

        # Напоминаем, только если визит ещё не прошёл и до него меньше суток
        if now < start <= now + REMIND_BEFORE:
            label = date_label(date.fromisoformat(day))
            try:
                await bot.send_message(
                    user_id, f"⏰ Напоминаем: {service}, {label} в {time}. Ждём тебя! 🌸"
                )
            except Exception as error:
                # Например, человек заблокировал бота — просто пишем в консоль
                print("Не удалось отправить напоминание:", error)
            database.mark_reminded(booking_id)


# Бесконечный цикл: проверить → подождать минуту → снова проверить
async def reminder_loop(bot):
    while True:
        await send_reminders(bot)
        await asyncio.sleep(CHECK_EVERY)
