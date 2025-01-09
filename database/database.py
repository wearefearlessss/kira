# Подключение к SQLite
import sqlite3

conn = sqlite3.connect("notes.db")
cursor = conn.cursor()

# Создание таблицы, если её нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    tag TEXT
)
""")
conn.commit()

