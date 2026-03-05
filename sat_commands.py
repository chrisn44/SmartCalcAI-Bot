"""
SAT Commands Module - Telegram command handlers for SAT-level features
"""

from telegram import Update
from telegram.ext import ContextTypes
import history
import sat_calculator
from bot import reply_with_steps, enforce_limit, premium_required  # Import from main bot

# ========== ADVANCED ALGEBRA COMMANDS ==========

async def quadratic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quadratic command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Quadratic Equation Solver**\n\n"
            "Usage: `/quadratic <equation>`\n"
            "Examples:\n"
            "• `/quadratic 2x^2 + 3x - 5 = 0`\n"
            "• `/quadratic x^2 - 4 = 0`\n"
            "• `/quadratic x^2 + 2x + 5 = 0`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, solutions = sat_calculator.solve_quadratic(text)
        if solutions is not None:
            result_str = ", ".join([str(s) for s in solutions])
            await reply_with_steps(update, steps, result_str)
            history.add_history(update.effective_user.id, "quadratic", text, result_str)
        else:
            await update.message.reply_text("❌ Could not solve the equation.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def rational_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rational command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Rational Equation Solver**\n\n"
            "Usage: `/rational <equation>`\n"
            "Examples:\n"
            "• `/rational (x+1)/(x-2) = 3`\n"
            "• `/rational 2/(x+1) = 4/(x-3)`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, solutions = sat_calculator.solve_rational(text)
        if solutions is not None:
            result_str = ", ".join([str(s) for s in solutions])
            await reply_with_steps(update, steps, result_str)
            history.add_history(update.effective_user.id, "rational", text, result_str)
        else:
            await update.message.reply_text("❌ Could not solve the equation.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== PERCENTAGES & RATIOS COMMANDS ==========

async def percent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /percent command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Percentage Calculator**\n\n"
            "Usage: `/percent <expression>`\n"
            "Examples:\n"
            "• `/percent 15percent of 200`\n"
            "• `/percent what percent is 30 of 150`\n"
            "• `/percent 25 is 20percent of what`",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Simple parsing for common patterns
        text_lower = text.lower()
        
        if 'percent of' in text_lower:
            # Find percent of number: "15percent of 200"
            import re
            match = re.search(r'(\d+)percent\s+of\s+(\d+)', text_lower)
            if match:
                percent = float(match.group(1))
                whole = float(match.group(2))
                steps, result = sat_calculator.calculate_percentage(part=None, whole=whole, percent=percent)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "percent", text, str(result))
                return
                
        elif 'what percent' in text_lower:
            # Find what percent: "30 is what percent of 150"
            match = re.search(r'(\d+)\s+is\s+what\s+percent\s+of\s+(\d+)', text_lower)
            if match:
                part = float(match.group(1))
                whole = float(match.group(2))
                steps, result = sat_calculator.calculate_percentage(part=part, whole=whole, percent=None)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "percent", text, str(result))
                return
                
        else:
            await update.message.reply_text(
                "❌ Format not recognized.\n"
                "Try: `/percent 15percent of 200` or `/percent what percent is 30 of 150`"
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def ratio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ratio command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Proportion Solver**\n\n"
            "Usage: `/ratio <proportion>`\n"
            "Examples:\n"
            "• `/ratio 3:4 = 12:x`\n"
            "• `/ratio 5:2 = x:8`\n"
            "• `/ratio 3/4 = 12/x`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, result = sat_calculator.solve_proportion(text)
        if result is not None:
            await reply_with_steps(update, steps, result)
            history.add_history(update.effective_user.id, "ratio", text, str(result))
        else:
            await update.message.reply_text("❌ Could not solve the proportion.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== PROBABILITY COMMANDS ==========

async def prob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /prob command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "🎲 **Probability Calculator**\n\n"
            "Usage: `/prob <favorable> <total>`\n"
            "Example: `/prob 3 10` (probability of 3 out of 10)",
            parse_mode='Markdown'
        )
        return
    
    try:
        favorable = float(args[0])
        total = float(args[1])
        description = ' '.join(args[2:]) if len(args) > 2 else ""
        
        steps, result = sat_calculator.calculate_probability(favorable, total, description)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "prob", f"{favorable} {total}", str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== TRIGONOMETRY COMMANDS ==========

async def trig_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trig command (was /trig-solve)"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Trigonometric Equation Solver**\n\n"
            "Usage: `/trig <equation>`\n"
            "Examples:\n"
            "• `/trig sin(x) = 0.5`\n"
            "• `/trig cos(x) = 0`\n"
            "• `/trig tan(x) = 1`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, solutions = sat_calculator.solve_trig_equation(text)
        if solutions is not None:
            result_str = ", ".join([str(s) for s in solutions])
            await reply_with_steps(update, steps, result_str)
            history.add_history(update.effective_user.id, "trig", text, result_str)
        else:
            await update.message.reply_text("❌ Could not solve the equation.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== COMPLEX NUMBERS COMMANDS ==========

async def complex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /complex command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "🔢 **Complex Number Arithmetic**\n\n"
            "Usage: `/complex <expression>`\n"
            "Examples:\n"
            "• `/complex (3+2i) + (1-4i)`\n"
            "• `/complex (2+3i) * (1-i)`\n"
            "• `/complex (5+2i) / (1+i)`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, result = sat_calculator.complex_arithmetic(text)
        if result is not None:
            await reply_with_steps(update, steps, result)
            history.add_history(update.effective_user.id, "complex", text, str(result))
        else:
            await update.message.reply_text("❌ Could not evaluate expression.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def polar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /polar command (was /complex-polar)"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "🔢 **Complex to Polar Form**\n\n"
            "Usage: `/polar <complex>`\n"
            "Example: `/polar 1+i`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, result = sat_calculator.complex_to_polar(text)
        if result is not None:
            r, theta = result
            result_str = f"r = {r}, θ = {theta} rad"
            await reply_with_steps(update, steps, result_str)
            history.add_history(update.effective_user.id, "polar", text, result_str)
        else:
            await update.message.reply_text("❌ Could not convert to polar form.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== GEOMETRY COMMANDS ==========

async def circle_area_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /circle_area command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "⭕ **Circle Area**\n\n"
            "Usage: `/circle_area <radius>`\n"
            "Example: `/circle_area 5`",
            parse_mode='Markdown'
        )
        return
    
    try:
        radius = float(args[0])
        steps, result = sat_calculator.circle_area(radius)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "circle_area", str(radius), str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def circle_circumference_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /circle_circ command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "⭕ **Circle Circumference**\n\n"
            "Usage: `/circle_circ <radius>`\n"
            "Example: `/circle_circ 5`",
            parse_mode='Markdown'
        )
        return
    
    try:
        radius = float(args[0])
        steps, result = sat_calculator.circle_circumference(radius)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "circle_circ", str(radius), str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def sphere_volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sphere_volume command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "🌐 **Sphere Volume**\n\n"
            "Usage: `/sphere_volume <radius>`\n"
            "Example: `/sphere_volume 5`",
            parse_mode='Markdown'
        )
        return
    
    try:
        radius = float(args[0])
        steps, result = sat_calculator.sphere_volume(radius)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "sphere_volume", str(radius), str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def cylinder_volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cylinder_volume command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "🥫 **Cylinder Volume**\n\n"
            "Usage: `/cylinder_volume <radius> <height>`\n"
            "Example: `/cylinder_volume 5 10`",
            parse_mode='Markdown'
        )
        return
    
    try:
        radius = float(args[0])
        height = float(args[1])
        steps, result = sat_calculator.cylinder_volume(radius, height)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "cylinder_volume", f"{radius} {height}", str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def rectangle_area_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rectangle_area command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📏 **Rectangle Area**\n\n"
            "Usage: `/rectangle_area <length> <width>`\n"
            "Example: `/rectangle_area 5 3`",
            parse_mode='Markdown'
        )
        return
    
    try:
        length = float(args[0])
        width = float(args[1])
        steps, result = sat_calculator.rectangle_area(length, width)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "rectangle_area", f"{length} {width}", str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def triangle_area_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /triangle_area command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📐 **Triangle Area**\n\n"
            "Usage: `/triangle_area <base> <height>`\n"
            "Example: `/triangle_area 6 4`",
            parse_mode='Markdown'
        )
        return
    
    try:
        base = float(args[0])
        height = float(args[1])
        steps, result = sat_calculator.triangle_area(base, height)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "triangle_area", f"{base} {height}", str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def pythagorean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pythagorean command"""
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "📐 **Pythagorean Theorem**\n\n"
            "Usage: `/pythagorean <a|b|c> <value> ...`\n"
            "Examples:\n"
            "• `/pythagorean a=3 b=4` (find c)\n"
            "• `/pythagorean a=5 c=13` (find b)\n"
            "• `/pythagorean b=8 c=17` (find a)",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Parse arguments
        a = b = c = None
        for arg in args:
            if '=' in arg:
                side, val = arg.split('=')
                if side == 'a':
                    a = float(val)
                elif side == 'b':
                    b = float(val)
                elif side == 'c':
                    c = float(val)
        
        steps, result = sat_calculator.pythagorean_theorem(a, b, c)
        if result is not None:
            await reply_with_steps(update, steps, result)
            history.add_history(update.effective_user.id, "pythagorean", ' '.join(args), str(result))
        else:
            await update.message.reply_text("❌ Could not solve. Provide exactly two sides.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== TEST GENERATOR (PREMIUM) ==========

@premium_required
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /test command - Premium only"""
    args = context.args
    topic = args[0] if args else "algebra"
    difficulty = args[1] if len(args) > 1 else "medium"
    
    steps, problem = sat_calculator.generate_test(topic, difficulty)
    
    if problem:
        msg = "\n".join(steps)
        await update.message.reply_text(msg, parse_mode='Markdown')
        history.add_history(update.effective_user.id, "test", topic, str(problem))
    else:
        await update.message.reply_text("❌ Could not generate test.")
