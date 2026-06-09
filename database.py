import sqlite3

conn = sqlite3.connect("bearing_capacity.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    soil_type TEXT,
    footing_type TEXT,
    cohesion REAL,
    phi REAL,
    gamma REAL,
    depth REAL,
    width REAL,
    fos REAL,
    ultimate_capacity REAL,
    safe_capacity REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")