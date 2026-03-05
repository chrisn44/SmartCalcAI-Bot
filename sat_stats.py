"""
SAT Statistics Module – Database queries for bot statistics
"""

import sqlite3
from config import DATABASE
from datetime import datetime

def get_total_users():
    """Get total number of unique users who have used the bot."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT user_id) FROM history")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_premium_users():
    """Get number of active premium users."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("SELECT COUNT(*) FROM premium_users WHERE expiry > ?", (now,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_total_calculations():
    """Get total number of calculations performed."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM history")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_stats():
    """Return a dict with all statistics."""
    return {
        "total_users": get_total_users(),
        "premium_users": get_premium_users(),
        "total_calculations": get_total_calculations()
    }