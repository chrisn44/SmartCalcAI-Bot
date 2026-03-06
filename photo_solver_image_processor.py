"""
Image preprocessing for better OCR accuracy
"""
import logging
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Try to import OpenCV with fallback
try:
    import cv2
    OPENCV_AVAILABLE = True
    logger.info("✅ OpenCV loaded successfully")
except ImportError as e:
    OPENCV_AVAILABLE = False
    logger.error(f"❌ OpenCV import failed: {e}")
    
    # Create dummy functions as fallback
    class DummyCV2:
        @staticmethod
        def imdecode(*args, **kwargs):
            raise ImportError("OpenCV not available")
        
        @staticmethod
        def cvtColor(*args, **kwargs):
            raise ImportError("OpenCV not available")
    
    cv2 = DummyCV2()

def enhance_image(image_bytes):
    """Apply OpenCV enhancements to improve OCR accuracy"""
    if not OPENCV_AVAILABLE:
        logger.error("OpenCV not available - cannot enhance image")
        # Return original image as numpy array
        img = Image.open(io.BytesIO(image_bytes))
        return np.array(img)
    
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            # Fallback to PIL
            img_pil = Image.open(io.BytesIO(image_bytes))
            return np.array(img_pil)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to make text sharper
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Resize if too small (helps OCR)
        height, width = enhanced.shape
        if width < 800:
            scale = 800 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            enhanced = cv2.resize(enhanced, (new_width, new_height))
        
        return enhanced
        
    except Exception as e:
        logger.error(f"OpenCV enhancement failed: {e}")
        # Fallback to PIL
        try:
            img_pil = Image.open(io.BytesIO(image_bytes))
            return np.array(img_pil.convert('L'))  # Convert to grayscale
        except Exception as e2:
            logger.error(f"PIL fallback also failed: {e2}")
            return None

def image_to_bytes(img_array):
    """Convert numpy array back to bytes for processing"""
    if not OPENCV_AVAILABLE or img_array is None:
        return image_bytes
    
    try:
        _, buffer = cv2.imencode('.png', img_array)
        return buffer.tobytes()
    except Exception as e:
        logger.error(f"Failed to convert image to bytes: {e}")
        return None

async def load_image_from_update(photo):
    """Download photo from Telegram update"""
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    return image_bytes
