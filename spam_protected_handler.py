"""
Spam Protected Handler - Decorator to add spam protection to any command
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging
from anti_spam import anti_spam

logger = logging.getLogger(__name__)

def spam_protected(func):
    """Decorator to add spam protection to command handlers"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Get user and chat info
        user_id = update.effective_user.id if update.effective_user else None
        chat_id = update.effective_chat.id if update.effective_chat else None
        message_text = update.message.text if update.message else ""
        
        # Check rate limits
        is_allowed, reason, should_ban = anti_spam.check_rate_limits(
            user_id, chat_id, message_text
        )
        
        if not is_allowed:
            if should_ban:
                logger.warning(f"User {user_id} banned automatically")
                await update.message.reply_text(
                    "🚫 You have been banned for spamming.\n"
                    "Contact the bot owner if this is a mistake."
                )
            else:
                await update.message.reply_text(f"⏱️ {reason}")
            return
        
        # Execute the original function
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )
    
    return wrapper

def owner_only(func):
    """Decorator for owner-only commands"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from config import OWNER_ID
        
        user_id = update.effective_user.id
        if user_id != OWNER_ID:
            await update.message.reply_text("❌ This command is only for bot owner.")
            return
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper