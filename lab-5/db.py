import sqlite3

def init_db():
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_name TEXT UNIQUE,
            rate REAL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE
        );
    """)
    conn.commit()
    return conn
