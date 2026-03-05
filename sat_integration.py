"""
SAT Integration Module - Connects SAT features to the main bot
"""

from telegram.ext import CommandHandler
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
    app.add_handler(CommandHandler("trig-solve", sat_commands.trig_solve_command))
    
    # Complex Numbers
    app.add_handler(CommandHandler("complex", sat_commands.complex_command))
    app.add_handler(CommandHandler("complex-polar", sat_commands.complex_polar_command))
    
    # Geometry
    app.add_handler(CommandHandler("circle-area", sat_commands.circle_area_command))
    app.add_handler(CommandHandler("circle-circ", sat_commands.circle_circumference_command))
    app.add_handler(CommandHandler("sphere-volume", sat_commands.sphere_volume_command))
    app.add_handler(CommandHandler("cylinder-volume", sat_commands.cylinder_volume_command))
    app.add_handler(CommandHandler("rectangle-area", sat_commands.rectangle_area_command))
    app.add_handler(CommandHandler("triangle-area", sat_commands.triangle_area_command))
    app.add_handler(CommandHandler("pythagorean", sat_commands.pythagorean_command))
    
    # Test Generator (Premium)
    app.add_handler(CommandHandler("test", sat_commands.test_command))
    
    print("✅ SAT features loaded successfully!")