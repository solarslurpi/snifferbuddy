# Add this to test.py temporarily to check:
import sqlite3
try:
    conn = sqlite3.connect("C:/Users/happy/Documents/Projects/snifferbuddy/data/sniffer_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:", tables)
    conn.close()
except Exception as e:
    print("Error:", e)