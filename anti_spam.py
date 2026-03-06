"""
Anti-Spam Module - Protects your bot from spam and prevents Telegram blocks
"""

import time
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

class AntiSpam:
    def __init__(self):
        # Rate limits
        self.USER_LIMIT = 10          # Max 10 messages per minute per user
        self.CHAT_LIMIT = 20           # Max 20 messages per minute per chat
        self.GLOBAL_LIMIT = 100        # Max 100 messages per minute globally
        self.SAME_MESSAGE_LIMIT = 3     # Max 3 identical messages per minute
        self.CAPS_LIMIT = 5             # Max 5 CAPS messages per minute
        
        # Tracking dictionaries
        self.user_requests = defaultdict(list)
        self.chat_requests = defaultdict(list)
        self.global_requests = []
        self.user_messages = defaultdict(list)
        self.caps_messages = defaultdict(int)
        self.banned_users = set()
        self.banned_chats = set()
        self.warnings = defaultdict(int)
        
        # Time windows
        self.WINDOW = 60  # 60 seconds window
        self.BAN_DURATION = 3600  # 1 hour ban
        self.MAX_WARNINGS = 3  # Ban after 3 warnings
        
    def clean_old_requests(self):
        """Remove requests older than the time window"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.WINDOW)
        
        # Clean user requests
        for user_id in list(self.user_requests.keys()):
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id]
                if req_time > cutoff
            ]
            if not self.user_requests[user_id]:
                del self.user_requests[user_id]
        
        # Clean chat requests
        for chat_id in list(self.chat_requests.keys()):
            self.chat_requests[chat_id] = [
                req_time for req_time in self.chat_requests[chat_id]
                if req_time > cutoff
            ]
            if not self.chat_requests[chat_id]:
                del self.chat_requests[chat_id]
        
        # Clean global requests
        self.global_requests = [
            req_time for req_time in self.global_requests
            if req_time > cutoff
        ]
        
        # Clean user messages
        for user_id in list(self.user_messages.keys()):
            self.user_messages[user_id] = [
                (msg, t) for msg, t in self.user_messages[user_id]
                if t > cutoff
            ]
            if not self.user_messages[user_id]:
                del self.user_messages[user_id]
    
    def is_caps_spam(self, text):
        """Check if message is mostly caps (spam)"""
        if not text or len(text) < 5:
            return False
        
        caps_count = sum(1 for c in text if c.isupper())
        total_alpha = sum(1 for c in text if c.isalpha())
        
        if total_alpha == 0:
            return False
        
        caps_ratio = caps_count / total_alpha
        return caps_ratio > 0.7 and len(text) > 10
    
    def check_rate_limits(self, user_id, chat_id, message_text=""):
        """Check all rate limits and return (is_allowed, reason, should_ban)"""
        self.clean_old_requests()
        
        now = datetime.now()
        
        # Check if user is banned
        if user_id in self.banned_users:
            return False, "User is banned", False
        
        # Check if chat is banned
        if chat_id in self.banned_chats:
            return False, "Chat is banned", False
        
        # Check user rate limit
        if len(self.user_requests[user_id]) >= self.USER_LIMIT:
            self.warnings[user_id] += 1
            if self.warnings[user_id] >= self.MAX_WARNINGS:
                self.banned_users.add(user_id)
                logger.warning(f"User {user_id} banned for exceeding rate limit")
                return False, "User banned for spam", True
            return False, f"Rate limit exceeded. Please wait.", False
        
        # Check chat rate limit
        if len(self.chat_requests[chat_id]) >= self.CHAT_LIMIT:
            return False, "Chat rate limit exceeded", False
        
        # Check global rate limit
        if len(self.global_requests) >= self.GLOBAL_LIMIT:
            return False, "Global rate limit exceeded", False
        
        # Check for duplicate messages
        if message_text:
            # Count identical messages in last minute
            identical_count = sum(1 for msg, t in self.user_messages[user_id] 
                                 if msg == message_text)
            
            if identical_count >= self.SAME_MESSAGE_LIMIT:
                self.warnings[user_id] += 1
                if self.warnings[user_id] >= self.MAX_WARNINGS:
                    self.banned_users.add(user_id)
                    logger.warning(f"User {user_id} banned for message spam")
                    return False, "User banned for spam", True
                return False, "Please don't send the same message multiple times", False
            
            # Check for caps spam
            if self.is_caps_spam(message_text):
                self.caps_messages[user_id] += 1
                if self.caps_messages[user_id] >= self.CAPS_LIMIT:
                    self.banned_users.add(user_id)
                    logger.warning(f"User {user_id} banned for CAPS spam")
                    return False, "User banned for CAPS spam", True
                return False, "Please don't use ALL CAPS", False
        
        # Record the request
        self.user_requests[user_id].append(now)
        self.chat_requests[chat_id].append(now)
        self.global_requests.append(now)
        
        if message_text:
            self.user_messages[user_id].append((message_text, now))
        
        return True, "", False
    
    def unban_user(self, user_id):
        """Manually unban a user"""
        if user_id in self.banned_users:
            self.banned_users.remove(user_id)
            self.warnings[user_id] = 0
            logger.info(f"User {user_id} unbanned")
            return True
        return False
    
    def unban_chat(self, chat_id):
        """Manually unban a chat"""
        if chat_id in self.banned_chats:
            self.banned_chats.remove(chat_id)
            logger.info(f"Chat {chat_id} unbanned")
            return True
        return False
    
    def get_stats(self):
        """Get spam protection statistics"""
        return {
            'active_users': len(self.user_requests),
            'active_chats': len(self.chat_requests),
            'banned_users': len(self.banned_users),
            'banned_chats': len(self.banned_chats),
            'warnings_issued': sum(self.warnings.values()),
            'requests_last_minute': len(self.global_requests)
        }

# Global instance
anti_spam = AntiSpam()