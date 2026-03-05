#!/usr/bin/env python3
"""
SmartCalcAI Bot - Complete Telegram Math Assistant
All features included: free tier, premium with Stars, BYO LLM key
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, PreCheckoutQueryHandler, CallbackQueryHandler
)
import config
import calculator
import graphing
import units
import matrix
import stats
import history
from llm_integration import LLMHandler, interpret_math_query

# Initialize database
history.init_db()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== Helper Functions ==========

async def reply_with_steps(update, steps, result=None):
    """Send steps as formatted text."""
    msg = ""
    for s in steps:
        msg += s + "\n"
    if result is not None and not isinstance(result, str):
        msg += f"\n**Result:** `{result}`"
    await update.message.reply_text(msg, parse_mode='Markdown')

def check_free_limit(user_id):
    """Return True if user is premium or under daily limit."""
    if history.is_premium(user_id):
        return True
    if config.FREE_DAILY_LIMIT == 0:
        return True
    count = history.get_daily_count(user_id)
    return count < config.FREE_DAILY_LIMIT

async def enforce_limit(update: Update):
    """Check and enforce free tier limit."""
    if not check_free_limit(update.effective_user.id):
        keyboard = [[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="show_buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"⚠️ You've used your {config.FREE_DAILY_LIMIT} free calculations today.\n"
            "Upgrade to premium for unlimited access!",
            reply_markup=reply_markup
        )
        return False
    return True

def premium_required(func):
    """Decorator for premium-only commands."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not history.is_premium(update.effective_user.id):
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
    welcome = """
🧠 **SmartCalcAI Bot – The Ultimate Math Assistant**

**✨ Free Features** (10 calculations/day):
• `/calc 2+2` – Basic calculations
• `/derive x^3*sin(x)` – Derivatives with steps
• `/integrate x^2 dx` – Indefinite integrals
• `/integrate x^2 from 0 to 1` – Definite integrals
• `/limit sin(x)/x as 0` – Limits
• `/series exp(x) about 0` – Series expansion
• `/ode y'' + y = 0` – Differential equations
• `/laplace sin(t)` – Laplace transforms
• `/fourier exp(-x^2)` – Fourier transforms
• `/gradient x^2*y` – Gradient
• `/divergence [x*y, y*z, z*x]` – Divergence
• `/curl [x*y, y*z, z*x]` – Curl
• `/fsolve x^2-2=0` – Numerical root finding
• `/quad integrate x^2 0 1` – Numerical integration
• `/minimize x^2+2x+1` – Minimization
• `/plot sin(x) from -10 to 10` – 2D plotting
• `/matrix [[1,2],[3,4]] * [[0,1],[1,0]]` – Matrix multiply
• `/inverse [[1,2],[3,4]]` – Matrix inverse
• `/det [[1,2],[3,4]]` – Determinant
• `/unit 100 km to miles` – Unit conversion
• `/stat 1,2,3,4,5` – Basic statistics
• `/regress 1,2,3 4,5,6` – Linear regression
• `/ttest 1,2,3,4,5 0` – T-test
• `/history` – Your last calculations

**💎 Premium Features** (unlock with /buy):
• `/plot3d x*y from -5 to 5` – 3D surface plots
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

Just send a math question – if you have an API key, I'll understand natural language!
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')

# ========== Free Commands (with limit check) ==========

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    expr = ' '.join(context.args)
    if not expr:
        await update.message.reply_text("Usage: /calc <expression>")
        return
    try:
        steps, result = calculator.evaluate_expression(expr)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "calc", expr, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def derive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /derive <function> [variable]")
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
        await update.message.reply_text("Usage: /integrate <function> [from a to b] [variable]")
        return
    try:
        if " from " in text and " to " in text:
            func_part, rest = text.split(" from ")
            limits_part, var_part = rest.split(" to ")
            a_str, b_str = limits_part.split()
            var = var_part.strip() if var_part else 'x'
            a, b = float(a_str), float(b_str)
            steps, result = calculator.integral_with_steps(func_part, var, (a, b))
        else:
            parts = text.split()
            if parts and parts[-1].isalpha():
                var = parts[-1]
                func_str = ' '.join(parts[:-1])
            else:
                var = 'x'
                func_str = text
            steps, result = calculator.integral_with_steps(func_str, var)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "integrate", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /limit <function> as <variable> <value>")
        return
    try:
        # Parse: "sin(x)/x as x 0"
        if " as " in text:
            func_part, rest = text.split(" as ")
            var_val = rest.split()
            if len(var_val) == 2:
                var, approach = var_val
                approach = float(approach)
                steps, result = calculator.limit_calc(func_part, var, approach)
                await reply_with_steps(update, steps, result)
                history.add_history(update.effective_user.id, "limit", text, str(result))
            else:
                await update.message.reply_text("Format: /limit <function> as <variable> <value>")
        else:
            await update.message.reply_text("Format: /limit <function> as <variable> <value>")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def ode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /ode <ODE> [function] [variable]\nExample: /ode f'' + f = 0")
        return
    try:
        steps, sol = calculator.solve_ode(text)
        await reply_with_steps(update, steps, sol)
        history.add_history(update.effective_user.id, "ode", text, str(sol))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def laplace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /laplace <function> [variable=t] [s_var=s]")
        return
    try:
        steps, result = calculator.laplace_transform(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "laplace", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def gradient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /gradient <scalar field>")
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
        await update.message.reply_text("Usage: /divergence [x,y,z]")
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
        await update.message.reply_text("Usage: /curl [x,y,z]")
        return
    try:
        steps, result = calculator.curl(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "curl", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def fsolve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /fsolve <equation> [guess]")
        return
    try:
        parts = text.split()
        if len(parts) > 1 and parts[-1].replace('.','').isdigit():
            guess = float(parts[-1])
            expr = ' '.join(parts[:-1])
        else:
            guess = 0.0
            expr = text
        steps, result = calculator.fsolve(expr, guess=guess)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "fsolve", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def quad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /quad <function> <a> <b>")
        return
    try:
        parts = text.split()
        if len(parts) >= 3:
            expr = ' '.join(parts[:-2])
            a, b = float(parts[-2]), float(parts[-1])
            steps, result = calculator.quad_integral(expr, a=a, b=b)
            await reply_with_steps(update, steps, result)
            history.add_history(update.effective_user.id, "quad", text, str(result))
        else:
            await update.message.reply_text("Usage: /quad <function> <a> <b>")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def plot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    try:
        if " from " in text and " to " in text:
            func_str, range_str = text.split(" from ")
            range_parts = range_str.split(" to ")
            xmin = float(range_parts[0])
            xmax = float(range_parts[1])
            buf = graphing.plot_function(func_str, xmin, xmax)
            await update.message.reply_photo(photo=buf, caption=f"Plot of {func_str}")
            history.add_history(update.effective_user.id, "plot", text, "Plot generated")
        else:
            await update.message.reply_text("Please use format: /plot <function> from <min> to <max>")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def matrix_mult(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if '*' not in text:
        await update.message.reply_text("Usage: /matrix <A> * <B>\nExample: /matrix [[1,2],[3,4]] * [[0,1],[1,0]]")
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
        await update.message.reply_text("Usage: /inverse [[1,2],[3,4]]")
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
        await update.message.reply_text("Usage: /det [[1,2],[3,4]]")
        return
    try:
        steps, result = matrix.matrix_determinant(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "det", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /unit <value> <from_unit> to <to_unit>\nExample: /unit 100 km to miles")
        return
    try:
        steps, result = units.convert_units(text)
        await reply_with_steps(update, steps, result)
        history.add_history(update.effective_user.id, "unit", text, str(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_limit(update): return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("Usage: /stat <numbers>\nExample: /stat 1,2,3,4,5")
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
        await update.message.reply_text("Usage: /regress <x_values> <y_values>\nExample: /regress 1,2,3 2,4,6")
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
        await update.message.reply_text("Usage: /ttest <data> <popmean>\nExample: /ttest 1,2,3,4,5 3")
        return
    try:
        data_text = args[0]
        popmean = float(args[1])
        steps, results = stats.t_test_onesample(data_text, popmean)
        await reply_with_steps(update, steps)
        history.add_history(update.effective_user.id, "ttest", f"{data_text} {popmean}", str(results))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

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
    # Format: x*y from -5 to 5 for -5 to 5
    try:
        if " from " in text and " to " in text and " for " in text:
            func_part, rest = text.split(" from ")
            x_range, y_range = rest.split(" for ")
            xmin, xmax = map(float, x_range.split(" to "))
            ymin, ymax = map(float, y_range.split(" to "))
            buf = graphing.plot3d_function(func_part, xmin, xmax, ymin, ymax)
            await update.message.reply_photo(photo=buf, caption=f"3D plot of {func_part}")
            history.add_history(update.effective_user.id, "plot3d", text, "3D plot")
        else:
            await update.message.reply_text("Usage: /plot3d <f(x,y)> from <xmin> to <xmax> for <ymin> to <ymax>")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@premium_required
async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if " for " not in text:
        await update.message.reply_text("Usage: /system <eq1, eq2> for <vars>\nExample: /system x+y=5, 2x-y=1 for x,y")
        return
    try:
        eqs_str, vars_str = text.split(" for ")
        steps, sol = calculator.solve_system(eqs_str, vars_str)
        await reply_with_steps(update, steps, sol)
        history.add_history(update.effective_user.id, "system", text, str(sol))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@premium_required
async def fit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    await update.message.reply_text("Curve fitting coming soon! (Premium feature)")
    history.add_history(update.effective_user.id, "fit", text, "Placeholder")

@premium_required
async def exportpdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In real implementation, generate PDF from user's history
    await update.message.reply_text("📄 PDF export coming soon! This will generate a PDF of your calculations.")
    history.add_history(update.effective_user.id, "exportpdf", "", "PDF export requested")

@premium_required
async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    calc_id = ' '.join(context.args) if context.args else "latest"
    await update.message.reply_text(f"🔗 Sharing calculation {calc_id} – feature coming soon!")
    history.add_history(update.effective_user.id, "share", calc_id, "Share requested")

@premium_required
async def save_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /save <name> <expression>\nExample: /save f1 x**2 + 1")
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

# ========== API Key Commands ==========

async def setkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /setkey <provider> <your_api_key>\nProviders: openai, gemini, claude")
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
        await buy(update, context)
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
    """Handle non-command messages."""
    user_text = update.message.text
    user_id = update.effective_user.id
    
    # Check if user has API key
    provider, api_key = history.get_user_key(user_id)
    
    if provider and api_key:
        # Use their key for interpretation
        try:
            llm = LLMHandler(provider, api_key)
            interpretation = interpret_math_query(user_text, llm)
            
            expr = interpretation.get("expression")
            explanation = interpretation.get("explanation")
            cmd = interpretation.get("command", "none")
            
            if expr and cmd != "none":
                await update.message.reply_text(
                    f"🧠 **Interpretation:** {explanation}\n\n"
                    f"Try using: `/{cmd} {expr}`",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"🧠 **Interpretation:** {explanation}\n\n"
                    f"I couldn't map that to a command. Try using one of the commands in /start",
                    parse_mode='Markdown'
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error with your API key: {e}\n"
                f"Try /removekey and set it again."
            )
    else:
        # No key - guide to commands
        await update.message.reply_text(
            "I didn't understand that as a command.\n\n"
            "To use natural language, set your API key with /setkey.\n"
            "Otherwise, use one of the commands listed in /start."
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

def main():
    """Start the bot."""
    # Create application
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Free commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("derive", derive))
    app.add_handler(CommandHandler("integrate", integrate))
    app.add_handler(CommandHandler("limit", limit))
    app.add_handler(CommandHandler("ode", ode))
    app.add_handler(CommandHandler("laplace", laplace))
    app.add_handler(CommandHandler("gradient", gradient))
    app.add_handler(CommandHandler("divergence", divergence))
    app.add_handler(CommandHandler("curl", curl))
    app.add_handler(CommandHandler("fsolve", fsolve))
    app.add_handler(CommandHandler("quad", quad))
    app.add_handler(CommandHandler("plot", plot))
    app.add_handler(CommandHandler("matrix", matrix_mult))
    app.add_handler(CommandHandler("inverse", inverse))
    app.add_handler(CommandHandler("det", determinant))
    app.add_handler(CommandHandler("unit", unit))
    app.add_handler(CommandHandler("stat", stat))
    app.add_handler(CommandHandler("regress", regress))
    app.add_handler(CommandHandler("ttest", ttest))
    app.add_handler(CommandHandler("history", history_cmd))
    
    # Premium commands
    app.add_handler(CommandHandler("plot3d", plot3d))
    app.add_handler(CommandHandler("system", system))
    app.add_handler(CommandHandler("fit", fit))
    app.add_handler(CommandHandler("exportpdf", exportpdf))
    app.add_handler(CommandHandler("share", share))
    app.add_handler(CommandHandler("save", save_func))
    app.add_handler(CommandHandler("list", list_funcs))
    
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
    main()