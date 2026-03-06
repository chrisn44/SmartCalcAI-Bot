"""
Message Filter - Filters out spam messages before they reach handlers
"""

import re
from telegram import Update
from telegram.ext import MessageHandler, filters
from anti_spam import anti_spam

class SpamFilter:
    """Filter for spam messages"""
    
    # Spam patterns
    SPAM_PATTERNS = [
        r'(http|https)://\S+',  # URLs
        r'@\w+',                 # Mentions
        r'\b(bit\.ly|tinyurl|goo\.gl)\b',  # URL shorteners
        r'[📢🔊🔔📣]',            # Spam emojis
        r'(\b\w+\b)\s+\1\s+\1',  # Repeated words
        r'(.)\1{4,}',            # Repeated characters
    ]
    
    # Compiled patterns
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in SPAM_PATTERNS]
    
    @staticmethod
    def is_spam(text):
        """Check if message contains spam patterns"""
        if not text:
            return False
        
        for pattern in SpamFilter.compiled_patterns:
            if pattern.search(text):
                return True
        
        return False
    
    @staticmethod
    async def filter_message(update: Update):
        """Filter message and return True if it should be blocked"""
        if not update.message or not update.message.text:
            return False
        
        text = update.message.text
        user_id = update.effective_user.id
        
        # Check for spam patterns
        if SpamFilter.is_spam(text):
            # Warn user
            await update.message.reply_text(
                "⚠️ Your message looks like spam. Please don't send spam messages."
            )
            return True
        
        return False

# Create filter instance
spam_filter = SpamFilter()