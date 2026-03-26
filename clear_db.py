import sqlite3

conn = sqlite3.connect("data/lime_data.db")
conn.execute("DELETE FROM vehicles;")
conn.commit()
conn.close()

print("🧹 Old data cleared!")
