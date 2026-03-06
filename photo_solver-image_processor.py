"""
Image preprocessing for better OCR accuracy
"""
import cv2
import numpy as np
from PIL import Image
import io

def enhance_image(image_bytes):
    """Apply OpenCV enhancements to improve OCR accuracy"""
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
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

def image_to_bytes(img_array):
    """Convert numpy array back to bytes for processing"""
    _, buffer = cv2.imencode('.png', img_array)
    return buffer.tobytes()

async def load_image_from_update(photo):
    """Download photo from Telegram update"""
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    return image_bytes