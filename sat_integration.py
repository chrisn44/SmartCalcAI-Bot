"""
SAT Integration Module - Connects SAT features to the main bot
Includes spam protection and owner management commands
"""

from telegram.ext import CommandHandler, MessageHandler, filters
import sat_commands

def add_sat_handlers(app):
    """
    Add all SAT command handlers to the bot application
    Call this from your main bot.py
    """
    
    # Advanced Algebra
    app.add_handler(CommandHandler("quadratic", sat_commands.quadratic_command))
    app.add_handler(CommandHandler("rational", sat_commands.rational_command))
    
    # Percentages & Ratios
    app.add_handler(CommandHandler("percent", sat_commands.percent_command))
    app.add_handler(CommandHandler("ratio", sat_commands.ratio_command))
    
    # Probability
    app.add_handler(CommandHandler("prob", sat_commands.prob_command))
    
    # Trigonometry
    app.add_handler(CommandHandler("trig", sat_commands.trig_command))
    
    # Complex Numbers
    app.add_handler(CommandHandler("complex", sat_commands.complex_command))
    app.add_handler(CommandHandler("polar", sat_commands.polar_command))
    
    # Geometry
    app.add_handler(CommandHandler("circle_area", sat_commands.circle_area_command))
    app.add_handler(CommandHandler("circle_circ", sat_commands.circle_circumference_command))
    app.add_handler(CommandHandler("sphere_volume", sat_commands.sphere_volume_command))
    app.add_handler(CommandHandler("cylinder_volume", sat_commands.cylinder_volume_command))
    app.add_handler(CommandHandler("rectangle_area", sat_commands.rectangle_area_command))
    app.add_handler(CommandHandler("triangle_area", sat_commands.triangle_area_command))
    app.add_handler(CommandHandler("pythagorean", sat_commands.pythagorean_command))
    
    # Vector Calculus
    app.add_handler(CommandHandler("gradient", sat_commands.gradient_command))
    app.add_handler(CommandHandler("divergence", sat_commands.divergence_command))
    app.add_handler(CommandHandler("curl", sat_commands.curl_command))
    
    # Curve Fitting (Premium)
    app.add_handler(CommandHandler("fit", sat_commands.fit_command))
    
    # PDF Export (Premium)
    app.add_handler(CommandHandler("exportpdf", sat_commands.exportpdf_command))
    
    # Test Generator (Premium)
    app.add_handler(CommandHandler("test", sat_commands.test_command))
    
    # 👑 Owner Statistics
    app.add_handler(CommandHandler("botstats", sat_commands.botstats_command))
    
    # ========== SPAM PROTECTION COMMANDS (Owner Only) ==========
    try:
        from spam_commands import (
            spam_stats_command,
            unban_user_command,
            unban_chat_command,
            adjust_limits_command,
            whitelist_user_command
        )
        
        app.add_handler(CommandHandler("spamstats", spam_stats_command))
        app.add_handler(CommandHandler("unbanuser", unban_user_command))
        app.add_handler(CommandHandler("unbanchat", unban_chat_command))
        app.add_handler(CommandHandler("setlimit", adjust_limits_command))
        app.add_handler(CommandHandler("whitelist", whitelist_user_command))
        
        print("✅ Spam protection commands registered")
    except ImportError as e:
        print(f"⚠️ Spam protection module not available: {e}")
    except Exception as e:
        print(f"⚠️ Error registering spam commands: {e}")
    
    # ========== PHOTO EQUATION SOLVER (Premium) ==========
    try:
        from photo_solver_photo_handler import handle_photo
        # Register for all possible image types
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        print("✅ Photo handler registered for PHOTO")
        
        # Also handle documents that are images
        app.add_handler(MessageHandler(filters.Document.IMAGE, handle_photo))
        print("✅ Photo handler registered for Document.IMAGE")
        
    except ImportError as e:
        print(f"⚠️ Photo solver module not available: {e}")
    except Exception as e:
        print(f"⚠️ Error registering photo handler: {e}")
    
    # Command to guide users to send photos
    try:
        app.add_handler(CommandHandler("solvephoto", sat_commands.solvephoto_command))
        print("✅ /solvephoto command registered")
    except Exception as e:
        print(f"⚠️ Error registering solvephoto command: {e}")
    
    # ========== MESSAGE FILTER (Spam Prevention) ==========
    try:
        from message_filter import SpamFilter
        # This will be handled in the main message handler in bot.py
        print("✅ Spam filter initialized")
    except ImportError as e:
        print(f"⚠️ Spam filter not available: {e}")
    
    print("✅ SAT features loaded successfully!")
    print("   • 20+ SAT math commands")
    print("   • Vector calculus: gradient, divergence, curl")
    print("   • Premium features: fit, exportpdf, test, photo solver")
    print("   • Spam protection: /spamstats, /unbanuser, /unbanchat, /setlimit")
