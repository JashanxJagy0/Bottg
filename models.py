# models.py - Adapter module for feature file integration
# This module bridges the feature files with bot.py's data structures
import sqlite3
from datetime import datetime, timezone
import os

# Initialize databases if they don't exist
def init_databases():
    """Initialize database tables"""
    # dicegame.db for game data
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0,
                username TEXT,
                created_at TEXT
            )
        """)
        
        # Transactions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount REAL,
                details TEXT,
                timestamp TEXT
            )
        """)
        
        # Stats table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                user_id INTEGER PRIMARY KEY,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0
            )
        """)
        
        # Wagers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wagers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game_type TEXT,
                amount REAL,
                payout REAL DEFAULT 0,
                timestamp TEXT
            )
        """)
        
        # Games table for dice games
        cur.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                p1_id INTEGER,
                p2_id INTEGER,
                amount REAL,
                created_at TEXT
            )
        """)
        
        # Game sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                mode TEXT,
                played_at TEXT,
                bet REAL,
                won_amount REAL DEFAULT 0,
                is_win INTEGER DEFAULT 0
            )
        """)
        
        # Referrals table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                user_id INTEGER PRIMARY KEY,
                referrer_id INTEGER
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS referral_earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                amount REAL,
                timestamp TEXT
            )
        """)
        
        conn.commit()

# Initialize on import
init_databases()

def get_connection():
    """Get database connection for dicegame.db"""
    return sqlite3.connect("dicegame.db")

def update_balance(user_id: int, new_balance: float):
    """Update user balance in database"""
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, balance, created_at) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET balance = ?
        """, (user_id, new_balance, datetime.now(timezone.utc).isoformat(), new_balance))
        conn.commit()

def log_transaction(user_id: int, tx_type: str, amount: float, details: str = ""):
    """Log a transaction to the database"""
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (user_id, type, amount, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, tx_type, amount, details, datetime.now(timezone.utc).isoformat()))
        conn.commit()

def update_stats(user_id: int, *args):
    """Update user statistics - flexible signature for compatibility"""
    # Handle both (user_id, won) and (user_id, game_type, bet, payout) signatures
    if len(args) == 1:
        won = args[0]
    elif len(args) == 3:
        # game_type, bet, payout format - determine win from payout
        game_type, bet, payout = args
        won = payout > bet
    else:
        won = False
        
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        if won:
            cur.execute("""
                INSERT INTO stats (user_id, wins, losses) VALUES (?, 1, 0)
                ON CONFLICT(user_id) DO UPDATE SET wins = wins + 1
            """, (user_id,))
        else:
            cur.execute("""
                INSERT INTO stats (user_id, wins, losses) VALUES (?, 0, 1)
                ON CONFLICT(user_id) DO UPDATE SET losses = losses + 1
            """, (user_id,))
        conn.commit()
