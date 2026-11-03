# Работа с базой данных SQLite: сохраняем и читаем записи
import sqlite3
from pathlib import Path

# Файл базы лежит рядом с кодом, откуда бы ни запустили бота
DB_PATH = Path(__file__).parent / "studio.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        # UNIQUE(date, time) — база сама не даст записать двоих на одно время
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name    TEXT,
                service TEXT NOT NULL,
                date    TEXT NOT NULL,
                time    TEXT NOT NULL,
                reminded INTEGER DEFAULT 0,
                UNIQUE (date, time)
            )
        """)
        # В базе, созданной до Этапа 8, столбца reminded ещё нет — добавляем его.
        # Если он уже есть, SQLite выдаст ошибку, и мы её просто пропустим
        try:
            conn.execute("ALTER TABLE bookings ADD COLUMN reminded INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass


# Возвращает True, если записали, и False, если время уже занято
def add_booking(user_id, name, service, date, time):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO bookings (user_id, name, service, date, time) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, name, service, date, time),
            )
        return True
    except sqlite3.IntegrityError:
        return False


# Список занятых времён на дату, например ["10:00", "14:00"]
def taken_times(date):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT time FROM bookings WHERE date = ?", (date,)
        ).fetchall()
    return [row[0] for row in rows]


# Будущие записи пользователя: список (id, услуга, дата, время), ближайшие первыми
def user_bookings(user_id, today):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, service, date, time FROM bookings "
            "WHERE user_id = ? AND date >= ? ORDER BY date, time",
            (user_id, today),
        ).fetchall()


# Все записи на дату для владельца: список (время, услуга, имя) по порядку
def day_bookings(date):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT time, service, name FROM bookings WHERE date = ? ORDER BY time",
            (date,),
        ).fetchall()


# Будущие записи, о которых ещё не напомнили: список (id, user_id, услуга, дата, время)
def not_reminded(today):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, user_id, service, date, time FROM bookings "
            "WHERE reminded = 0 AND date >= ?",
            (today,),
        ).fetchall()


# Ставим отметку «напомнили», чтобы не напоминать второй раз
def mark_reminded(booking_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE bookings SET reminded = 1 WHERE id = ?", (booking_id,))


# Удаляет запись. Проверяем и user_id, чтобы нельзя было отменить чужую запись.
# Возвращает True, если что-то удалили
def delete_booking(booking_id, user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM bookings WHERE id = ? AND user_id = ?",
            (booking_id, user_id),
        )
    return cursor.rowcount > 0
