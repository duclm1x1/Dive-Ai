"""
Screen OCR - Text recognition from screenshots

Uses Tesseract for OCR.
"""

import io
from typing import List, Tuple, Optional

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCRService:
    """OCR text extraction service"""
    
    def __init__(self, tesseract_path: str = None):
        if TESSERACT_AVAILABLE and tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, image_bytes: bytes = None) -> str:
        """Extract text from image or current screen"""
        if not TESSERACT_AVAILABLE:
            return "Tesseract not installed"
        
        if image_bytes:
            img = Image.open(io.BytesIO(image_bytes))
        elif PIL_AVAILABLE:
            img = ImageGrab.grab()
        else:
            return "PIL not available"
        
        try:
            return pytesseract.image_to_string(img)
        except Exception as e:
            return f"OCR error: {e}"
    
    def extract_from_region(self, x: int, y: int, width: int, height: int) -> str:
        """Extract text from screen region"""
        if not PIL_AVAILABLE:
            return "PIL not available"
        
        img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        
        if not TESSERACT_AVAILABLE:
            return "Tesseract not installed"
        
        try:
            return pytesseract.image_to_string(img)
        except Exception as e:
            return f"OCR error: {e}"
    
    def find_text(self, text: str) -> List[Tuple[int, int, int, int]]:
        """Find text on screen and return bounding boxes"""
        if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
            return []
        
        img = ImageGrab.grab()
        
        try:
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            results = []
            for i, word in enumerate(data['text']):
                if text.lower() in word.lower():
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    results.append((x, y, w, h))
            
            return results
        except Exception:
            return []
    
    def is_available(self) -> bool:
        """Check if OCR is available"""
        return TESSERACT_AVAILABLE and PIL_AVAILABLE


# Singleton
_ocr = None

def get_ocr() -> OCRService:
    """Get OCR service"""
    global _ocr
    if _ocr is None:
        _ocr = OCRService()
    return _ocr


def extract_screen_text() -> str:
    """Quick extract from screen"""
    return get_ocr().extract_text()
