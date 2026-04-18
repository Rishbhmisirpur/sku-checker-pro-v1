import sqlite3

conn = sqlite3.connect("data.db")
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

print("Database ready")
