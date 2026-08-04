import sqlite3

conn = sqlite3.connect("billsphere.db")
cur = conn.cursor()

cur.execute("PRAGMA table_info(plans)")
existing_cols = [row[1] for row in cur.fetchall()]

if "status" not in existing_cols:
    cur.execute("ALTER TABLE plans ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
    print("Added 'status' column")

if "deleted_at" not in existing_cols:
    cur.execute("ALTER TABLE plans ADD COLUMN deleted_at TIMESTAMP")
    print("Added 'deleted_at' column")

conn.commit()
conn.close()
print("Migration complete.")