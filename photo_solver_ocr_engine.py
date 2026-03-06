"""
Multi‑strategy OCR engine for mathematical equations
"""
import pytesseract
import re
from PIL import Image
import io
import logging
import os
import subprocess

# Configure logging
logger = logging.getLogger(__name__)

# ========== TESSERACT PATH DETECTION ==========

def find_tesseract():
    """Find tesseract executable in common locations"""
    possible_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/app/.local/bin/tesseract',
        'tesseract'  # Let system PATH handle it
    ]
    
    for path in possible_paths:
        try:
            if path == 'tesseract':
                # Try running from PATH
                result = subprocess.run(['tesseract', '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Tesseract found in PATH")
                    return 'tesseract'
            elif os.path.exists(path):
                # Test if it works
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Tesseract found at: {path}")
                    return path
        except:
            continue
    
    print("❌ Tesseract not found. Please install tesseract-ocr")
    return None

# Set tesseract path
tesseract_path = find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print("⚠️ Tesseract not available - OCR will fail")

# Try importing advanced OCR libraries
try:
    from pix2tex.cli import LatexOCR
    PIX2TEX_AVAILABLE = True
    print("✅ pix2tex LaTeX OCR available")
except ImportError:
    PIX2TEX_AVAILABLE = False
    logger.warning("pix2tex not installed – advanced LaTeX OCR disabled")

try:
    import aspose.ocr as ocr
    ASPOSE_AVAILABLE = True
    print("✅ Aspose.OCR available")
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
                ('--psm 6', 'Uniform text block'),
                ('--psm 7', 'Single text line'),
                ('--psm 8', 'Single word'),
                ('-c tessedit_char_whitelist=0123456789+-*/^()=xXyYabcdefghijklmnopqrstuvwxyz --psm 6', 'Math characters')
            ]
            
            best_text = ""
            max_length = 0
            best_config = ""
            
            for config, desc in configs:
                try:
                    text = pytesseract.image_to_string(img, config=config)
                    # Clean the text
                    text = re.sub(r'[^\w\s\+\-\*\/\^\(\)\=]', '', text)
                    text = text.strip()
                    
                    # Keep the longest meaningful result
                    if len(text) > max_length and len(text) > 2:
                        best_text = text
                        max_length = len(text)
                        best_config = desc
                except Exception as e:
                    logger.debug(f"OCR config '{desc}' failed: {e}")
                    continue
            
            if best_text:
                logger.info(f"OCR successful with {best_config}: {best_text}")
                return best_text
            else:
                logger.warning("No text extracted from image")
                return None
            
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
            result = latex.strip()
            logger.info(f"pix2tex extracted: {result}")
            return result
            
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
                result = results[0].recognition_text.strip()
                logger.info(f"Aspose extracted: {result}")
                return result
            return None
            
        except Exception as e:
            logger.error(f"Aspose OCR failed: {e}")
            return None
    
    def extract_equation(self, image_bytes, image_array):
        """
        Try multiple OCR strategies in order of sophistication
        """
        logger.info("Starting OCR extraction...")
        
        # Strategy 1: Try pix2tex (best for LaTeX)
        if PIX2TEX_AVAILABLE and self.latex_model:
            try:
                result = self.extract_with_pix2tex(image_bytes)
                if result and len(result) > 3:
                    logger.info(f"pix2tex succeeded: {result}")
                    return result, "pix2tex (AI LaTeX)"
            except Exception as e:
                logger.error(f"pix2tex error: {e}")
        
        # Strategy 2: Try Aspose (commercial)
        if ASPOSE_AVAILABLE and self.aspose_api:
            try:
                result = self.extract_with_aspose(image_bytes)
                if result and len(result) > 3:
                    logger.info(f"Aspose succeeded: {result}")
                    return result, "Aspose.OCR (Formula)"
            except Exception as e:
                logger.error(f"Aspose error: {e}")
        
        # Strategy 3: Fallback to pytesseract
        try:
            result = self.extract_with_pytesseract(image_array)
            if result:
                logger.info(f"Tesseract succeeded: {result}")
                return result, "Tesseract (Basic OCR)"
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
        
        logger.warning("All OCR strategies failed")
        return None, None

    def test_tesseract(self):
        """Test if tesseract is working"""
        try:
            # Create a simple test image
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Create a simple image with text
            img = Image.new('RGB', (200, 50), color='white')
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
            d.text((10, 10), "2+2=4", fill='black', font=font)
            
            # Convert to array for OCR
            import numpy as np
            img_array = np.array(img)
            
            # Try OCR
            result = self.extract_with_pytesseract(img_array)
            if result:
                print(f"✅ Tesseract test successful: {result}")
                return True
            else:
                print("❌ Tesseract test failed: No text extracted")
                return False
        except Exception as e:
            print(f"❌ Tesseract test error: {e}")
            return False
