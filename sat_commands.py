"""
SAT Commands Module - Telegram command handlers for SAT-level features
"""

from telegram import Update
from telegram.ext import ContextTypes
import history
import sat_calculator
import config  # added for owner check
from bot import reply_with_steps, enforce_limit, premium_required  # Import from main bot
import os

# ========== OWNER UTILITY ==========
def is_owner(user_id):
    """Check if user is the bot owner."""
    return user_id == config.OWNER_ID

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
            "• `/quadratic 2x^2 + 7x - 15 = 0`\n"
            "• `/quadratic x^2 + 2x + 5 = 0`",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Keep original for history, but clean for parsing
        original_text = text
        clean_text = text.replace(' ', '')
        
        steps, solutions = sat_calculator.solve_quadratic(clean_text)
        
        if solutions is not None:
            if len(solutions) == 2:
                result_str = f"x₁ = {solutions[0]}, x₂ = {solutions[1]}"
            elif len(solutions) == 1:
                result_str = f"x = {solutions[0]} (double root)"
            else:
                result_str = ", ".join([str(s) for s in solutions])
            
            await reply_with_steps(update, steps, result_str)
            history.add_history(update.effective_user.id, "quadratic", original_text, result_str)
        else:
            # Send the steps even if no solutions
            if steps and len(steps) > 1:
                steps_text = "\n".join(steps)
                await update.message.reply_text(steps_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Could not solve the equation.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n\nTry: `/quadratic 2x^2+7x-15=0`")

async def rational_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /rational command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Rational Equation Solver**\n\n"
            "Usage: `/rational <equation>`\n"
            "Examples:\n"
            "• `/rational (x+2)/(x-3) = 4`\n"
            "• `/rational (2x+1)/(x-1) = (x+4)/(x+2)`\n"
            "• `/rational 2/(x+1) = 3/(x-2)`",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Remove spaces for parsing
        clean_text = text.replace(' ', '')
        
        steps, solutions = sat_calculator.solve_rational(clean_text)
        
        if solutions is not None and len(solutions) > 0:
            result_str = ", ".join([f"{s:.4f}" if isinstance(s, (int, float)) else str(s) for s in solutions])
            await reply_with_steps(update, steps, result_str)
            history.add_history(update.effective_user.id, "rational", text, result_str)
        else:
            # Send the steps even if no solutions
            if steps and len(steps) > 1:
                steps_text = "\n".join(steps)
                await update.message.reply_text(steps_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Could not solve the equation.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n\nTry: `/rational (2x+1)/(x-1)=(x+4)/(x+2)`")

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
            "• `/percent 15% of 200`\n"
            "• `/percent what percent is 30 of 150`\n"
            "• `/percent 25 is 20% of what`",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Simple parsing for common patterns
        text_lower = text.lower()
        
        if '%' in text_lower or 'percent' in text_lower:
            import re
            # Handle "15% of 200"
            match = re.search(r'(\d+)%?\s+of\s+(\d+)', text_lower)
            if match:
                percent = float(match.group(1))
                whole = float(match.group(2))
                steps, result = sat_calculator.calculate_percentage(part=None, whole=whole, percent=percent)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "percent", text, str(result))
                return
            
            # Handle "what percent is 30 of 150"
            match = re.search(r'what\s+percent\s+is\s+(\d+)\s+of\s+(\d+)', text_lower)
            if match:
                part = float(match.group(1))
                whole = float(match.group(2))
                steps, result = sat_calculator.calculate_percentage(part=part, whole=whole, percent=None)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "percent", text, str(result))
                return
            
            # Handle "25 is 20% of what"
            match = re.search(r'(\d+)\s+is\s+(\d+)%\s+of\s+what', text_lower)
            if match:
                part = float(match.group(1))
                percent = float(match.group(2))
                steps, result = sat_calculator.calculate_percentage(part=part, whole=None, percent=percent)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "percent", text, str(result))
                return
                
        await update.message.reply_text(
            "❌ Format not recognized.\n"
            "Try: `/percent 15% of 200` or `/percent what percent is 30 of 150`"
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
        # Remove spaces for parsing
        clean_text = text.replace(' ', '')
        steps, result = sat_calculator.solve_proportion(clean_text)
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
    """Handle /trig command"""
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
        # Remove spaces for parsing
        clean_text = text.replace(' ', '')
        steps, solutions = sat_calculator.solve_trig_equation(clean_text)
        if solutions is not None:
            result_str = ", ".join([str(s) for s in solutions])
            await reply_with_steps(update, steps, result_str)
            history.add_history(update.effective_user.id, "trig", text, result_str)
        else:
            await update.message.reply_text("❌ Could not solve the equation.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== VECTOR CALCULUS COMMANDS ==========

async def gradient_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gradient command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Gradient Calculator**\n\n"
            "Usage: `/gradient <scalar field>`\n"
            "Examples:\n"
            "• `/gradient x^2*y + y*z`\n"
            "• `/gradient sin(x)*cos(y)`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, result = sat_calculator.gradient(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "gradient", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def divergence_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /divergence command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Divergence Calculator**\n\n"
            "Usage: `/divergence [F_x, F_y, F_z]`\n"
            "Examples:\n"
            "• `/divergence [x*y, y*z, z*x]`\n"
            "• `/divergence x*y, y*z, z*x`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, result = sat_calculator.divergence(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "divergence", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def curl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /curl command"""
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Curl Calculator**\n\n"
            "Usage: `/curl [F_x, F_y, F_z]`\n"
            "Examples:\n"
            "• `/curl [x*y, y*z, z*x]`\n"
            "• `/curl x*y, y*z, z*x`",
            parse_mode='Markdown'
        )
        return
    
    try:
        steps, result = sat_calculator.curl(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "curl", text, str(result))
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
    """Handle /polar command"""
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
    if len(args) < 2:
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

# ========== CURVE FITTING (Premium) ==========

@premium_required
async def fit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fit command - Premium only"""
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "📈 **Curve Fitting (Premium)**\n\n"
            "Usage: `/fit <function> <x_values> <y_values>`\n\n"
            "**Examples:**\n"
            "• `/fit a*exp(b*x)+c 1,2,3 2,4,8`\n"
            "• `/fit a*x+b 1,2,3,4 2,4,6,8`\n"
            "• `/fit a*x^2+b*x+c 0,1,2 0,1,4`\n\n"
            "**Parameters:**\n"
            "• Use letters (a,b,c,etc.) for parameters to fit\n"
            "• Use `x` as the variable\n"
            "• Separate values with commas",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Parse arguments
        func_template = args[0]
        x_data = args[1]
        y_data = args[2]
        
        steps, results = sat_calculator.curve_fit_function(func_template, x_data, y_data)
        
        if results:
            # Send steps as text
            steps_text = "\n".join(steps)
            await update.message.reply_text(steps_text, parse_mode='Markdown')
            
            # Send the plot if available
            if 'plot' in results:
                await update.message.reply_photo(
                    photo=results['plot'],
                    caption=f"📈 Fitted curve: {results['fitted_function']}"
                )
            
            # Store results in history
            result_summary = f"R²={results['r_squared']:.4f}, params={results['parameters']}"
            history.add_history(update.effective_user.id, "fit", 
                               f"{func_template} {x_data} {y_data}", result_summary)
        else:
            await update.message.reply_text("❌ Curve fitting failed. Check your function and data.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== PDF EXPORT (Premium) ==========

@premium_required
async def exportpdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /exportpdf command - Premium only"""
    user_id = update.effective_user.id
    
    # Send initial status
    status_msg = await update.message.reply_text("📄 **Generating PDF report...**", parse_mode='Markdown')
    
    try:
        # Get user's calculation history
        history_data = history.get_history(user_id, limit=50)  # Get last 50 calculations
        
        # Get any current calculations to include (optional)
        calculations = []
        
        steps, pdf_path = sat_calculator.export_to_pdf(user_id, history_data, calculations)
        
        if pdf_path and os.path.exists(pdf_path):
            # Send the PDF file
            with open(pdf_path, 'rb') as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=f"calc_history_{user_id}.pdf",
                    caption="📊 **Your Calculation History**\n\nGenerated by SmartCalcAI Bot"
                )
            
            # Delete the status message
            await status_msg.delete()
            
            # Clean up the temporary file
            try:
                os.remove(pdf_path)
            except:
                pass
            
            # Log success
            history.add_history(user_id, "exportpdf", "", "PDF exported successfully")
        else:
            await status_msg.edit_text("❌ Failed to generate PDF.")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ Error generating PDF: {e}")

# ========== TEST GENERATOR (Premium) ==========

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

# ========== PHOTO EQUATION SOLVER (Premium) ==========

@premium_required
async def solvephoto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guide user to send a photo for equation solving"""
    await update.message.reply_text(
        "📸 **Photo Equation Solver**\n\n"
        "Send me a photo of any mathematical equation, and I'll solve it step‑by‑step!\n\n"
        "**Tips for best results:**\n"
        "• Good lighting\n"
        "• Clear handwriting or printed text\n"
        "• Square/cropped to the equation\n\n"
        "Ready? Send me a photo now!",
        parse_mode='Markdown'
    )

# ========== OWNER STATISTICS COMMAND ==========

async def botstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to get real bot statistics."""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ This command is only for bot owner.")
        return

    try:
        # Import the real stats module
        from sat_stats import get_stats
        stats = get_stats()
        
        await update.message.reply_text(
            f"👑 **Bot Statistics**\n\n"
            f"📊 **Total users:** `{stats['total_users']}`\n"
            f"💎 **Premium users:** `{stats['premium_users']}`\n"
            f"🧮 **Total calculations:** `{stats['total_calculations']}`",
            parse_mode='Markdown'
        )
        history.add_history(user_id, "botstats", "", str(stats))
    except ImportError:
        await update.message.reply_text(
            "❌ Statistics module not found.\n"
            "Please make sure `sat_stats.py` exists in your bot directory."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching stats: {e}")
