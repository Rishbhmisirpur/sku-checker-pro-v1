# db.py
import sqlite3
import threading

lock = threading.Lock()

DB = "data.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT,
        seller TEXT,
        price TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_result(sku, seller, price, result):
    conn = sqlite3.connect(DB, check_same_thread=False)
    c = conn.cursor()

    with lock:
        c.execute(
            "INSERT INTO results (sku, seller, price, result) VALUES (?, ?, ?, ?)",
            (str(sku), str(seller), str(price), str(result))
        )

        conn.commit()

    conn.close()
