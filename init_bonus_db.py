import sqlite3

if __name__ == '__main__':
    with sqlite3.connect("bonus.db") as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS level_progress (
            user_id INTEGER PRIMARY KEY,
            total_wager REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS level_bonus_claims (
            user_id INTEGER NOT NULL,
            level_name TEXT NOT NULL,
            claimed_at TEXT NOT NULL,
            PRIMARY KEY (user_id, level_name)
        )
        """)

        c.execute("CREATE INDEX IF NOT EXISTS idx_progress_wager ON level_progress(total_wager)")

        conn.commit()
    print("bonus.db initialized successfully")
