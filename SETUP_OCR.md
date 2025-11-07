# OCR Setup Guide for Image Uploads

## Current Status

✅ **Python packages installed:**
- Pillow (version 12.0.0)
- pytesseract (version 0.3.13)

❌ **Tesseract OCR engine:** Not installed

## Important Notes

🟢 **Text files (.txt) work immediately!** You don't need OCR for text file uploads.

🟡 **Image/screenshot uploads require Tesseract OCR** to extract text from images.

## Installing Tesseract OCR (for Image Support)

### Option 1: Automatic Installation (Recommended)

1. **Download Tesseract OCR for Windows:**
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)

2. **Install Tesseract:**
   - Run the installer
   - **Important:** Use the default installation path: `C:\Program Files\Tesseract-OCR`
   - **Important:** Check the "Add to PATH" option during installation
   - Complete the installation

3. **Restart your terminal/IDE:**
   - Close all terminal windows and your code editor
   - Reopen them to refresh the PATH

4. **Verify installation:**
   ```bash
   python check_ocr.py
   ```

### Option 2: Manual Path Configuration (If Tesseract is installed elsewhere)

If Tesseract is already installed but not in PATH, you can manually configure it:

1. Find where Tesseract is installed (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`)

2. The app will automatically try to detect it in common locations. If it's in a different location, you can modify `main.py`:

   ```python
   # Add this at the top of main.py after the imports
   if OCR_AVAILABLE:
       pytesseract.pytesseract.tesseract_cmd = r'C:\Your\Custom\Path\Tesseract-OCR\tesseract.exe'
   ```

## Testing

After installation, verify everything works:

```bash
# Check OCR setup
python check_ocr.py

# Start the Flask server
python app.py

# Open http://localhost:5000 in your browser
```

## Troubleshooting

### "Tesseract not found" error
- Make sure Tesseract is installed
- Restart your terminal/IDE after installation
- Verify PATH includes Tesseract: `echo %PATH%` (should show Tesseract-OCR folder)
- Run `check_ocr.py` to verify

### Image upload still fails
- Make sure the image is clear and readable
- Try a higher resolution image
- Ensure the image contains WhatsApp chat text in a recognizable format

### Text files work but images don't
- This is expected if Tesseract is not installed
- Install Tesseract following Option 1 above
- Restart the Flask server after installation

## Quick Reference

- **Text files:** Work immediately, no setup needed ✅
- **Image files:** Require Tesseract OCR installation 🟡
- **Check OCR status:** `python check_ocr.py`
- **Download Tesseract:** https://github.com/UB-Mannheim/tesseract/wiki

