#!/usr/bin/env python3
"""
Dive AI V25.3 - GPT-4 Vision Integration
Screen understanding and visual grounding for commands
"""

import os
import base64
import io
import time
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import mss
import pyautogui

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


@dataclass
class VisionConfig:
    """Configuration for Vision capabilities"""
    model: str = "gpt-4-vision-preview"
    max_tokens: int = 1000
    detail: str = "high"  # low, high, auto
    auto_capture: bool = True
    capture_delay: float = 0.5  # seconds


class DiveVisionProcessor:
    """
    GPT-4 Vision processor for screen understanding
    Enables visual grounding and context-aware commands
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[VisionConfig] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.config = config or VisionConfig()
        
        if OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            print("⚠ OpenAI library not available")
        
        # Screenshot tool
        self.sct = mss.mss()
        
        # Cache
        self.last_screenshot = None
        self.last_screenshot_time = 0
        
        print(f"✓ Vision Processor initialized")
        print(f"  Model: {self.config.model}")
        print(f"  Auto-capture: {self.config.auto_capture}")
    
    def capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        save_path: Optional[str] = None
    ) -> Image.Image:
        """
        Capture screenshot
        
        Args:
            region: (left, top, width, height) or None for full screen
            save_path: Optional path to save screenshot
        
        Returns:
            PIL Image object
        """
        try:
            if region:
                # Capture specific region
                monitor = {
                    "left": region[0],
                    "top": region[1],
                    "width": region[2],
                    "height": region[3]
                }
            else:
                # Capture full screen
                monitor = self.sct.monitors[1]  # Primary monitor
            
            # Capture
            sct_img = self.sct.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes(
                "RGB",
                (sct_img.width, sct_img.height),
                sct_img.rgb
            )
            
            # Cache
            self.last_screenshot = img
            self.last_screenshot_time = time.time()
            
            # Save if requested
            if save_path:
                img.save(save_path)
                print(f"💾 Screenshot saved: {save_path}")
            
            print(f"📸 Screenshot captured: {img.width}x{img.height}")
            return img
        
        except Exception as e:
            print(f"⚠ Screenshot error: {e}")
            return None
    
    def get_cached_screenshot(self, max_age: float = 2.0) -> Optional[Image.Image]:
        """
        Get cached screenshot if recent enough
        
        Args:
            max_age: Maximum age in seconds
        
        Returns:
            Cached screenshot or None
        """
        if self.last_screenshot and (time.time() - self.last_screenshot_time) <= max_age:
            return self.last_screenshot
        return None
    
    def encode_image(self, image: Image.Image, format: str = "PNG") -> str:
        """
        Encode image to base64 string
        
        Args:
            image: PIL Image
            format: Image format (PNG, JPEG)
        
        Returns:
            Base64 encoded string
        """
        buffered = io.BytesIO()
        image.save(buffered, format=format)
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def analyze_image(
        self,
        image: Optional[Image.Image] = None,
        prompt: str = "What do you see in this image?",
        use_cache: bool = True
    ) -> str:
        """
        Analyze image with GPT-4 Vision
        
        Args:
            image: PIL Image or None to capture screen
            prompt: Analysis prompt
            use_cache: Use cached screenshot if available
        
        Returns:
            Analysis result text
        """
        if not self.client:
            return "Vision API not available"
        
        # Get image
        if image is None:
            if use_cache:
                image = self.get_cached_screenshot()
            if image is None:
                image = self.capture_screen()
        
        if image is None:
            return "Failed to capture screenshot"
        
        try:
            # Encode image
            img_base64 = self.encode_image(image)
            
            # Create message
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}",
                                    "detail": self.config.detail
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.config.max_tokens
            )
            
            result = response.choices[0].message.content
            print(f"👁️ Vision analysis complete")
            return result
        
        except Exception as e:
            print(f"⚠ Vision analysis error: {e}")
            return f"Error: {str(e)}"
    
    def detect_elements(
        self,
        image: Optional[Image.Image] = None,
        element_type: str = "button"
    ) -> List[Dict[str, Any]]:
        """
        Detect UI elements in image
        
        Args:
            image: PIL Image or None to capture screen
            element_type: Type of element to detect (button, text, icon, etc.)
        
        Returns:
            List of detected elements with positions
        """
        prompt = f"""
        Analyze this screenshot and identify all {element_type}s visible.
        For each {element_type}, provide:
        1. Description
        2. Approximate position (percentage from top-left: x%, y%)
        3. Color
        4. Text (if any)
        
        Format as JSON array:
        [
            {{
                "description": "...",
                "position": {{"x": 50, "y": 30}},
                "color": "blue",
                "text": "Submit"
            }}
        ]
        """
        
        result = self.analyze_image(image, prompt)
        
        # Parse JSON response
        try:
            import json
            # Extract JSON from response
            json_start = result.find('[')
            json_end = result.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                elements = json.loads(json_str)
                return elements
        except Exception as e:
            print(f"⚠ Element detection parsing error: {e}")
        
        return []
    
    def extract_text(
        self,
        image: Optional[Image.Image] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> str:
        """
        Extract text from image (OCR)
        
        Args:
            image: PIL Image or None to capture screen
            region: Optional region to focus on
        
        Returns:
            Extracted text
        """
        if region and image is None:
            image = self.capture_screen(region)
        
        prompt = """
        Extract all visible text from this image.
        Preserve the layout and structure as much as possible.
        Include:
        - UI labels
        - Button text
        - Menu items
        - Error messages
        - Any other visible text
        """
        
        return self.analyze_image(image, prompt)
    
    def visual_grounding(
        self,
        query: str,
        image: Optional[Image.Image] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Find element position based on description
        
        Args:
            query: Description of element to find (e.g., "blue submit button")
            image: PIL Image or None to capture screen
        
        Returns:
            (x, y) coordinates or None if not found
        """
        if image is None:
            image = self.capture_screen()
        
        if image is None:
            return None
        
        prompt = f"""
        Find the element matching this description: "{query}"
        
        Provide the approximate position as percentage from top-left corner.
        Format: {{"x": 50, "y": 30}} where x and y are percentages (0-100).
        
        If multiple matches, return the most prominent one.
        If no match found, return {{"x": -1, "y": -1}}.
        """
        
        result = self.analyze_image(image, prompt)
        
        # Parse position
        try:
            import json
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                position = json.loads(json_str)
                
                x_percent = position.get('x', -1)
                y_percent = position.get('y', -1)
                
                if x_percent >= 0 and y_percent >= 0:
                    # Convert percentage to pixel coordinates
                    screen_width, screen_height = image.size
                    x = int(screen_width * x_percent / 100)
                    y = int(screen_height * y_percent / 100)
                    
                    print(f"🎯 Element found at: ({x}, {y})")
                    return (x, y)
        except Exception as e:
            print(f"⚠ Visual grounding parsing error: {e}")
        
        print(f"❌ Element not found: {query}")
        return None
    
    def click_element(self, query: str) -> bool:
        """
        Find and click element based on description
        
        Args:
            query: Description of element to click
        
        Returns:
            True if clicked, False otherwise
        """
        position = self.visual_grounding(query)
        
        if position:
            x, y = position
            pyautogui.click(x, y)
            print(f"🖱️ Clicked at ({x}, {y})")
            return True
        
        return False
    
    def annotate_screenshot(
        self,
        image: Image.Image,
        elements: List[Dict[str, Any]],
        save_path: str
    ):
        """
        Annotate screenshot with detected elements
        
        Args:
            image: PIL Image
            elements: List of elements with positions
            save_path: Path to save annotated image
        """
        # Create a copy
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Draw elements
        for i, element in enumerate(elements):
            pos = element.get('position', {})
            x_percent = pos.get('x', 0)
            y_percent = pos.get('y', 0)
            
            # Convert to pixels
            x = int(image.width * x_percent / 100)
            y = int(image.height * y_percent / 100)
            
            # Draw circle
            radius = 10
            draw.ellipse(
                [(x - radius, y - radius), (x + radius, y + radius)],
                outline='red',
                width=3
            )
            
            # Draw label
            label = f"{i+1}. {element.get('description', 'Element')}"
            draw.text((x + 15, y - 10), label, fill='red', font=font)
        
        # Save
        annotated.save(save_path)
        print(f"💾 Annotated screenshot saved: {save_path}")


# Example usage
if __name__ == "__main__":
    # Create vision processor
    vision = DiveVisionProcessor()
    
    # Test 1: Capture and analyze screen
    print("\n" + "="*70)
    print("TEST 1: Screen Analysis")
    print("="*70)
    
    result = vision.analyze_image(prompt="Describe what you see on this screen in detail.")
    print(f"\nAnalysis:\n{result}")
    
    # Test 2: Extract text
    print("\n" + "="*70)
    print("TEST 2: Text Extraction")
    print("="*70)
    
    text = vision.extract_text()
    print(f"\nExtracted text:\n{text}")
    
    # Test 3: Detect buttons
    print("\n" + "="*70)
    print("TEST 3: Button Detection")
    print("="*70)
    
    buttons = vision.detect_elements(element_type="button")
    print(f"\nDetected {len(buttons)} buttons:")
    for i, button in enumerate(buttons):
        print(f"{i+1}. {button}")
    
    # Test 4: Visual grounding
    print("\n" + "="*70)
    print("TEST 4: Visual Grounding")
    print("="*70)
    
    position = vision.visual_grounding("close button")
    if position:
        print(f"\nClose button found at: {position}")
    else:
        print("\nClose button not found")
    
    print("\n" + "="*70)
    print("Vision tests complete!")
    print("="*70)
