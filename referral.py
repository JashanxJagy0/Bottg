# referral.py - Referral system adapter
import sqlite3

def track_referral_event(user_id: int, commission: float):
    """Track referral commission event"""
    with sqlite3.connect("dicegame.db") as conn:
        cur = conn.cursor()
        # Find referrer
        cur.execute("SELECT referrer_id FROM referrals WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row and row[0]:
            referrer_id = row[0]
            # Add commission to referrer's balance
            cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (commission, referrer_id))
            cur.execute("""
                INSERT INTO referral_earnings (referrer_id, referred_id, amount, timestamp)
                VALUES (?, ?, ?, datetime('now'))
            """, (referrer_id, user_id, commission))
            conn.commit()
