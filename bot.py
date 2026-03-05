#!/usr/bin/env python3
"""
SmartCalcAI Bot - Complete Telegram Math Assistant
All features included: free tier, premium with Stars, BYO LLM key
"""

import os
import logging
import threading
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, PreCheckoutQueryHandler, CallbackQueryHandler
)

# Add Flask for Railway web server
try:
    from flask import Flask
    WEB_SERVER = True
except ImportError:
    WEB_SERVER = False
    print("Flask not installed - web server disabled")

import config
import calculator
import graphing
import units
import matrix
import stats
import history
from llm_integration import LLMHandler, interpret_math_query

# Flask web server for Railway
if WEB_SERVER:
    web_app = Flask(__name__)
    
    @web_app.route('/')
    def home():
        return "SmartCalcAI Bot is running!"
    
    @web_app.route('/health')
    def health():
        return "OK", 200
    
    def run_web_server():
        port = int(os.getenv("PORT", 8080))
        web_app.run(host="0.0.0.0", port=port)

# Initialize database
history.init_db()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== Helper Functions ==========

def is_owner(user_id):
    """Check if user is the bot owner."""
    return user_id == config.OWNER_ID

async def reply_with_steps(update, steps, result=None):
    """Send steps as formatted text."""
    msg = ""
    for s in steps:
        # Clean up any duplicate formatting
        s = s.replace('**Result:**', '').replace('Result:', '')
        msg += s + "\n"
    if result is not None and not isinstance(result, str):
        # Only add result if it's not already in steps
        result_str = str(result)
        # Check if result is already in the last step
        if result_str not in msg:
            msg += f"\n**Result:** `{result_str}`"
    # Remove any potential double spaces or formatting issues
    msg = msg.replace('\n\n', '\n').strip()
    try:
        await update.message.reply_text(msg, parse_mode='Markdown')
    except:
        # Fallback to plain text if Markdown fails
        plain_msg = msg.replace('*', '').replace('`', '').replace('_', '')
        await update.message.reply_text(plain_msg)

def check_free_limit(user_id):
    """Return True if user is premium or under daily limit."""
    if is_owner(user_id):  # Owner always has access
        return True
    if history.is_premium(user_id):
        return True
    if config.FREE_DAILY_LIMIT == 0:
        return True
    count = history.get_daily_count(user_id)
    return count < config.FREE_DAILY_LIMIT

async def enforce_limit(update: Update):
    """Check and enforce free tier limit."""
    user_id = update.effective_user.id
    
    # Owner bypass - always unlimited
    if is_owner(user_id):
        return True
    
    # Premium users bypass
    if history.is_premium(user_id):
        return True
    
    # Check daily limit for free users
    if config.FREE_DAILY_LIMIT == 0:
        return True
    
    count = history.get_daily_count(user_id)
    if count < config.FREE_DAILY_LIMIT:
        return True
    
    # User has exceeded limit
    keyboard = [[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="show_buy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"⚠️ You've used your {config.FREE_DAILY_LIMIT} free calculations today.\n"
        "Upgrade to premium for unlimited access!",
        reply_markup=reply_markup
    )
    return False

def premium_required(func):
    """Decorator for premium-only commands."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not history.is_premium(user_id) and not is_owner(user_id):
            keyboard = [[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="show_buy")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🚫 This feature is for premium users only.\n"
                "Upgrade to unlock 3D plots, system solvers, PDF exports, and more!",
                reply_markup=reply_markup
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ========== Command Handlers ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with all commands."""
    user_id = update.effective_user.id
    owner_note = " (Owner)" if is_owner(user_id) else ""
    
    welcome = f"""
🧠 **SmartCalcAI Bot – The Ultimate Math Assistant**{owner_note}

**✨ Free Features** (10 calculations/day):
• `/calc 2+2` – Basic calculations
• `/derive x^3*sin(x)` – Derivatives with steps
• `/integrate x^2 dx` – Indefinite integrals
• `/integrate x^2 from 0 to 1` – Definite integrals
• `/limit sin(x)/x as x 0` – Limits
• `/series exp(x) about 0` – Series expansion
• `/ode y'' + y = 0` – Differential equations
• `/laplace sin(t)` – Laplace transforms
• `/fourier exp(-x^2)` – Fourier transforms
• `/gradient x^2*y` – Gradient
• `/divergence [x*y, y*z, z*x]` – Divergence
• `/curl [x*y, y*z, z*x]` – Curl
• `/fsolve x^2-2=0` – Numerical root finding
• `/quad x^2 0 1` – Numerical integration
• `/minimize x^2+2x+1` – Minimization
• `/plot sin(x) from -10 to 10` – 2D plotting
• `/plotmulti sin(x), cos(x) from 0 to 10` – Multiple plots
• `/matrix [[1,2],[3,4]] * [[0,1],[1,0]]` – Matrix multiply
• `/inverse [[1,2],[3,4]]` – Matrix inverse
• `/det [[1,2],[3,4]]` – Determinant
• `/transpose [[1,2],[3,4]]` – Matrix transpose
• `/eigen [[1,2],[3,4]]` – Eigenvalues
• `/unit 100 km to miles` – Unit conversion
• `/stat 1,2,3,4,5` – Basic statistics
• `/regress 1,2,3 4,5,6` – Linear regression
• `/ttest 1,2,3,4,5 3` – T-test
• `/correlate 1,2,3 4,5,6` – Correlation
• `/history` – Your last calculations

**💎 Premium Features** (unlock with /buy):
• `/plot3d x*y from -5 to 5 for -5 to 5` – 3D surface plots
• `/system x+y=5, 2x-y=1 for x,y` – System solver
• `/fit a*exp(b*x)+c 1,2,3 2,4,8` – Curve fitting
• `/exportpdf` – Export as PDF
• `/share calc_id` – Share calculations
• `/save func1 x**2+1` – Save custom functions
• `/list` – List saved functions
• No daily limits, priority processing

**🔑 Bring Your Own LLM**:
• `/setkey openai sk-...` – Store your API key (encrypted)
• `/checkkey` – Check key status
• `/removekey` – Remove key

**💰 Buy Premium**:
• `/buy` – See subscription options
"""
    
    # Add owner commands if user is owner
    if is_owner(user_id):
        welcome += """
**👑 Owner Commands**:
• `/addpremium <user_id> <days>` – Manually add premium
• `/removepremium <user_id>` – Remove premium
• `/checkuser <user_id>` – Check user status
• `/broadcast <message>` – Send message to all users
• `/stats` – Bot statistics
"""
    
    await update.message.reply_text(welcome, parse_mode='Markdown')

# ========== Basic Math Commands ==========

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    expr = ' '.join(context.args)
    if not expr:
        await update.message.reply_text("Usage: /calc <expression>\nExample: /calc 2+2")
        return
    try:
        steps, result = calculator.evaluate_expression(expr)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "calc", expr, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== Calculus Commands ==========

async def derive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /derive <function> [variable]\nExample: /derive x^3*sin(x)")
        return
    var = 'x'
    if len(args) > 1 and args[-1].isalpha():
        var = args[-1]
        expr_str = ' '.join(args[:-1])
    else:
        expr_str = ' '.join(args)
    try:
        steps, result = calculator.derivative_with_steps(expr_str, var)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "derive", expr_str, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def integrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /integrate <function> [from a to b] [variable]\nExample: /integrate x^2 from 0 to 1")
        return
    try:
        if " from " in text and " to " in text:
            # Parse: "x^2 from 0 to 1"
            parts = text.split(" from ")
            func_part = parts[0].strip()
            
            # Get the range part
            range_part = parts[1].strip()
            range_parts = range_part.split(" to ")
            
            if len(range_parts) != 2:
                await update.message.reply_text("Please specify both lower and upper limits")
                return
                
            a_str = range_parts[0].strip()
            b_str = range_parts[1].strip()
            
            # Check if there's a variable specified after the limits
            var = 'x'
            # Split b_str in case variable is like "1 x"
            b_parts = b_str.split()
            if len(b_parts) > 1:
                b_str = b_parts[0]
                var = b_parts[1]
            
            a, b = float(a_str), float(b_str)
            steps, result = calculator.integral_with_steps(func_part, var, (a, b))
        else:
            # Indefinite integral
            parts = text.split()
            if len(parts) > 1 and parts[-1].isalpha():
                var = parts[-1]
                func_str = ' '.join(parts[:-1])
            else:
                var = 'x'
                func_str = text
            steps, result = calculator.integral_with_steps(func_str, var)
            
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "integrate", text, str(result))
    except ValueError as e:
        await update.message.reply_text(f"❌ Error: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error parsing input. Use format: /integrate x^2 from 0 to 1")

async def limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Limit Calculator**\n\n"
            "Usage: `/limit <function> as <variable> <value>`\n"
            "Examples:\n"
            "• `/limit sin(x)/x as x 0`\n"
            "• `/limit (1+1/x)^x as x infinity`\n"
            "• `/limit ln(x) as x 1`",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Handle "as" keyword
        if " as " in text.lower():
            parts = text.lower().split(" as ")
            func_part = parts[0].strip()
            
            # Get variable and approach value
            var_val = parts[1].strip().split()
            
            if len(var_val) == 2:
                var = var_val[0]
                approach_str = var_val[1]
                
                # Handle special cases like "infinity"
                if approach_str in ['infinity', 'inf', '∞']:
                    approach = float('inf')
                else:
                    try:
                        approach = float(approach_str)
                    except:
                        await update.message.reply_text(f"❌ Invalid approach value: {approach_str}")
                        return
                
                steps, result = calculator.limit_calc(func_part, var, approach)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "limit", text, str(result))
            else:
                await update.message.reply_text(
                    "❌ Invalid format. Use: `/limit sin(x)/x as x 0`\n"
                    "Make sure to include both the variable AND the value.",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                "❌ Missing 'as' keyword.\n"
                "Correct format: `/limit sin(x)/x as x 0`",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n\nTry: `/limit sin(x)/x as x 0`", parse_mode='Markdown')

async def series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📈 **Series Expansion**\n\n"
            "Usage: `/series <function> about <value> [order]`\n"
            "Examples:\n"
            "• `/series exp(x) about 0` (default order 6)\n"
            "• `/series sin(x) about 0 8` (order 8)\n"
            "• `/series ln(1+x) about 0 5`",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Parse: "exp(x) about 0" or "exp(x) about 0 8"
        if " about " in text.lower():
            parts = text.lower().split(" about ")
            func_str = parts[0].strip()
            
            # Get about value and optional order
            about_parts = parts[1].strip().split()
            
            if len(about_parts) >= 1:
                about_val = float(about_parts[0])
                
                # Default order is 6, or use provided order
                order = 6
                if len(about_parts) >= 2:
                    order = int(about_parts[1])
                
                steps, result = calculator.series_expansion(func_str, about=about_val, n=order)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "series", text, str(result))
            else:
                await update.message.reply_text("Please specify the point to expand about.")
        else:
            await update.message.reply_text(
                "❌ Missing 'about' keyword.\n"
                "Correct format: `/series exp(x) about 0`",
                parse_mode='Markdown'
            )
            
    except ValueError as e:
        await update.message.reply_text(f"❌ Error: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error parsing input. Use: /series exp(x) about 0")

# ========== Differential Equations ==========

async def ode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Ordinary Differential Equations**\n\n"
            "**Usage:** `/ode <ODE>`\n\n"
            "**Examples:**\n"
            "• `/ode y'' + y = 0`\n"
            "• `/ode y' = y`\n"
            "• `/ode y'' + 2*y' + y = 0`\n"
            "• `/ode y'' - 4*y = 0`\n\n"
            "**Notes:**\n"
            "• Use `''` for second derivative\n"
            "• Use `'` for first derivative\n"
            "• Always include spaces around operators\n"
            "• Use `*` for multiplication (e.g., `2*y` not `2y`)",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Detect the function name (y, f, etc.)
        import re
        func_match = re.match(r"\s*([a-zA-Z])['\"]", text)
        if func_match:
            func_name = func_match.group(1)
        else:
            func_name = 'y'  # default
        
        steps, solution = calculator.solve_ode(text, func=func_name)
        
        # Format the response nicely
        response = f"{steps[0]}\n\n{steps[1]}"
        await update.message.reply_text(response, parse_mode='Markdown')
        history.add_history(update.effective_user.id, "ode", text, str(solution))
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {e}\n\n"
            f"Try these exact formats:\n"
            f"• `/ode y'' + y = 0`\n"
            f"• `/ode y' = y`\n"
            f"• `/ode y'' + 2*y' + y = 0`\n\n"
            f"Make sure to use spaces around operators!",
            parse_mode='Markdown'
        )

# ========== Transforms ==========

async def laplace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "⚡ **Laplace Transform**\n\n"
            "Usage: `/laplace <function> [variable] [s_var]`\n"
            "Examples:\n"
            "• `/laplace sin(t)`\n"
            "• `/laplace exp(-a*t) t s`",
            parse_mode='Markdown'
        )
        return
    try:
        # Parse arguments
        parts = text.split()
        if len(parts) == 1:
            steps, result = calculator.laplace_transform(parts[0])
        elif len(parts) == 2:
            steps, result = calculator.laplace_transform(parts[0], parts[1])
        else:
            steps, result = calculator.laplace_transform(parts[0], parts[1], parts[2])
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "laplace", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def inverse_laplace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "⚡ **Inverse Laplace Transform**\n\n"
            "Usage: `/invlaplace <function> [s_var] [t_var]`\n"
            "Example: `/invlaplace 1/(s^2+1)`",
            parse_mode='Markdown'
        )
        return
    try:
        parts = text.split()
        if len(parts) == 1:
            steps, result = calculator.inverse_laplace_transform(parts[0])
        elif len(parts) == 2:
            steps, result = calculator.inverse_laplace_transform(parts[0], parts[1])
        else:
            steps, result = calculator.inverse_laplace_transform(parts[0], parts[1], parts[2])
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "invlaplace", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def fourier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Fourier Transform**\n\n"
            "Usage: `/fourier <function> [variable] [k_var]`\n"
            "Example: `/fourier exp(-x^2)`",
            parse_mode='Markdown'
        )
        return
    try:
        parts = text.split()
        if len(parts) == 1:
            steps, result = calculator.fourier_transform(parts[0])
        elif len(parts) == 2:
            steps, result = calculator.fourier_transform(parts[0], parts[1])
        else:
            steps, result = calculator.fourier_transform(parts[0], parts[1], parts[2])
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "fourier", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== Vector Calculus ==========

async def gradient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Gradient**\n\n"
            "Usage: `/gradient <scalar field>`\n"
            "Example: `/gradient x^2*y + y*z`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = calculator.gradient(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "gradient", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def divergence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Divergence**\n\n"
            "Usage: `/divergence [F_x, F_y, F_z]`\n"
            "Example: `/divergence [x*y, y*z, z*x]`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = calculator.divergence(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "divergence", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def curl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📐 **Curl**\n\n"
            "Usage: `/curl [F_x, F_y, F_z]`\n"
            "Example: `/curl [x*y, y*z, z*x]`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = calculator.curl(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "curl", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== Numerical Methods Commands ==========

async def fsolve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "🔢 **Numerical Root Finding**\n\n"
            "Usage: `/fsolve <equation> [guess]`\n"
            "Examples:\n"
            "• `/fsolve x^2-2 1` - solves x² - 2 = 0\n"
            "• `/fsolve x^2-2=0 1` - also works with = sign",
            parse_mode='Markdown'
        )
        return
    
    try:
        # Parse: remove equals sign if present
        expr_text = text
        
        # Handle equations with = sign
        if '=' in expr_text:
            # Split into left and right sides
            parts = expr_text.split('=')
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                
                # Check if right side contains the guess
                right_parts = right.split()
                if len(right_parts) > 1 and right_parts[-1].replace('.','').replace('-','').replace('+','').replace('e','').isdigit():
                    # Last part is guess
                    guess = float(right_parts[-1])
                    right = ' '.join(right_parts[:-1])
                else:
                    guess = 0.0
                
                # Convert to expression = 0: left - right = 0
                expr = f"({left}) - ({right})"
            else:
                await update.message.reply_text("❌ Invalid equation format. Use: equation = 0")
                return
        else:
            # No equals sign - assume =0
            parts = text.split()
            if len(parts) > 1 and parts[-1].replace('.','').replace('-','').replace('+','').replace('e','').isdigit():
                guess = float(parts[-1])
                expr = ' '.join(parts[:-1])
            else:
                guess = 0.0
                expr = text
        
        steps, result = calculator.fsolve(expr, guess=guess)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "fsolve", text, str(result))
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {e}\n\n"
            f"Try these formats:\n"
            f"• `/fsolve x^2-2 1`\n"
            f"• `/fsolve x^2-2=0 1`",
            parse_mode='Markdown'
        )

async def quad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Numerical Integration**\n\n"
            "Usage: `/quad <function> <a> <b>`\n"
            "Example: `/quad x^2 0 1`",
            parse_mode='Markdown'
        )
        return
    try:
        parts = text.split()
        if len(parts) >= 3:
            # Check if last two are numbers
            try:
                a = float(parts[-2])
                b = float(parts[-1])
                expr = ' '.join(parts[:-2])
                steps, result = calculator.quad_integral(expr, a=a, b=b)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "quad", text, str(result))
            except ValueError:
                await update.message.reply_text("❌ Please specify numeric limits a and b")
        else:
            await update.message.reply_text("Usage: /quad <function> <a> <b>")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def minimize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📉 **Minimization**\n\n"
            "Usage: `/minimize <function> [guess]`\n"
            "Example: `/minimize x^2+2x+1 0`",
            parse_mode='Markdown'
        )
        return
    try:
        parts = text.split()
        if len(parts) > 1 and parts[-1].replace('.','').replace('-','').replace('+','').replace('e','').isdigit():
            guess = float(parts[-1])
            expr = ' '.join(parts[:-1])
        else:
            guess = 0.0
            expr = text
        steps, result = calculator.minimize(expr, guess=guess)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "minimize", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== Plotting Commands ==========

async def plot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text or " from " not in text or " to " not in text:
        await update.message.reply_text(
            "📈 **Function Plotter**\n\n"
            "Usage: `/plot <function> from <min> to <max>`\n"
            "Example: `/plot sin(x) from -10 to 10`",
            parse_mode='Markdown'
        )
        return
    try:
        parts = text.split(" from ")
        func_str = parts[0].strip()
        range_part = parts[1].strip()
        range_parts = range_part.split(" to ")
        
        if len(range_parts) != 2:
            await update.message.reply_text("Please specify both min and max values")
            return
            
        xmin = float(range_parts[0].strip())
        xmax = float(range_parts[1].strip())
        
        buf = graphing.plot_function(func_str, xmin, xmax)
        await update.message.reply_photo(photo=buf, caption=f"📈 Plot of {func_str}")
        history.add_history(update.effective_user.id, "plot", text, "Plot generated")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def plotmulti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text or " from " not in text or " to " not in text:
        await update.message.reply_text(
            "📈 **Multiple Function Plotter**\n\n"
            "Usage: `/plotmulti <func1>, <func2> from <min> to <max>`\n"
            "Example: `/plotmulti sin(x), cos(x) from 0 to 10`",
            parse_mode='Markdown'
        )
        return
    try:
        parts = text.split(" from ")
        funcs_str = parts[0].strip()
        range_part = parts[1].strip()
        range_parts = range_part.split(" to ")
        
        if len(range_parts) != 2:
            await update.message.reply_text("Please specify both min and max values")
            return
            
        xmin = float(range_parts[0].strip())
        xmax = float(range_parts[1].strip())
        
        buf = graphing.plot_multiple(funcs_str, xmin, xmax)
        await update.message.reply_photo(photo=buf, caption=f"📈 Multiple functions plot")
        history.add_history(update.effective_user.id, "plotmulti", text, "Plot generated")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== Matrix Commands ==========

async def matrix_mult(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if '*' not in text:
        await update.message.reply_text(
            "🔢 **Matrix Multiplication**\n\n"
            "Usage: `/matrix <A> * <B>`\n"
            "Example: `/matrix [[1,2],[3,4]] * [[0,1],[1,0]]`",
            parse_mode='Markdown'
        )
        return
    try:
        left, right = text.split('*')
        steps, result = matrix.matrix_multiply(left.strip(), right.strip())
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "matrix", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def inverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "🔄 **Matrix Inverse**\n\n"
            "Usage: `/inverse [[1,2],[3,4]]`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = matrix.matrix_inverse(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "inverse", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def determinant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Matrix Determinant**\n\n"
            "Usage: `/det [[1,2],[3,4]]`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = matrix.matrix_determinant(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "det", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def transpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "🔄 **Matrix Transpose**\n\n"
            "Usage: `/transpose [[1,2],[3,4]]`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = matrix.matrix_transpose(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "transpose", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def eigenvalues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Matrix Eigenvalues**\n\n"
            "Usage: `/eigen [[1,2],[3,4]]`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = matrix.matrix_eigenvalues(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "eigen", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== Unit Conversion ==========

async def unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📏 **Unit Converter**\n\n"
            "Usage: `/unit <value> <from_unit> to <to_unit>`\n"
            "Examples:\n"
            "• `/unit 100 km to miles`\n"
            "• `/unit 25 celsius to fahrenheit`\n"
            "• `/unit 10 kg to lb`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, result = units.convert_units(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "unit", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== Statistics Commands ==========

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📊 **Basic Statistics**\n\n"
            "Usage: `/stat <numbers>`\n"
            "Example: `/stat 1,2,3,4,5`",
            parse_mode='Markdown'
        )
        return
    try:
        steps, results = stats.basic_stats(text)
        await reply_with_steps(update, steps)
        history.add_history(update.effective_user.id, "stat", text, str(results))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def regress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📈 **Linear Regression**\n\n"
            "Usage: `/regress <x_values> <y_values>`\n"
            "Example: `/regress 1,2,3 2,4,6`",
            parse_mode='Markdown'
        )
        return
    try:
        x_text = args[0]
        y_text = args[1]
        steps, results = stats.linear_regression(x_text, y_text)
        await reply_with_steps(update, steps)
        history.add_history(update.effective_user.id, "regress", f"{x_text} {y_text}", str(results))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def ttest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📊 **T-Test**\n\n"
            "Usage: `/ttest <data> <population_mean>`\n"
            "Example: `/ttest 1,2,3,4,5 3`",
            parse_mode='Markdown'
        )
        return
    try:
        data_text = args[0]
        popmean = float(args[1])
        steps, results = stats.t_test_onesample(data_text, popmean)
        await reply_with_steps(update, steps)
        history.add_history(update.effective_user.id, "ttest", f"{data_text} {popmean}", str(results))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def correlate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "📊 **Correlation**\n\n"
            "Usage: `/correlate <x_values> <y_values>`\n"
            "Example: `/correlate 1,2,3,4,5 2,4,6,8,10`",
            parse_mode='Markdown'
        )
        return
    try:
        x_text = args[0]
        y_text = args[1]
        steps, results = stats.correlation(x_text, y_text)
        await reply_with_steps(update, steps)
        history.add_history(update.effective_user.id, "correlate", f"{x_text} {y_text}", str(results))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ========== History Command ==========

async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = history.get_history(update.effective_user.id)
    if not rows:
        await update.message.reply_text("No history yet.")
        return
    msg = "*Your last 10 calculations:*\n"
    for cmd, inp, out, ts in rows:
        date = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
        msg += f"• `{cmd}`: {inp} → {out[:50]}... ({date})\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

# ========== Premium Commands ==========

@premium_required
async def plot3d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if not text or " from " not in text or " to " not in text or " for " not in text:
        await update.message.reply_text(
            "📊 **3D Plotter**\n\n"
            "Usage: `/plot3d <f(x,y)> from <xmin> to <xmax> for <ymin> to <ymax>`\n"
            "Examples:\n"
            "• `/plot3d x*y from -5 to 5 for -5 to 5`\n"
            "• `/plot3d sin(x)*cos(y) from -3 to 3 for -3 to 3`\n"
            "• `/plot3d x**2 - y**2 from -2 to 2 for -2 to 2`",
            parse_mode='Markdown'
        )
        return
    try:
        parts = text.split(" from ")
        func_part = parts[0].strip()
        range_parts = parts[1].split(" for ")
        
        if len(range_parts) != 2:
            await update.message.reply_text("❌ Invalid format. Use: from <xmin> to <xmax> for <ymin> to <ymax>")
            return
            
        x_range = range_parts[0].strip()
        y_range = range_parts[1].strip()
        
        x_parts = x_range.split(" to ")
        y_parts = y_range.split(" to ")
        
        if len(x_parts) != 2 or len(y_parts) != 2:
            await update.message.reply_text("❌ Please specify valid ranges (e.g., -5 to 5)")
            return
            
        xmin, xmax = float(x_parts[0]), float(x_parts[1])
        ymin, ymax = float(y_parts[0]), float(y_parts[1])
        
        buf = graphing.plot3d_function(func_part, xmin, xmax, ymin, ymax)
        await update.message.reply_photo(photo=buf, caption=f"📊 3D plot of {func_part}")
        history.add_history(update.effective_user.id, "plot3d", text, "3D plot")
    except ValueError as e:
        await update.message.reply_text(f"❌ Invalid number format: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n\nMake sure your function uses x and y variables correctly.")

@premium_required
async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if " for " not in text:
        await update.message.reply_text(
            "🔢 **System of Equations**\n\n"
            "Usage: `/system <eq1, eq2> for <vars>`\n"
            "Examples:\n"
            "• `/system x+y=5, 2x-y=1 for x,y`\n"
            "• `/system x^2+y^2=25, x-y=1 for x,y`\n"
            "• `/system 2x+3y=8, 4x-5y=2 for x,y`",
            parse_mode='Markdown'
        )
        return
    
    try:
        eqs_str, vars_str = text.split(" for ")
        
        # Clean up the equations string
        eqs_str = eqs_str.strip()
        vars_str = vars_str.strip()
        
        # Remove any extra spaces
        eqs_str = re.sub(r'\s+', ' ', eqs_str)
        
        steps, sol = calculator.solve_system(eqs_str, vars_str)
        
        # Format the solution nicely
        if sol:
            if isinstance(sol, dict):
                # Single solution
                sol_text = "\n".join([f"  {k} = {v}" for k, v in sol.items()])
                formatted_sol = f"✅ **Solution:**\n{sol_text}"
            elif isinstance(sol, list) and len(sol) > 0:
                if isinstance(sol[0], dict):
                    # Multiple solutions
                    formatted_sol = "✅ **Solutions:**"
                    for i, s in enumerate(sol):
                        sol_text = "\n".join([f"    {k} = {v}" for k, v in s.items()])
                        formatted_sol += f"\n\n**Solution {i+1}:**\n{sol_text}"
                else:
                    # List of values
                    formatted_sol = f"✅ **Solution:** {sol}"
            else:
                formatted_sol = f"✅ **Solution:** {sol}"
        else:
            formatted_sol = "❌ No solutions found"
        
        # Send steps first, then the formatted solution
        steps_text = "\n".join(steps)
        await update.message.reply_text(
            f"{steps_text}\n\n{formatted_sol}",
            parse_mode='Markdown'
        )
        history.add_history(update.effective_user.id, "system", text, str(sol))
        
    except ValueError as e:
        await update.message.reply_text(
            f"❌ Error: {e}\n\n"
            f"Try this format:\n"
            f"`/system x+y=5, 2x-y=1 for x,y`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {e}\n\n"
            f"Make sure your equations are properly formatted with = signs.",
            parse_mode='Markdown'
        )

@premium_required
async def fit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    await update.message.reply_text(
        "📈 **Curve Fitting**\n\n"
        "This feature is coming soon! It will allow you to fit data to custom functions.\n"
        "Example: `/fit a*exp(b*x)+c 1,2,3 2,4,8`"
    )
    history.add_history(update.effective_user.id, "fit", text, "Placeholder")

@premium_required
async def exportpdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 **PDF Export**\n\n"
        "This feature is coming soon! It will generate a PDF of your calculation history."
    )
    history.add_history(update.effective_user.id, "exportpdf", "", "PDF export requested")

@premium_required
async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    calc_id = ' '.join(context.args) if context.args else "latest"
    await update.message.reply_text(
        "🔗 **Share Calculation**\n\n"
        "This feature is coming soon! It will allow you to share calculations with others."
    )
    history.add_history(update.effective_user.id, "share", calc_id, "Share requested")

@premium_required
async def save_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "💾 **Save Function**\n\n"
            "Usage: `/save <name> <expression>`\n"
            "Example: `/save f1 x**2 + 1`",
            parse_mode='Markdown'
        )
        return
    name = args[0]
    expr = ' '.join(args[1:])
    if history.save_function(update.effective_user.id, name, expr):
        await update.message.reply_text(f"✅ Function '{name}' saved as {expr}")
        history.add_history(update.effective_user.id, "save", f"{name} {expr}", "Saved")
    else:
        await update.message.reply_text("❌ Failed to save. Premium required?")

@premium_required
async def list_funcs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    funcs = history.list_saved_functions(update.effective_user.id)
    if not funcs:
        await update.message.reply_text("No saved functions.")
        return
    msg = "*Your saved functions:*\n"
    for name, expr, ts in funcs:
        msg += f"• `{name}`: {expr}\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

# ========== Owner Commands ==========

async def owner_add_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to manually add premium to a user."""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ This command is only for bot owner.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "👑 **Owner: Add Premium**\n\n"
            "Usage: `/addpremium <user_id> <days>`\n"
            "Examples:\n"
            "• `/addpremium 123456789 30` - 30 days\n"
            "• `/addpremium 123456789 365` - 1 year\n"
            "• `/addpremium 123456789 3650` - lifetime (10+ years)",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(args[0])
        days = int(args[1])
        
        if days <= 0:
            await update.message.reply_text("❌ Days must be positive.")
            return
        
        expiry = datetime.now() + timedelta(days=days)
        
        # Determine subscription type
        if days >= 3650:  # 10+ years = lifetime
            sub_type = "lifetime"
        elif days >= 365:
            sub_type = "yearly"
        else:
            sub_type = "monthly"
        
        history.set_premium(user_id, expiry, sub_type)
        
        await update.message.reply_text(
            f"✅ **Premium Added!**\n\n"
            f"User ID: `{user_id}`\n"
            f"Duration: {days} days\n"
            f"Expires: {expiry.strftime('%Y-%m-%d')}\n"
            f"Type: {sub_type}",
            parse_mode='Markdown'
        )
        
        # Try to notify the user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🎉 **Congratulations!**\n\n"
                     f"You have been granted premium access for {days} days!\n"
                     f"Expires: {expiry.strftime('%Y-%m-%d')}\n\n"
                     f"Enjoy all premium features!",
                parse_mode='Markdown'
            )
        except:
            logger.info(f"Could not notify user {user_id} about premium grant")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID or days. Use numbers.")

async def owner_remove_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to remove premium from a user."""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ This command is only for bot owner.")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "👑 **Owner: Remove Premium**\n\n"
            "Usage: `/removepremium <user_id>`\n"
            "Example: `/removepremium 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(args[0])
        
        # Check if user has premium
        if not history.is_premium(user_id):
            await update.message.reply_text(f"❌ User {user_id} does not have premium.")
            return
        
        # Remove premium by setting expiry to past
        past_expiry = datetime.now() - timedelta(days=1)
        history.set_premium(user_id, past_expiry, "expired")
        
        await update.message.reply_text(
            f"✅ **Premium Removed!**\n\n"
            f"User ID: `{user_id}`\n"
            f"Premium access has been revoked.",
            parse_mode='Markdown'
        )
        
        # Try to notify the user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"ℹ️ Your premium access has been removed by the administrator.",
                parse_mode='Markdown'
            )
        except:
            logger.info(f"Could not notify user {user_id} about premium removal")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def owner_check_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to check user status."""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ This command is only for bot owner.")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "👑 **Owner: Check User**\n\n"
            "Usage: `/checkuser <user_id>`\n"
            "Example: `/checkuser 123456789`",
            parse_mode='Markdown'
        )
        return
    
    try:
        user_id = int(args[0])
        
        # Check premium status
        is_premium = history.is_premium(user_id)
        expiry = history.get_premium_expiry(user_id)
        
        # Get daily count
        daily_count = history.get_daily_count(user_id)
        
        # Check if has API key
        provider, _ = history.get_user_key(user_id)
        
        msg = f"**User Information:**\n\n"
        msg += f"User ID: `{user_id}`\n"
        msg += f"Premium: {'✅ Yes' if is_premium else '❌ No'}\n"
        
        if is_premium and expiry:
            msg += f"Expires: {expiry.strftime('%Y-%m-%d')}\n"
        
        msg += f"Today's calculations: {daily_count}/{config.FREE_DAILY_LIMIT if not is_premium else '∞'}\n"
        msg += f"API Key: {'✅ ' + provider.capitalize() if provider else '❌ None'}\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def owner_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to broadcast message to all users."""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ This command is only for bot owner.")
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "👑 **Owner: Broadcast**\n\n"
            "Usage: `/broadcast <message>`\n"
            "Example: `/broadcast New features added!`",
            parse_mode='Markdown'
        )
        return
    
    message = ' '.join(args)
    
    await update.message.reply_text(
        f"📢 **Broadcasting to all users...**\n\n"
        f"Message: {message}\n\n"
        f"This feature requires a list of all user IDs from the database.\n"
        f"For now, it's a placeholder.",
        parse_mode='Markdown'
    )

async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to get bot statistics."""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ This command is only for bot owner.")
        return
    
    # This would require additional database queries
    await update.message.reply_text(
        "👑 **Bot Statistics**\n\n"
        "Total users: (coming soon)\n"
        "Premium users: (coming soon)\n"
        "Total calculations: (coming soon)\n\n"
        "This feature requires additional database queries.",
        parse_mode='Markdown'
    )

# ========== API Key Commands ==========

async def setkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "🔑 **Set API Key**\n\n"
            "Usage: `/setkey <provider> <your_api_key>`\n"
            "Providers: `openai`, `gemini`, `claude`\n"
            "Example: `/setkey openai sk-1234567890`",
            parse_mode='Markdown'
        )
        return
    provider = args[0].lower()
    api_key = ' '.join(args[1:])
    if provider not in ['openai', 'gemini', 'claude']:
        await update.message.reply_text("Provider must be openai, gemini, or claude.")
        return
    history.set_user_key(update.effective_user.id, provider, api_key)
    await update.message.reply_text(f"✅ {provider.capitalize()} API key saved securely (encrypted).")

async def checkkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    provider, _ = history.get_user_key(update.effective_user.id)
    if provider:
        await update.message.reply_text(f"🔑 You have a {provider.capitalize()} API key configured.")
    else:
        await update.message.reply_text("❌ No API key configured. Use /setkey to add one.")

async def removekey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.delete_user_key(update.effective_user.id)
    await update.message.reply_text("✅ Your API key has been removed.")

# ========== Payment Handlers ==========

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium subscription options."""
    keyboard = [
        [InlineKeyboardButton("💰 Monthly - 50 Stars", callback_data="buy_monthly")],
        [InlineKeyboardButton("📅 Yearly - 500 Stars (save 16%)", callback_data="buy_yearly")],
        [InlineKeyboardButton("💎 Lifetime - 2000 Stars", callback_data="buy_lifetime")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if already premium
    if history.is_premium(update.effective_user.id):
        expiry = history.get_premium_expiry(update.effective_user.id)
        if expiry:
            await update.message.reply_text(
                f"✨ You already have premium until {expiry.strftime('%Y-%m-%d')}\n"
                "You can extend your subscription below:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "✨ You already have premium! You can extend below:",
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            "💎 **Upgrade to Premium**\n\n"
            "• 3D plotting\n"
            "• System of equations solver\n"
            "• Curve fitting\n"
            "• PDF exports\n"
            "• Share calculations\n"
            "• Save custom functions\n"
            "• No daily limits\n"
            "• Priority processing\n\n"
            "Choose your plan:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_buy":
        # Create a new message with buy options
        keyboard = [
            [InlineKeyboardButton("💰 Monthly - 50 Stars", callback_data="buy_monthly")],
            [InlineKeyboardButton("📅 Yearly - 500 Stars", callback_data="buy_yearly")],
            [InlineKeyboardButton("💎 Lifetime - 2000 Stars", callback_data="buy_lifetime")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "💎 **Premium Plans**\n\nChoose your subscription:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    if query.data.startswith("buy_"):
        # Send invoice
        plan = query.data.replace("buy_", "")
        
        if plan == "monthly":
            title = "Premium Monthly"
            description = "30 days of premium access"
            payload = "premium_monthly"
            price = config.STAR_PRICES["premium_monthly"]
        elif plan == "yearly":
            title = "Premium Yearly"
            description = "365 days of premium access"
            payload = "premium_yearly"
            price = config.STAR_PRICES["premium_yearly"]
        elif plan == "lifetime":
            title = "Premium Lifetime"
            description = "Lifetime premium access"
            payload = "premium_lifetime"
            price = config.STAR_PRICES["premium_lifetime"]
        else:
            await query.edit_message_text("Invalid plan selected.")
            return
        
        prices = [LabeledPrice(title, price)]
        
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=config.PROVIDER_TOKEN,
            currency="XTR",
            prices=prices,
            start_parameter="premium"
        )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify pre-checkout."""
    query = update.pre_checkout_query
    if query.invoice_payload in ["premium_monthly", "premium_yearly", "premium_lifetime"]:
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Invalid product.")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Grant premium access after successful payment."""
    user_id = update.effective_user.id
    payload = update.message.successful_payment.invoice_payload
    
    if payload == "premium_monthly":
        expiry = datetime.now() + timedelta(days=30)
        sub_type = "monthly"
    elif payload == "premium_yearly":
        expiry = datetime.now() + timedelta(days=365)
        sub_type = "yearly"
    elif payload == "premium_lifetime":
        expiry = datetime.now() + timedelta(days=365*100)  # 100 years
        sub_type = "lifetime"
    else:
        await update.message.reply_text("Payment received, but unknown product.")
        return
    
    history.set_premium(user_id, expiry, sub_type)
    
    await update.message.reply_text(
        f"✅ **Thank you for your purchase!**\n\n"
        f"You now have premium access until {expiry.strftime('%Y-%m-%d')}\n"
        f"Enjoy all premium features!",
        parse_mode='Markdown'
    )

# ========== Natural Language Handler ==========

async def natural_language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-command messages - Premium feature with built-in AI!"""
    user_text = update.message.text
    user_id = update.effective_user.id
    
    # Use built-in smart interpreter (NO API KEYS NEEDED!)
    from llm_integration import interpret_math_query
    interpretation = interpret_math_query(user_text, None)
    
    # Check if this is a premium feature and user isn't premium/owner
    if interpretation.get("premium", False) and not history.is_premium(user_id) and not is_owner(user_id):
        # This is a premium feature but user isn't premium
        keyboard = [[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="show_buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"🔮 **Premium Feature!**\n\n"
            f"{interpretation.get('explanation', 'Natural language understanding')}\n\n"
            f"This is a premium feature. Upgrade to unlock natural language processing!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # User is premium, owner, or feature is free
    expr = interpretation.get("expression")
    explanation = interpretation.get("explanation")
    cmd = interpretation.get("command", "none")
    
    # If it's a simple calculation, just compute it directly
    if cmd == "calc" and expr:
        # Check free tier limit
        if not await enforce_limit(update):
            return
        try:
            steps, result = calculator.evaluate_expression(expr)
            await reply_with_steps(update, steps, result)
            history.add_history(update.effective_user.id, "calc", expr, str(result))
            return
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
            return
    
    # For other commands, suggest the command
    if expr and cmd != "none":
        # Build the command suggestion based on command type
        if cmd == "integrate" and interpretation.get("limits"):
            # Handle definite integral
            limits = interpretation.get("limits")
            var = interpretation.get("variable", "x")
            cmd_text = f"/{cmd} {expr} from {limits[0]} to {limits[1]}"
        elif cmd == "plot" and interpretation.get("xmin"):
            # Handle plot with range
            cmd_text = f"/{cmd} {expr} from {interpretation['xmin']} to {interpretation['xmax']}"
        elif cmd == "plot3d" and interpretation.get("xmin"):
            # Handle 3D plot (premium)
            cmd_text = f"/{cmd} {expr} from {interpretation['xmin']} to {interpretation['xmax']} for {interpretation['ymin']} to {interpretation['ymax']}"
        elif cmd == "unit":
            # Handle unit conversion
            cmd_text = f"/{cmd} {interpretation['expression']}"
        elif interpretation.get("variable") and cmd not in ["calc", "stat"]:
            # Handle commands with variables
            clean_expr = expr.replace('?', '').strip()
            cmd_text = f"/{cmd} {clean_expr}"
        else:
            # Default format
            cmd_text = f"/{cmd} {expr}"
        
        # Add premium badge if it's a premium feature
        premium_badge = " 💎" if interpretation.get("premium", False) else ""
        
        await update.message.reply_text(
            f"🧠 **Interpretation{premium_badge}:** {explanation}\n\n"
            f"Try using: `{cmd_text}`",
            parse_mode='Markdown'
        )
    else:
        # No command matched - upsell premium
        if is_owner(user_id) or history.is_premium(user_id):
            # Premium/owner users get more helpful message
            await update.message.reply_text(
                f"🔍 I couldn't understand that as a math query.\n\n"
                f"Try being more specific, or use commands from /start",
                parse_mode='Markdown'
            )
        else:
            # Free users get upsell
            keyboard = [[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="show_buy")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"🔮 **Premium Feature!**\n\n"
                f"Natural language understanding is a premium feature.\n"
                f"Upgrade to ask questions in plain English!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

# ========== Error Handler ==========

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.message:
            await update.message.reply_text(
                "❌ An internal error occurred. Please try again later."
            )
    except:
        pass

# ========== Main ==========

def run_bot():
    """Start the bot."""
    # Create application
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Free commands - Basic
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("calc", calc))
    
    # Free commands - Calculus
    app.add_handler(CommandHandler("derive", derive))
    app.add_handler(CommandHandler("integrate", integrate))
    app.add_handler(CommandHandler("limit", limit))
    app.add_handler(CommandHandler("series", series))
    
    # Free commands - Differential Equations
    app.add_handler(CommandHandler("ode", ode))
    
    # Free commands - Transforms
    app.add_handler(CommandHandler("laplace", laplace))
    app.add_handler(CommandHandler("invlaplace", inverse_laplace))
    app.add_handler(CommandHandler("fourier", fourier))
    
    # Free commands - Vector Calculus
    app.add_handler(CommandHandler("gradient", gradient))
    app.add_handler(CommandHandler("divergence", divergence))
    app.add_handler(CommandHandler("curl", curl))
    
    # Free commands - Numerical Methods
    app.add_handler(CommandHandler("fsolve", fsolve))
    app.add_handler(CommandHandler("quad", quad))
    app.add_handler(CommandHandler("minimize", minimize))
    
    # Free commands - Plotting
    app.add_handler(CommandHandler("plot", plot))
    app.add_handler(CommandHandler("plotmulti", plotmulti))
    
    # Free commands - Matrix Operations
    app.add_handler(CommandHandler("matrix", matrix_mult))
    app.add_handler(CommandHandler("inverse", inverse))
    app.add_handler(CommandHandler("det", determinant))
    app.add_handler(CommandHandler("transpose", transpose))
    app.add_handler(CommandHandler("eigen", eigenvalues))
    
    # Free commands - Unit Conversion
    app.add_handler(CommandHandler("unit", unit))
    
    # Free commands - Statistics
    app.add_handler(CommandHandler("stat", stat))
    app.add_handler(CommandHandler("regress", regress))
    app.add_handler(CommandHandler("ttest", ttest))
    app.add_handler(CommandHandler("correlate", correlate))
    
    # Free commands - History
    app.add_handler(CommandHandler("history", history_cmd))
    
    # Premium commands
    app.add_handler(CommandHandler("plot3d", plot3d))
    app.add_handler(CommandHandler("system", system))
    app.add_handler(CommandHandler("fit", fit))
    app.add_handler(CommandHandler("exportpdf", exportpdf))
    app.add_handler(CommandHandler("share", share))
    app.add_handler(CommandHandler("save", save_func))
    app.add_handler(CommandHandler("list", list_funcs))
    
    # Owner commands
    app.add_handler(CommandHandler("addpremium", owner_add_premium))
    app.add_handler(CommandHandler("removepremium", owner_remove_premium))
    app.add_handler(CommandHandler("checkuser", owner_check_user))
    app.add_handler(CommandHandler("broadcast", owner_broadcast))
    app.add_handler(CommandHandler("stats", owner_stats))
    
    # API key commands
    app.add_handler(CommandHandler("setkey", setkey))
    app.add_handler(CommandHandler("checkkey", checkkey))
    app.add_handler(CommandHandler("removekey", removekey))
    
    # Payment commands
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    # Natural language fallback
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, natural_language_handler))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    logger.info("SmartCalcAI Bot started! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    # Start web server in background (for Railway)
    if WEB_SERVER:
        threading.Thread(target=run_web_server, daemon=True).start()
        logger.info(f"Web server started on port {os.getenv('PORT', 8080)}")
    
    # Start the bot
    run_bot()
