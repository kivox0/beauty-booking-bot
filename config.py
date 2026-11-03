# Настройки бота: читаем секреты из файла .env
import os

from dotenv import load_dotenv

# Загружаем переменные из .env в окружение программы
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Если токена нет, сразу понятно, что не так, вместо странной ошибки позже
if not BOT_TOKEN:
    raise SystemExit("Не найден BOT_TOKEN. Проверь файл .env")

# Telegram ID тех, кому доступен режим владельца, через запятую: 111,222,333
# Всё, что не число, пропускаем. Пустой список — режим владельца выключен
ADMIN_IDS = []
for part in os.getenv("ADMIN_IDS", "").split(","):
    part = part.strip()
    if part.isdigit():
        ADMIN_IDS.append(int(part))
