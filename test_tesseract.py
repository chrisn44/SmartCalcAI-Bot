import pytesseract
import subprocess
import sys

print("=" * 50)
print("Tesseract Diagnostic Test")
print("=" * 50)

# Check tesseract in PATH
try:
    result = subprocess.run(['tesseract', '--version'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Tesseract found in PATH")
        print(f"Version: {result.stdout.splitlines()[0] if result.stdout else 'unknown'}")
    else:
        print("❌ Tesseract not found in PATH")
except Exception as e:
    print(f"❌ Error checking tesseract: {e}")

# Check common locations
paths = ['/usr/bin/tesseract', '/usr/local/bin/tesseract']
for path in paths:
    import os
    if os.path.exists(path):
        print(f"✅ Tesseract found at: {path}")
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   Works! Version: {result.stdout.splitlines()[0] if result.stdout else 'unknown'}")
        except:
            print(f"   ❌ But failed to run")
    else:
        print(f"❌ Not found at: {path}")

# Test pytesseract
print("\nTesting pytesseract:")
try:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (200, 50), color='white')
    d = ImageDraw.Draw(img)
    d.text((10, 10), "2+2=4", fill='black')
    text = pytesseract.image_to_string(img)
    print(f"✅ pytesseract works! Extracted: '{text.strip()}'")
except Exception as e:
    print(f"❌ pytesseract test failed: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)