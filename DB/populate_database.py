import os
import sqlite3
import json

# Path to your JSON file
json_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fmi_full_site.json")

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("documents.db")
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT NOT NULL
)
""")

# Load the JSON data
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Insert data into the DB table
for entry in data:
    title = entry.get("title", "")
    content = entry.get("content", "")
    url = entry.get("url", "")
    cursor.execute("INSERT INTO documents (title, content, url) VALUES (?, ?, ?)", (title, content, url))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully transferred to the DB database.")