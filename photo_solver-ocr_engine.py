"""
Multi‑strategy OCR engine for mathematical equations
"""
import pytesseract
import re
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Try importing advanced OCR libraries
try:
    from pix2tex.cli import LatexOCR
    PIX2TEX_AVAILABLE = True
except ImportError:
    PIX2TEX_AVAILABLE = False
    logger.warning("pix2tex not installed – advanced LaTeX OCR disabled")

try:
    import aspose.ocr as ocr
    ASPOSE_AVAILABLE = True
except ImportError:
    ASPOSE_AVAILABLE = False
    logger.warning("aspose-ocr not installed – commercial OCR disabled")

class OCREngine:
    def __init__(self):
        self.latex_model = None
        if PIX2TEX_AVAILABLE:
            try:
                self.latex_model = LatexOCR()
                logger.info("pix2tex LaTeX model loaded")
            except Exception as e:
                logger.error(f"Failed to load pix2tex: {e}")
        
        self.aspose_api = None
        if ASPOSE_AVAILABLE:
            try:
                self.aspose_api = ocr.AsposeOcr()
                logger.info("Aspose.OCR initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Aspose: {e}")
    
    def extract_with_pytesseract(self, image_array):
        """Basic OCR with pytesseract"""
        try:
            # Convert numpy array to PIL Image
            img = Image.fromarray(image_array)
            
            # Try multiple PSM modes for better accuracy
            configs = [
                '--psm 6',      # Assume uniform text block
                '--psm 7',      # Single text line
                '--psm 8',      # Single word
                '-c tessedit_char_whitelist=0123456789+-*/^()=xXyYabcdefghijklmnopqrstuvwxyz --psm 6'
            ]
            
            best_text = ""
            max_length = 0
            
            for config in configs:
                text = pytesseract.image_to_string(img, config=config)
                # Clean the text
                text = re.sub(r'[^\w\s\+\-\*\/\^\(\)\=]', '', text)
                text = text.strip()
                
                # Keep the longest meaningful result
                if len(text) > max_length and len(text) > 2:
                    best_text = text
                    max_length = len(text)
            
            return best_text if max_length > 0 else None
            
        except Exception as e:
            logger.error(f"Pytesseract OCR failed: {e}")
            return None
    
    def extract_with_pix2tex(self, image_bytes):
        """Advanced LaTeX OCR using transformer model"""
        if not self.latex_model:
            return None
        
        try:
            # pix2tex expects file-like object or path
            import io
            from PIL import Image
            
            img = Image.open(io.BytesIO(image_bytes))
            latex = self.latex_model(img)
            return latex.strip()
            
        except Exception as e:
            logger.error(f"pix2tex failed: {e}")
            return None
    
    def extract_with_aspose(self, image_bytes):
        """Commercial OCR specialized for formulas"""
        if not self.aspose_api:
            return None
        
        try:
            import aspose.ocr as ocr
            input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
            input.add_bytes(image_bytes)
            
            settings = ocr.RecognitionSettings()
            settings.detect_areas_mode = ocr.DetectAreasMode.FORMULA
            
            results = self.aspose_api.recognize(input, settings)
            
            if results and len(results) > 0:
                return results[0].recognition_text.strip()
            return None
            
        except Exception as e:
            logger.error(f"Aspose OCR failed: {e}")
            return None
    
    def extract_equation(self, image_bytes, image_array):
        """
        Try multiple OCR strategies in order of sophistication
        """
        # Strategy 1: Try pix2tex (best for LaTeX)
        if PIX2TEX_AVAILABLE:
            result = self.extract_with_pix2tex(image_bytes)
            if result and len(result) > 3:
                return result, "pix2tex (AI LaTeX)"
        
        # Strategy 2: Try Aspose (commercial)
        if ASPOSE_AVAILABLE:
            result = self.extract_with_aspose(image_bytes)
            if result and len(result) > 3:
                return result, "Aspose.OCR (Formula)"
        
        # Strategy 3: Fallback to pytesseract
        result = self.extract_with_pytesseract(image_array)
        if result:
            return result, "Tesseract (Basic OCR)"
        
        return None, None