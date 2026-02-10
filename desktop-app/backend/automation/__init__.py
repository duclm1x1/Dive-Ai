"""Automation Package"""

from .uitars import UITarsEngine, get_engine, execute_instruction
from .screenshot import ScreenshotService, get_screenshot_service, capture
from .input import InputController, get_controller
from .ocr import OCRService, get_ocr, extract_screen_text


__all__ = [
    "UITarsEngine", "get_engine", "execute_instruction",
    "ScreenshotService", "get_screenshot_service", "capture",
    "InputController", "get_controller",
    "OCRService", "get_ocr", "extract_screen_text",
]
