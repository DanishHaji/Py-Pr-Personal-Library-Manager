import sqlite3

# Connect to the database (creates the file if it doesn't exist)
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# Create a table for books if it doesn't already exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        genre TEXT,
        read_status BOOLEAN
    )
''')

conn.commit()
conn.close()
print("✅ Database and table created successfully!")
