import sqlite3

def save_result(sku, seller, price, result):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("INSERT INTO results (sku, seller, price, result) VALUES (?, ?, ?, ?)",
              (sku, seller, price, result))

    conn.commit()
    conn.close()
