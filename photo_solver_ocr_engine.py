"""
Multi‑strategy OCR engine for mathematical equations
"""
import pytesseract
import re
from PIL import Image, ImageEnhance, ImageFilter
import io
import logging
import os
import subprocess
import numpy as np
import cv2

# Configure logging
logger = logging.getLogger(__name__)

# ========== TESSERACT PATH DETECTION ==========

def find_tesseract():
    """Find tesseract executable in common locations"""
    possible_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/app/.local/bin/tesseract',
        '/opt/homebrew/bin/tesseract',  # macOS Homebrew
        'tesseract'  # Let system PATH handle it
    ]
    
    for path in possible_paths:
        try:
            if path == 'tesseract':
                # Try running from PATH
                result = subprocess.run(['tesseract', '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0] if result.stdout else "unknown"
                    print(f"✅ Tesseract found in PATH (version: {version})")
                    return 'tesseract'
            elif os.path.exists(path):
                # Test if it works
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0] if result.stdout else "unknown"
                    print(f"✅ Tesseract found at: {path} (version: {version})")
                    return path
        except Exception as e:
            print(f"⚠️ Error checking path {path}: {e}")
            continue
    
    print("❌ Tesseract not found. Please install tesseract-ocr")
    return None

# Set tesseract path
tesseract_path = find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✅ Tesseract configured at: {pytesseract.pytesseract.tesseract_cmd}")
    
    # Test tesseract version
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
    except Exception as e:
        print(f"⚠️ Could not get tesseract version: {e}")
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
                logger.info("✅ pix2tex LaTeX model loaded")
            except Exception as e:
                logger.error(f"❌ Failed to load pix2tex: {e}")
        
        self.aspose_api = None
        if ASPOSE_AVAILABLE:
            try:
                self.aspose_api = ocr.AsposeOcr()
                logger.info("✅ Aspose.OCR initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Aspose: {e}")
    
    def preprocess_image(self, image_array):
        """Apply multiple preprocessing techniques to improve OCR accuracy"""
        try:
            # Convert to PIL Image for preprocessing
            if isinstance(image_array, np.ndarray):
                img = Image.fromarray(image_array)
            else:
                img = image_array
            
            logger.info(f"📸 Original image: mode={img.mode}, size={img.size}")
            
            # Store all preprocessed versions
            preprocessed_images = []
            
            # 1. Original
            preprocessed_images.append(("Original", img))
            
            # 2. Convert to grayscale if needed
            if img.mode != 'L':
                img_gray = img.convert('L')
                preprocessed_images.append(("Grayscale", img_gray))
            
            # 3. Increase contrast
            enhancer = ImageEnhance.Contrast(img)
            img_contrast = enhancer.enhance(2.0)
            preprocessed_images.append(("High Contrast", img_contrast))
            
            # 4. Sharpen
            img_sharp = img.filter(ImageFilter.SHARPEN)
            preprocessed_images.append(("Sharpened", img_sharp))
            
            # 5. Binarize (threshold)
            if img.mode == 'L':
                img_bin = img.point(lambda x: 0 if x < 128 else 255, '1')
                preprocessed_images.append(("Binary", img_bin))
            
            # 6. Scale up if too small
            width, height = img.size
            if width < 800:
                scale = 800 / width
                new_size = (int(width * scale), int(height * scale))
                img_scaled = img.resize(new_size, Image.Resampling.LANCZOS)
                preprocessed_images.append(f"Scaled {scale:.1f}x", img_scaled)
            
            logger.info(f"✅ Created {len(preprocessed_images)} preprocessed versions")
            return preprocessed_images
            
        except Exception as e:
            logger.error(f"❌ Image preprocessing failed: {e}")
            return [("Original", Image.fromarray(image_array))] if isinstance(image_array, np.ndarray) else [("Original", image_array)]
    
    def extract_with_pytesseract(self, image):
        """Basic OCR with pytesseract using multiple configurations"""
        try:
            results = []
            
            # Try different PSM modes
            psm_modes = [
                (6, "Uniform block of text"),
                (7, "Single text line"),
                (8, "Single word"),
                (11, "Sparse text"),
                (12, "Sparse text with OSD"),
                (13, "Raw line"),
                (3, "Automatic page segmentation")
            ]
            
            # Try with and without character whitelist
            configs = []
            for psm, desc in psm_modes:
                # Standard config
                configs.append((f'--psm {psm}', f"PSM {psm} ({desc})"))
                
                # Math-focused config (only math characters)
                math_config = f'-c tessedit_char_whitelist=0123456789+-*/^()=xXyY. --psm {psm}'
                configs.append((math_config, f"Math PSM {psm}"))
            
            # Try with different OEM modes (OCR Engine modes)
            oem_modes = [1, 2, 3]  # 1=LSTM only, 2=Legacy + LSTM, 3=Default
            for oem in oem_modes:
                configs.append((f'--oem {oem} --psm 6', f"OEM {oem} + PSM 6"))
            
            for config, desc in configs:
                try:
                    text = pytesseract.image_to_string(image, config=config)
                    
                    # Clean the text
                    text_clean = re.sub(r'[^\w\s\+\-\*\/\^\(\)\=]', '', text)
                    text_clean = text_clean.strip()
                    
                    if text_clean:
                        results.append({
                            'config': desc,
                            'text': text_clean,
                            'length': len(text_clean),
                            'raw': text.strip()
                        })
                        logger.debug(f"OCR with {desc}: '{text_clean}' (raw: '{text.strip()}')")
                except Exception as e:
                    logger.debug(f"OCR config '{desc}' failed: {e}")
                    continue
            
            # Sort by length (longest likely best)
            results.sort(key=lambda x: x['length'], reverse=True)
            
            if results:
                best = results[0]
                logger.info(f"✅ Best OCR result ({best['config']}): '{best['text']}'")
                
                # Log all results for debugging
                if len(results) > 1:
                    logger.debug("All OCR results:")
                    for r in results:
                        logger.debug(f"  - {r['config']}: '{r['text']}'")
                
                return best['text']
            else:
                logger.warning("❌ No text extracted with any configuration")
                return None
            
        except Exception as e:
            logger.error(f"❌ Pytesseract OCR failed: {e}")
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
            logger.info(f"✅ pix2tex extracted: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ pix2tex failed: {e}")
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
                logger.info(f"✅ Aspose extracted: {result}")
                return result
            return None
            
        except Exception as e:
            logger.error(f"❌ Aspose OCR failed: {e}")
            return None
    
    def extract_equation(self, image_bytes, image_array):
        """
        Try multiple OCR strategies in order of sophistication
        """
        logger.info("🚀 Starting OCR extraction...")
        
        # First, preprocess the image
        if image_array is not None:
            if isinstance(image_array, np.ndarray):
                # Try OpenCV preprocessing if available
                try:
                    # Enhance with OpenCV
                    import cv2
                    
                    # Convert to grayscale if needed
                    if len(image_array.shape) == 3:
                        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = image_array
                    
                    # Try different preprocessing techniques
                    preprocessed_versions = []
                    
                    # 1. Original grayscale
                    preprocessed_versions.append(("Grayscale", gray))
                    
                    # 2. Thresholding
                    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    preprocessed_versions.append(("OTSU Threshold", thresh))
                    
                    # 3. Adaptive threshold
                    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY, 11, 2)
                    preprocessed_versions.append(("Adaptive Threshold", adaptive))
                    
                    # 4. Denoised
                    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
                    preprocessed_versions.append(("Denoised", denoised))
                    
                    # 5. CLAHE
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                    enhanced = clahe.apply(gray)
                    preprocessed_versions.append(("CLAHE", enhanced))
                    
                    logger.info(f"✅ Created {len(preprocessed_versions)} OpenCV preprocessed versions")
                    
                    # Try OCR on each preprocessed version
                    for prep_name, prep_img in preprocessed_versions:
                        try:
                            result = self.extract_with_pytesseract(prep_img)
                            if result:
                                logger.info(f"✅ OCR succeeded with {prep_name}: '{result}'")
                                return result, f"Tesseract ({prep_name})"
                        except Exception as e:
                            logger.debug(f"OCR with {prep_name} failed: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"OpenCV preprocessing failed: {e}")
            
            # Fallback to PIL preprocessing
            preprocessed = self.preprocess_image(image_array)
            
            for prep_name, prep_img in preprocessed:
                try:
                    result = self.extract_with_pytesseract(prep_img)
                    if result:
                        logger.info(f"✅ OCR succeeded with {prep_name}: '{result}'")
                        return result, f"Tesseract ({prep_name})"
                except Exception as e:
                    logger.debug(f"OCR with {prep_name} failed: {e}")
                    continue
        
        # Try advanced OCR libraries if available
        if PIX2TEX_AVAILABLE and self.latex_model:
            try:
                result = self.extract_with_pix2tex(image_bytes)
                if result and len(result) > 3:
                    logger.info(f"✅ pix2tex succeeded: {result}")
                    return result, "pix2tex (AI LaTeX)"
            except Exception as e:
                logger.error(f"pix2tex error: {e}")
        
        if ASPOSE_AVAILABLE and self.aspose_api:
            try:
                result = self.extract_with_aspose(image_bytes)
                if result and len(result) > 3:
                    logger.info(f"✅ Aspose succeeded: {result}")
                    return result, "Aspose.OCR (Formula)"
            except Exception as e:
                logger.error(f"Aspose error: {e}")
        
        logger.warning("❌ All OCR strategies failed")
        return None, None

    def test_tesseract(self):
        """Test if tesseract is working with a simple generated image"""
        try:
            # Create a simple test image
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple image with text
            img = Image.new('RGB', (400, 100), color='white')
            d = ImageDraw.Draw(img)
            
            # Try to use a larger font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 32)
            except:
                try:
                    font = ImageFont.truetype("Arial.ttf", 32)
                except:
                    font = ImageFont.load_default()
            
            d.text((50, 30), "2 + 2 = 4", fill='black', font=font)
            
            logger.info(f"✅ Created test image: size={img.size}")
            
            # Save for debugging
            img.save("test_ocr_image.png")
            logger.info("✅ Saved test image as 'test_ocr_image.png'")
            
            # Convert to array for OCR
            import numpy as np
            img_array = np.array(img)
            
            # Try OCR with multiple attempts
            result = self.extract_with_pytesseract(img)
            
            if result:
                logger.info(f"✅ Tesseract test successful: '{result}'")
                return True
            else:
                logger.error("❌ Tesseract test failed: No text extracted")
                
                # Try with preprocessing
                logger.info("Attempting OCR with preprocessing...")
                preprocessed = self.preprocess_image(img)
                for prep_name, prep_img in preprocessed:
                    r = self.extract_with_pytesseract(prep_img)
                    if r:
                        logger.info(f"✅ Preprocessing '{prep_name}' worked: '{r}'")
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Tesseract test error: {e}")
            return False

# Run a quick test when module loads
if __name__ != "__main__":
    # Test Tesseract on module load
    tester = OCREngine()
    test_result = tester.test_tesseract()
    if test_result:
        print("✅ Tesseract initialization test passed")
    else:
        print("⚠️ Tesseract initialization test failed - OCR may not work")
