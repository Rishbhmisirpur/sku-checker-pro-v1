import sqlite3

conn = sqlite3.connect("results.db", check_same_thread=False)
cur = conn.cursor()

def init_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT,
            seller TEXT,
            price TEXT,
            result TEXT
        )
    """)
    conn.commit()

def save_result(res):
    cur.execute("""
        INSERT INTO results (sku, seller, price, result)
        VALUES (?, ?, ?, ?)
    """, (
        res["sku_val"],
        res["seller_val"],
        res["price_val"],
        res["result"]
    ))
    conn.commit()
