import os
from cryptography.fernet import Fernet

# Required: Telegram bot token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Required for payments: provider token from BotFather (after enabling Stars)
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "YOUR_PROVIDER_TOKEN_HERE")

# Encryption key for API keys – generate once and keep secret
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())

# Database file
DATABASE = "user_history.db"

# Star prices for premium products (in Telegram Stars)
STAR_PRICES = {
    "premium_monthly": 50,      # 50 Stars ≈ $0.70
    "premium_yearly": 500,       # 500 Stars ≈ $7.00
    "premium_lifetime": 2000,    # 2000 Stars ≈ $28.00
}

# Free tier daily limit (0 = unlimited)
FREE_DAILY_LIMIT = 10

# Owner Telegram ID (get from @userinfobot)
OWNER_ID = 123456789  # ← REPLACE WITH YOUR ACTUAL USER ID
