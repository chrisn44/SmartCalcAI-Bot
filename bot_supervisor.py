"""
Bot Supervisor Module - Makes your bot indestructible!
Automatically recovers from crashes, connection issues, and message deletions.
"""

import os
import sys
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta
import signal
import psutil

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotSupervisor:
    """
    Supervises the bot process and automatically restarts it if it crashes.
    Also handles message deletion issues by resetting the connection.
    """
    
    def __init__(self, bot_script='bot.py', max_restarts=10, restart_delay=5):
        self.bot_script = bot_script
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.restart_count = 0
        self.process = None
        self.last_restart_time = None
        self.healthy = True
        
    def start_bot(self):
        """Start the bot process"""
        try:
            logger.info(f"🚀 Starting bot: {self.bot_script}")
            self.process = subprocess.Popen(
                [sys.executable, self.bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.last_restart_time = datetime.now()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False
    
    def stop_bot(self):
        """Stop the bot process gracefully"""
        if self.process and self.process.poll() is None:
            logger.info("🛑 Stopping bot...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Bot didn't terminate, killing...")
                self.process.kill()
    
    def monitor_bot(self):
        """Monitor the bot process and restart if needed"""
        while True:
            if self.process and self.process.poll() is not None:
                # Bot crashed
                logger.error(f"💥 Bot crashed with code: {self.process.returncode}")
                
                # Check restart limits
                if self.restart_count >= self.max_restarts:
                    logger.critical("🔥 Too many restarts. Waiting 60 seconds...")
                    time.sleep(60)
                    self.restart_count = 0
                
                # Wait before restarting
                logger.info(f"⏳ Waiting {self.restart_delay} seconds before restart...")
                time.sleep(self.restart_delay)
                
                # Restart bot
                if self.start_bot():
                    self.restart_count += 1
                    logger.info(f"✅ Bot restarted (attempt {self.restart_count})")
                else:
                    logger.error("❌ Failed to restart bot")
                    time.sleep(30)
            
            time.sleep(2)  # Check every 2 seconds
    
    def watch_logs(self):
        """Watch and display bot logs in real-time"""
        while True:
            if self.process and self.process.stdout:
                try:
                    line = self.process.stdout.readline()
                    if line:
                        print(f"[BOT] {line.strip()}")
                except:
                    pass
            time.sleep(0.1)
    
    def health_check(self):
        """Periodic health check to ensure bot is responsive"""
        while True:
            if self.process and self.process.poll() is None:
                # Bot is running, check if it's actually working
                # This is a placeholder - you could add actual health checks
                pass
            time.sleep(30)
    
    def run(self):
        """Main supervisor loop"""
        logger.info("=" * 50)
        logger.info("🛡️ Bot Supervisor Started")
        logger.info(f"📜 Bot script: {self.bot_script}")
        logger.info(f"🔄 Max restarts: {self.max_restarts}")
        logger.info("=" * 50)
        
        # Start the bot
        if not self.start_bot():
            logger.critical("❌ Could not start bot initially!")
            return
        
        # Start monitoring threads
        monitor_thread = threading.Thread(target=self.monitor_bot, daemon=True)
        monitor_thread.start()
        
        log_thread = threading.Thread(target=self.watch_logs, daemon=True)
        log_thread.start()
        
        health_thread = threading.Thread(target=self.health_check, daemon=True)
        health_thread.start()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("👋 Shutting down supervisor...")
            self.stop_bot()
            sys.exit(0)


class MessageRecoveryHandler:
    """
    Handles message deletion issues by resetting the update offset.
    This prevents the bot from getting stuck when messages are deleted.
    """
    
    def __init__(self, bot_app):
        self.bot_app = bot_app
        self.last_update_id = 0
        self.consecutive_errors = 0
        
    def reset_connection(self):
        """Reset the bot's connection to Telegram"""
        logger.warning("🔄 Resetting bot connection...")
        try:
            # Get current updates to find the last offset
            updates = self.bot_app.bot.get_updates(offset=self.last_update_id + 1, timeout=1)
            if updates:
                self.last_update_id = updates[-1].update_id
                logger.info(f"✅ Reset complete. Last update ID: {self.last_update_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Reset failed: {e}")
            return False
    
    def handle_error(self, error):
        """Handle different types of errors"""
        error_str = str(error)
        
        # Check for message deletion errors
        if "message to delete not found" in error_str or "message not found" in error_str:
            logger.warning("📝 Message deletion detected - resetting connection")
            self.consecutive_errors += 1
            if self.consecutive_errors > 3:
                self.reset_connection()
                self.consecutive_errors = 0
        else:
            self.consecutive_errors = 0


# Patch for your bot.py to make it crash-proof
BOT_PATCH = """
# ========== CRASH PROTECTION PATCH ==========
import signal
import sys
import traceback

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("🔥 UNCAUGHT EXCEPTION:", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
    print("🔄 Bot will restart automatically...", file=sys.stderr)

sys.excepthook = global_exception_handler

def signal_handler(sig, frame):
    print("\\n👋 Received signal to stop. Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ===========================================
"""

def patch_bot_file():
    """Add crash protection to bot.py if not already present"""
    bot_file = 'bot.py'
    
    try:
        with open(bot_file, 'r') as f:
            content = f.read()
        
        # Check if already patched
        if "CRASH PROTECTION PATCH" not in content:
            # Add patch at the top after imports
            lines = content.split('\n')
            import_section_end = 0
            
            for i, line in enumerate(lines):
                if 'import' in line and '#' not in line[:5]:
                    import_section_end = i
            
            # Insert patch after imports
            lines.insert(import_section_end + 1, BOT_PATCH)
            
            with open(bot_file, 'w') as f:
                f.write('\n'.join(lines))
            
            logger.info("✅ Added crash protection to bot.py")
        else:
            logger.info("✓ bot.py already has crash protection")
            
    except Exception as e:
        logger.error(f"❌ Failed to patch bot.py: {e}")


if __name__ == "__main__":
    # Patch bot.py first
    patch_bot_file()
    
    # Start supervisor
    supervisor = BotSupervisor(
        bot_script='bot.py',
        max_restarts=10,
        restart_delay=5
    )
    
    try:
        supervisor.run()
    except KeyboardInterrupt:
        logger.info("👋 Supervisor stopped by user")
    except Exception as e:
        logger.critical(f"💥 Supervisor crashed: {e}")
        time.sleep(5)
        # Restart supervisor itself
        os.execv(sys.executable, [sys.executable] + sys.argv)