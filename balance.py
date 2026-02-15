# balance.py - Balance management adapter
import sqlite3
from datetime import datetime, timezone

def get_balance(user_id: int) -> float:
    """Get user balance from database"""
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            return float(row[0])
        # If no balance in DB, initialize with 0
        cur.execute("INSERT OR IGNORE INTO users (user_id, balance, created_at) VALUES (?, 0, ?)",
                    (user_id, datetime.now(timezone.utc).isoformat()))
        conn.commit()
        return 0.0

def update_balance(user_id: int, new_balance: float):
    """Update user balance"""
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, balance, created_at) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET balance = ?
        """, (user_id, new_balance, datetime.now(timezone.utc).isoformat(), new_balance))
        conn.commit()

def add_wager(user_id: int, *args):
    """Log a wager to the database - flexible signature"""
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        
        # Handle different call signatures
        if len(args) == 1:
            # add_wager(user_id, amount)
            amount = args[0]
            cur.execute("""
                INSERT INTO wagers (user_id, game_type, amount, timestamp)
                VALUES (?, 'unknown', ?, ?)
            """, (user_id, amount, datetime.now(timezone.utc).isoformat()))
        elif len(args) == 2:
            # add_wager(user_id, game_type, amount) or add_wager(user_id, amount, payout)
            if isinstance(args[0], str):
                game_type, amount = args
                cur.execute("""
                    INSERT INTO wagers (user_id, game_type, amount, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (user_id, game_type, amount, datetime.now(timezone.utc).isoformat()))
            else:
                amount, payout = args
                cur.execute("""
                    INSERT INTO wagers (user_id, game_type, amount, payout, timestamp)
                    VALUES (?, 'unknown', ?, ?, ?)
                """, (user_id, amount, payout, datetime.now(timezone.utc).isoformat()))
        else:
            # add_wager(user_id, game_type, amount, payout)
            game_type, amount, payout = args
            cur.execute("""
                INSERT INTO wagers (user_id, game_type, amount, payout, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, game_type, amount, payout, datetime.now(timezone.utc).isoformat()))
        
        conn.commit()
