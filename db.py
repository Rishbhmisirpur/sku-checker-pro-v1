import sqlite3
import threading

# 🔒 Lock prevents multi-thread crash
lock = threading.Lock()

DB_NAME = "data.db"


# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
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


# ---------------- SAVE RESULT (THREAD SAFE) ----------------
def save_result(sku, seller, price, result):
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()

        with lock:
            c.execute(
                "INSERT INTO results (sku, seller, price, result) VALUES (?, ?, ?, ?)",
                (str(sku), str(seller), str(price), str(result))
            )

            conn.commit()

        conn.close()

    except Exception as e:
        print("DB Error:", e)


# ---------------- FETCH ALL (optional dashboard use) ----------------
def fetch_all():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()

    c.execute("SELECT * FROM results ORDER BY id DESC")
    data = c.fetchall()

    conn.close()
    return data
