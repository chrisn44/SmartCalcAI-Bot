"""
Spam Management Commands - For bot owner to manage spam protection
"""

from telegram import Update
from telegram.ext import ContextTypes
from anti_spam import anti_spam
from spam_protected_handler import owner_only
import logging

logger = logging.getLogger(__name__)

@owner_only
async def spam_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get spam protection statistics"""
    stats = anti_spam.get_stats()
    
    message = (
        "📊 **Spam Protection Statistics**\n\n"
        f"👤 Active users: `{stats['active_users']}`\n"
        f"💬 Active chats: `{stats['active_chats']}`\n"
        f"🚫 Banned users: `{stats['banned_users']}`\n"
        f"🚫 Banned chats: `{stats['banned_chats']}`\n"
        f"⚠️ Warnings issued: `{stats['warnings_issued']}`\n"
        f"📨 Requests/min: `{stats['requests_last_minute']}`\n"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

@owner_only
async def unban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user - Usage: /unbanuser <user_id>"""
    try:
        user_id = int(context.args[0])
        if anti_spam.unban_user(user_id):
            await update.message.reply_text(f"✅ User {user_id} has been unbanned.")
        else:
            await update.message.reply_text(f"❌ User {user_id} was not banned.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /unbanuser <user_id>")

@owner_only
async def unban_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a chat - Usage: /unbanchat <chat_id>"""
    try:
        chat_id = int(context.args[0])
        if anti_spam.unban_chat(chat_id):
            await update.message.reply_text(f"✅ Chat {chat_id} has been unbanned.")
        else:
            await update.message.reply_text(f"❌ Chat {chat_id} was not banned.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /unbanchat <chat_id>")

@owner_only
async def whitelist_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add user to whitelist (exempt from spam protection)"""
    # This would need a whitelist set in anti_spam
    await update.message.reply_text("Whitelist feature coming soon.")

@owner_only
async def adjust_limits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adjust spam limits - Usage: /setlimit <user|chat|global> <new_limit>"""
    try:
        limit_type = context.args[0].lower()
        new_limit = int(context.args[1])
        
        if limit_type == 'user':
            anti_spam.USER_LIMIT = new_limit
            await update.message.reply_text(f"✅ User limit set to {new_limit}")
        elif limit_type == 'chat':
            anti_spam.CHAT_LIMIT = new_limit
            await update.message.reply_text(f"✅ Chat limit set to {new_limit}")
        elif limit_type == 'global':
            anti_spam.GLOBAL_LIMIT = new_limit
            await update.message.reply_text(f"✅ Global limit set to {new_limit}")
        else:
            await update.message.reply_text("Invalid limit type. Use: user, chat, or global")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /setlimit <user|chat|global> <new_limit>")