"""
Image preprocessing for better OCR accuracy
"""
import logging
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
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
        
        @staticmethod
        def threshold(*args, **kwargs):
            raise ImportError("OpenCV not available")
        
        @staticmethod
        def fastNlMeansDenoising(*args, **kwargs):
            raise ImportError("OpenCV not available")
        
        @staticmethod
        def createCLAHE(*args, **kwargs):
            raise ImportError("OpenCV not available")
        
        @staticmethod
        def resize(*args, **kwargs):
            raise ImportError("OpenCV not available")
        
        @staticmethod
        def imencode(*args, **kwargs):
            raise ImportError("OpenCV not available")
    
    cv2 = DummyCV2()

def enhance_image(image_bytes):
    """Apply OpenCV enhancements to improve OCR accuracy"""
    if not OPENCV_AVAILABLE:
        logger.warning("OpenCV not available - using PIL fallback")
        # Return original image as numpy array using PIL
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return np.array(img.convert('L'))  # Convert to grayscale
        except Exception as e:
            logger.error(f"PIL fallback failed: {e}")
            return None
    
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            # Fallback to PIL
            img_pil = Image.open(io.BytesIO(image_bytes))
            return np.array(img_pil.convert('L'))
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Try multiple preprocessing techniques and return the best one
        enhanced_versions = []
        
        # 1. Simple thresholding
        _, thresh1 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        enhanced_versions.append(("Threshold", thresh1))
        
        # 2. Adaptive thresholding
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY, 11, 2)
        enhanced_versions.append(("Adaptive", thresh2))
        
        # 3. Otsu's thresholding
        _, thresh3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        enhanced_versions.append(("Otsu", thresh3))
        
        # 4. Denoise + threshold
        denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
        _, thresh4 = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        enhanced_versions.append(("Denoised+Otsu", thresh4))
        
        # 5. CLAHE (contrast enhancement)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        _, thresh5 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        enhanced_versions.append(("CLAHE+Otsu", thresh5))
        
        # Return the last enhanced version (usually best)
        # The OCR engine will try multiple versions anyway
        final_enhanced = thresh5
        
        # Resize if too small
        height, width = final_enhanced.shape
        if width < 800:
            scale = 800 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            final_enhanced = cv2.resize(final_enhanced, (new_width, new_height))
            logger.info(f"📸 Resized image from {width}x{height} to {new_width}x{new_height}")
        
        logger.info(f"✅ Image enhancement complete - final shape: {final_enhanced.shape}")
        return final_enhanced
        
    except Exception as e:
        logger.error(f"OpenCV enhancement failed: {e}")
        # Fallback to PIL
        try:
            img_pil = Image.open(io.BytesIO(image_bytes))
            return np.array(img_pil.convert('L'))
        except Exception as e2:
            logger.error(f"PIL fallback also failed: {e2}")
            return None

def image_to_bytes(img_array):
    """Convert numpy array back to bytes for processing"""
    if img_array is None:
        return None
    
    if OPENCV_AVAILABLE:
        try:
            _, buffer = cv2.imencode('.png', img_array)
            return buffer.tobytes()
        except Exception as e:
            logger.error(f"OpenCV image conversion failed: {e}")
    
    # Fallback to PIL
    try:
        img = Image.fromarray(img_array)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    except Exception as e:
        logger.error(f"PIL image conversion failed: {e}")
        return None

async def load_image_from_update(photo):
    """Download photo from Telegram update"""
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    logger.info(f"📸 Downloaded image: {len(image_bytes)} bytes")
    return image_bytes

def preprocess_image_pil(image):
    """PIL-based preprocessing (fallback when OpenCV not available)"""
    try:
        if isinstance(image, np.ndarray):
            img = Image.fromarray(image)
        else:
            img = image
        
        logger.info(f"📸 PIL preprocessing: mode={img.mode}, size={img.size}")
        
        # Convert to grayscale
        if img.mode != 'L':
            img = img.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Sharpen
        img = img.filter(ImageFilter.SHARPEN)
        
        # Convert back to numpy array
        return np.array(img)
        
    except Exception as e:
        logger.error(f"PIL preprocessing failed: {e}")
        return None
