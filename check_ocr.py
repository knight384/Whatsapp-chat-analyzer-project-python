#!/usr/bin/env python
"""
Helper script to check OCR setup for WhatsApp Chat Analyzer
"""
import sys

def check_ocr_setup():
    print("=" * 60)
    print("WhatsApp Chat Analyzer - OCR Setup Check")
    print("=" * 60)
    print()
    
    # Check Python packages
    print("1. Checking Python packages...")
    try:
        import PIL
        print("   [OK] Pillow is installed (version: {})".format(PIL.__version__))
    except ImportError:
        print("   [X] Pillow is NOT installed")
        print("     Install with: pip install Pillow")
        return False
    
    try:
        import pytesseract
        print("   [OK] pytesseract is installed (version: {})".format(pytesseract.__version__))
    except ImportError:
        print("   [X] pytesseract is NOT installed")
        print("     Install with: pip install pytesseract")
        return False
    
    print()
    print("2. Checking Tesseract OCR engine...")
    
    # Try to get Tesseract version
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print("   [OK] Tesseract OCR is installed (version: {})".format(version))
        print()
        print("=" * 60)
        print("[OK] All OCR dependencies are properly installed!")
        print("=" * 60)
        return True
    except Exception as e:
        print("   [X] Tesseract OCR is NOT found or not in PATH")
        print()
        print("   Error:", str(e))
        print()
        print("=" * 60)
        print("Installation Instructions for Windows:")
        print("=" * 60)
        print()
        print("1. Download Tesseract OCR installer:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        print("2. Run the installer and:")
        print("   - Use default installation path: C:\\Program Files\\Tesseract-OCR")
        print("   - Make sure 'Add to PATH' option is checked during installation")
        print()
        print("3. After installation:")
        print("   - Close and reopen your terminal/IDE")
        print("   - Run this script again to verify: python check_ocr.py")
        print()
        print("Alternative: If Tesseract is installed but not in PATH,")
        print("you can manually set it in your code:")
        print("   import pytesseract")
        print("   pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        print()
        print("=" * 60)
        print("Note: Text file (.txt) uploads work WITHOUT OCR!")
        print("OCR is only needed for image/screenshot uploads.")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = check_ocr_setup()
    sys.exit(0 if success else 1)

