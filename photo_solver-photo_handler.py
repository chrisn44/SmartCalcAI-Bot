"""
Telegram handler for photo messages
"""
import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from photo_solver-image_processor import enhance_image, load_image_from_update, image_to_bytes
from photo_solver-ocr_engine import OCREngine
from photo_solver-equation_parser import EquationParser
from photo_solver-solver import EquationSolver

# Initialize components (singletons)
ocr_engine = OCREngine()
parser = EquationParser()
solver = EquationSolver()

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main handler for photo messages – Premium only!
    """
    user_id = update.effective_user.id
    
    # Import premium check from your existing system
    from bot import is_owner, history
    
    # Premium check (owner always has access)
    if not is_owner(user_id) and not history.is_premium(user_id):
        keyboard = [[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="show_buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📸 **Photo Equation Solver**\n\n"
            "This feature is for premium users only.\n"
            "Upgrade to solve equations from photos!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Send initial status
    status_msg = await update.message.reply_text("🔍 Processing image...")
    
    try:
        # Get the largest photo
        photo = update.message.photo[-1]
        
        # Download image
        file = await photo.get_file()
        image_bytes = await file.download_as_bytearray()
        
        # Enhance image for OCR
        enhanced = enhance_image(image_bytes)
        
        # Extract equation text
        await status_msg.edit_text("🔍 Running OCR...")
        extracted_text, method = ocr_engine.extract_equation(image_bytes, enhanced)
        
        if not extracted_text:
            await status_msg.edit_text(
                "❌ Could not extract any text from the image.\n"
                "Please ensure the equation is clearly visible."
            )
            return
        
        # Parse equation
        await status_msg.edit_text(f"📝 Parsing equation...\nDetected: `{extracted_text}`")
        left_expr, right_expr, error = parser.parse_equation(extracted_text)
        
        if error:
            await status_msg.edit_text(
                f"❌ {error}\n\n"
                f"Raw text detected: `{extracted_text}`"
            )
            return
        
        # Solve
        await status_msg.edit_text("🧮 Solving...")
        steps, result = solver.solve_equation(left_expr, right_expr)
        
        # Format response
        response = f"📸 **Photo Equation Solver**\n"
        response += f"• OCR method: `{method}`\n"
        response += f"• Detected: `{extracted_text}`\n\n"
        response += "\n".join(steps)
        
        await status_msg.edit_text(response, parse_mode='Markdown')
        
        # Save to history
        from history import add_history
        add_history(user_id, "photo_solve", extracted_text, str(result))
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error processing image: {str(e)}")