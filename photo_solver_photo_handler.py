"""
Telegram handler for photo messages
"""
import os
import tempfile
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORRECTED IMPORTS - using underscores instead of hyphens
try:
    from photo_solver_image_processor import enhance_image, load_image_from_update, image_to_bytes
    from photo_solver_ocr_engine import OCREngine
    from photo_solver_equation_parser import EquationParser
    from photo_solver_solver import EquationSolver
    IMPORTS_SUCCESS = True
except ImportError as e:
    logger.error(f"Failed to import photo solver modules: {e}")
    IMPORTS_SUCCESS = False

# Initialize components (singletons) only if imports succeeded
if IMPORTS_SUCCESS:
    ocr_engine = OCREngine()
    parser = EquationParser()
    solver = EquationSolver()
    logger.info("✅ Photo solver components initialized")
else:
    ocr_engine = None
    parser = None
    solver = None
    logger.error("❌ Photo solver components not initialized due to import errors")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main handler for photo messages – Premium only!
    """
    logger.info("📸 Photo received! Processing...")
    
    # Log details about the photo
    if update.message.photo:
        photo_count = len(update.message.photo)
        logger.info(f"Photo message received with {photo_count} sizes")
        largest_photo = update.message.photo[-1]
        logger.info(f"Largest photo size: {largest_photo.width}x{largest_photo.height}")
    
    user_id = update.effective_user.id
    logger.info(f"User ID: {user_id}")
    
    # Check if imports succeeded
    if not IMPORTS_SUCCESS:
        await update.message.reply_text(
            "❌ Photo solver modules are not properly installed.\n"
            "Please check the server logs for more information."
        )
        return
    
    # Import premium check from your existing system
    try:
        from bot import is_owner, history
    except ImportError as e:
        logger.error(f"Failed to import from bot: {e}")
        await update.message.reply_text(
            "❌ Internal error: Could not verify premium status."
        )
        return
    
    # Premium check (owner always has access)
    try:
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
    except Exception as e:
        logger.error(f"Premium check failed: {e}")
        await update.message.reply_text(
            "❌ Error checking premium status. Please try again later."
        )
        return
    
    # Send initial status
    status_msg = await update.message.reply_text("🔍 Processing image...")
    
    try:
        # Get the largest photo
        photo = update.message.photo[-1]
        logger.info(f"Processing photo: {photo.width}x{photo.height}")
        
        # Download image
        file = await photo.get_file()
        image_bytes = await file.download_as_bytearray()
        logger.info(f"Downloaded image: {len(image_bytes)} bytes")
        
        # Enhance image for OCR
        logger.info("Enhancing image...")
        enhanced = enhance_image(image_bytes)
        
        # Extract equation text
        await status_msg.edit_text("🔍 Running OCR...")
        logger.info("Running OCR...")
        extracted_text, method = ocr_engine.extract_equation(image_bytes, enhanced)
        
        if not extracted_text:
            logger.warning("No text extracted from image")
            await status_msg.edit_text(
                "❌ Could not extract any text from the image.\n"
                "Please ensure the equation is clearly visible and well-lit."
            )
            return
        
        logger.info(f"OCR extracted: {extracted_text} (method: {method})")
        
        # Parse equation
        await status_msg.edit_text(f"📝 Parsing equation...\nDetected: `{extracted_text}`")
        left_expr, right_expr, error = parser.parse_equation(extracted_text)
        
        if error:
            logger.error(f"Parse error: {error}")
            await status_msg.edit_text(
                f"❌ {error}\n\n"
                f"Raw text detected: `{extracted_text}`"
            )
            return
        
        # Solve
        await status_msg.edit_text("🧮 Solving...")
        steps, result = solver.solve_equation(left_expr, right_expr)
        logger.info(f"Equation solved: {result}")
        
        # Format response
        response = f"📸 **Photo Equation Solver**\n"
        response += f"• OCR method: `{method}`\n"
        response += f"• Detected: `{extracted_text}`\n\n"
        response += "\n".join(steps)
        
        await status_msg.edit_text(response, parse_mode='Markdown')
        
        # Save to history
        try:
            from history import add_history
            add_history(user_id, "photo_solve", extracted_text, str(result))
        except Exception as e:
            logger.error(f"Failed to save to history: {e}")
        
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Error processing image: {str(e)}")
