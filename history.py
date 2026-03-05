import sqlite3
from datetime import datetime, timedelta
from config import DATABASE
from llm_integration import encrypt_key, decrypt_key

def init_db():
    """Initialize SQLite database with all tables."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # History table
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (user_id INTEGER, 
                  command TEXT, 
                  input TEXT, 
                  output TEXT, 
                  timestamp DATETIME)''')
    
    # User API keys table (encrypted)
    c.execute('''CREATE TABLE IF NOT EXISTS user_keys
                 (user_id INTEGER PRIMARY KEY,
                  provider TEXT,
                  encrypted_key TEXT,
                  created_at DATETIME)''')
    
    # Premium users table
    c.execute('''CREATE TABLE IF NOT EXISTS premium_users
                 (user_id INTEGER PRIMARY KEY,
                  expiry DATETIME,
                  subscription_type TEXT)''')
    
    # Saved functions/custom commands (premium feature)
    c.execute('''CREATE TABLE IF NOT EXISTS saved_functions
                 (user_id INTEGER,
                  name TEXT,
                  expression TEXT,
                  created_at DATETIME,
                  PRIMARY KEY (user_id, name))''')
    
    conn.commit()
    conn.close()

# ========== History Functions ==========
def add_history(user_id, command, input_text, output_text):
    """Add calculation to history."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO history VALUES (?,?,?,?,?)",
              (user_id, command, input_text[:200], str(output_text)[:200], timestamp))
    conn.commit()
    conn.close()

def get_history(user_id, limit=10):
    """Get user's recent history."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''SELECT command, input, output, timestamp 
                 FROM history 
                 WHERE user_id=? 
                 ORDER BY timestamp DESC 
                 LIMIT ?''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def clear_history(user_id):
    """Clear user's history."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

# ========== API Key Functions ==========
def set_user_key(user_id, provider, api_key):
    """Store encrypted API key."""
    encrypted = encrypt_key(api_key)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_keys (user_id, provider, encrypted_key, created_at)
                 VALUES (?, ?, ?, ?)''',
              (user_id, provider, encrypted, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_key(user_id):
    """Retrieve and decrypt API key."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT provider, encrypted_key FROM user_keys WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        provider, enc_key = row
        try:
            decrypted = decrypt_key(enc_key)
            return provider, decrypted
        except:
            return None, None
    return None, None

def delete_user_key(user_id):
    """Remove user's API key."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM user_keys WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()

# ========== Premium Functions ==========
def set_premium(user_id, expiry, sub_type="monthly"):
    """Set user as premium with expiry date."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO premium_users (user_id, expiry, subscription_type)
                 VALUES (?, ?, ?)''',
              (user_id, expiry.isoformat(), sub_type))
    conn.commit()
    conn.close()

def is_premium(user_id):
    """Check if user has active premium subscription."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT expiry FROM premium_users WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        expiry = datetime.fromisoformat(row[0])
        if expiry > datetime.now():
            return True
        else:
            # Auto-clean expired
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('DELETE FROM premium_users WHERE user_id=?', (user_id,))
            conn.commit()
            conn.close()
    return False

def get_premium_expiry(user_id):
    """Get premium expiry date."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT expiry FROM premium_users WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return datetime.fromisoformat(row[0])
    return None

def get_daily_count(user_id):
    """Count user's calculations today (for free tier limit)."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    c.execute('''SELECT COUNT(*) FROM history 
                 WHERE user_id=? AND DATE(timestamp)=?''', 
                 (user_id, today))
    count = c.fetchone()[0]
    conn.close()
    return count

# ========== Saved Functions (Premium) ==========
def save_function(user_id, name, expression):
    """Save a custom function (premium feature)."""
    if not is_premium(user_id):
        return False
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO saved_functions (user_id, name, expression, created_at)
                 VALUES (?, ?, ?, ?)''',
              (user_id, name, expression, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def get_saved_function(user_id, name):
    """Retrieve a saved function."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT expression FROM saved_functions WHERE user_id=? AND name=?',
              (user_id, name))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def list_saved_functions(user_id):
    """List all saved functions for a user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT name, expression, created_at FROM saved_functions WHERE user_id=?',
              (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows