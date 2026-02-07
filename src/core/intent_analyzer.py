"""
Dive AI v25 - Intent Understanding

Deep Understand: Extract intent, entities, and context from speech

Features:
- Action classification (click, type, scroll, open, etc.)
- Entity extraction (targets, parameters)
- Context awareness (conversation history)
- Multi-language support (EN/VI)
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions the assistant can perform"""
    # Desktop automation
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    DRAG = "drag"
    
    # Application control
    OPEN = "open"
    CLOSE = "close"
    SWITCH = "switch"
    
    # Navigation
    NAVIGATE = "navigate"
    SEARCH = "search"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    
    # File operations
    SAVE = "save"
    COPY = "copy"
    PASTE = "paste"
    DELETE = "delete"
    
    # System
    SCREENSHOT = "screenshot"
    WAIT = "wait"
    
    # Conversation
    QUESTION = "question"
    CLARIFY = "clarify"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class Entity:
    """Extracted entity from text"""
    type: str  # "target", "text", "url", "number", "direction", etc.
    value: str
    confidence: float = 1.0
    start: int = 0
    end: int = 0


@dataclass
class Intent:
    """Parsed intent from user speech"""
    action: ActionType
    entities: List[Entity] = field(default_factory=list)
    confidence: float = 0.0
    raw_text: str = ""
    language: str = "en"
    
    # Convenience properties
    @property
    def target(self) -> Optional[str]:
        """Get primary target entity"""
        for e in self.entities:
            if e.type == "target":
                return e.value
        return None
        
    @property
    def text_input(self) -> Optional[str]:
        """Get text to type"""
        for e in self.entities:
            if e.type == "text":
                return e.value
        return None
        
    @property
    def url(self) -> Optional[str]:
        """Get URL entity"""
        for e in self.entities:
            if e.type == "url":
                return e.value
        return None
        
    @property
    def direction(self) -> Optional[str]:
        """Get scroll direction"""
        for e in self.entities:
            if e.type == "direction":
                return e.value
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action": self.action.value,
            "target": self.target,
            "text": self.text_input,
            "url": self.url,
            "direction": self.direction,
            "confidence": self.confidence,
            "raw_text": self.raw_text,
            "language": self.language
        }
        
    def __str__(self):
        parts = [f"Intent({self.action.value}"]
        if self.target:
            parts.append(f"target='{self.target}'")
        if self.text_input:
            parts.append(f"text='{self.text_input}'")
        parts.append(f"conf={self.confidence:.1%})")
        return ", ".join(parts)


class IntentPatterns:
    """Pattern-based intent detection"""
    
    # English patterns
    EN_PATTERNS = {
        ActionType.CLICK: [
            r"click\s+(?:on\s+)?(?:the\s+)?(.+)",
            r"press\s+(?:the\s+)?(.+)",
            r"tap\s+(?:on\s+)?(?:the\s+)?(.+)",
            r"select\s+(?:the\s+)?(.+)",
            r"choose\s+(?:the\s+)?(.+)",
            r"hit\s+(?:the\s+)?(.+)"
        ],
        ActionType.TYPE: [
            r"type\s+[\"']?(.+?)[\"']?(?:\s+in(?:to)?\s+(.+))?$",
            r"write\s+[\"']?(.+?)[\"']?(?:\s+in(?:to)?\s+(.+))?$",
            r"enter\s+[\"']?(.+?)[\"']?(?:\s+in(?:to)?\s+(.+))?$",
            r"input\s+[\"']?(.+?)[\"']?(?:\s+in(?:to)?\s+(.+))?$",
            r"fill\s+(?:in\s+)?(.+)\s+with\s+[\"']?(.+?)[\"']?$"
        ],
        ActionType.SCROLL: [
            r"scroll\s+(up|down|left|right)",
            r"scroll\s+to\s+(?:the\s+)?(top|bottom)",
            r"go\s+(up|down)\s+(?:the\s+)?page",
            r"page\s+(up|down)"
        ],
        ActionType.OPEN: [
            r"open\s+(?:the\s+)?(.+)",
            r"launch\s+(?:the\s+)?(.+)",
            r"start\s+(?:the\s+)?(.+)",
            r"run\s+(?:the\s+)?(.+)"
        ],
        ActionType.CLOSE: [
            r"close\s+(?:the\s+)?(.+)",
            r"exit\s+(?:the\s+)?(.+)",
            r"quit\s+(?:the\s+)?(.+)",
            r"shut\s+down\s+(?:the\s+)?(.+)"
        ],
        ActionType.NAVIGATE: [
            r"go\s+to\s+(.+)",
            r"navigate\s+to\s+(.+)",
            r"visit\s+(.+)",
            r"open\s+(?:the\s+)?(?:website|page|url)\s+(.+)"
        ],
        ActionType.SEARCH: [
            r"search\s+(?:for\s+)?(.+)",
            r"find\s+(.+)",
            r"look\s+(?:up|for)\s+(.+)",
            r"google\s+(.+)"
        ],
        ActionType.SCREENSHOT: [
            r"take\s+(?:a\s+)?screenshot",
            r"capture\s+(?:the\s+)?screen",
            r"screenshot"
        ],
        ActionType.COPY: [
            r"copy\s+(?:the\s+)?(.+)?",
            r"copy\s+that"
        ],
        ActionType.PASTE: [
            r"paste\s+(?:it|that|here)?",
            r"paste"
        ],
        ActionType.GO_BACK: [
            r"go\s+back",
            r"back",
            r"previous\s+page"
        ],
        ActionType.GO_FORWARD: [
            r"go\s+forward",
            r"forward",
            r"next\s+page"
        ],
        ActionType.WAIT: [
            r"wait\s+(?:for\s+)?(\d+)\s*(?:seconds?)?",
            r"pause\s+(?:for\s+)?(\d+)\s*(?:seconds?)?"
        ],
        ActionType.CANCEL: [
            r"cancel",
            r"stop",
            r"never\s*mind",
            r"forget\s+it"
        ],
        ActionType.CONFIRM: [
            r"yes",
            r"confirm",
            r"do\s+it",
            r"go\s+ahead",
            r"okay|ok"
        ]
    }
    
    # Vietnamese patterns
    VI_PATTERNS = {
        ActionType.CLICK: [
            r"bấm\s+(?:vào\s+)?(.+)",
            r"nhấn\s+(?:vào\s+)?(.+)",
            r"click\s+(?:vào\s+)?(.+)",
            r"chọn\s+(.+)"
        ],
        ActionType.TYPE: [
            r"gõ\s+[\"']?(.+?)[\"']?(?:\s+vào\s+(.+))?$",
            r"nhập\s+[\"']?(.+?)[\"']?(?:\s+vào\s+(.+))?$",
            r"viết\s+[\"']?(.+?)[\"']?(?:\s+vào\s+(.+))?$",
            r"điền\s+[\"']?(.+?)[\"']?(?:\s+vào\s+(.+))?$"
        ],
        ActionType.SCROLL: [
            r"cuộn\s+(lên|xuống|trái|phải)",
            r"kéo\s+(lên|xuống)",
            r"scroll\s+(lên|xuống)"
        ],
        ActionType.OPEN: [
            r"mở\s+(.+)",
            r"khởi\s+động\s+(.+)",
            r"chạy\s+(.+)"
        ],
        ActionType.CLOSE: [
            r"đóng\s+(.+)",
            r"tắt\s+(.+)",
            r"thoát\s+(.+)"
        ],
        ActionType.NAVIGATE: [
            r"đi\s+(?:đến|tới)\s+(.+)",
            r"vào\s+(.+)",
            r"truy\s+cập\s+(.+)"
        ],
        ActionType.SEARCH: [
            r"tìm\s+(?:kiếm\s+)?(.+)",
            r"search\s+(.+)",
            r"tìm\s+(.+)"
        ],
        ActionType.SCREENSHOT: [
            r"chụp\s+màn\s+hình",
            r"screenshot"
        ],
        ActionType.GO_BACK: [
            r"quay\s+lại",
            r"trở\s+lại",
            r"back"
        ],
        ActionType.CANCEL: [
            r"hủy",
            r"thôi",
            r"dừng\s+lại"
        ],
        ActionType.CONFIRM: [
            r"được",
            r"đồng\s+ý",
            r"ok",
            r"ừ",
            r"vâng"
        ]
    }
    
    # Direction mappings
    DIRECTION_MAP = {
        # English
        "up": "up", "down": "down", "left": "left", "right": "right",
        "top": "up", "bottom": "down",
        # Vietnamese
        "lên": "up", "xuống": "down", "trái": "left", "phải": "right"
    }


class IntentAnalyzer:
    """
    Analyze text to extract intent and entities
    
    Uses pattern matching for fast detection,
    falls back to LLM for complex cases
    """
    
    def __init__(self, language: str = "auto"):
        self.language = language
        self._context: List[Intent] = []
        self._max_context = 10
        
    def detect_language(self, text: str) -> str:
        """Detect language from text"""
        # Simple heuristic based on Vietnamese characters
        vietnamese_chars = set("àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ")
        text_lower = text.lower()
        
        vi_count = sum(1 for c in text_lower if c in vietnamese_chars)
        
        if vi_count > 0:
            return "vi"
        return "en"
        
    async def analyze(self, text: str, context: Optional[Dict] = None) -> Intent:
        """
        Analyze text to extract intent
        
        Args:
            text: User's speech text
            context: Optional context (screen state, previous intents)
            
        Returns:
            Intent with action and entities
        """
        text = text.strip()
        
        # Detect language
        language = self.language if self.language != "auto" else self.detect_language(text)
        
        # Try pattern matching first (fast)
        intent = self._pattern_match(text, language)
        
        if intent.action == ActionType.UNKNOWN:
            # Fall back to LLM analysis (slower but more accurate)
            intent = await self._llm_analyze(text, language, context)
            
        # Add to context
        self._add_to_context(intent)
        
        logger.debug(f"📝 Intent: {intent}")
        
        return intent
        
    def _pattern_match(self, text: str, language: str) -> Intent:
        """Match text against patterns"""
        text_lower = text.lower().strip()
        
        patterns = IntentPatterns.VI_PATTERNS if language == "vi" else IntentPatterns.EN_PATTERNS
        
        for action_type, action_patterns in patterns.items():
            for pattern in action_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    entities = self._extract_entities(match, action_type, language)
                    return Intent(
                        action=action_type,
                        entities=entities,
                        confidence=0.9,
                        raw_text=text,
                        language=language
                    )
                    
        return Intent(
            action=ActionType.UNKNOWN,
            confidence=0.0,
            raw_text=text,
            language=language
        )
        
    def _extract_entities(self, match: re.Match, action: ActionType, language: str) -> List[Entity]:
        """Extract entities from regex match"""
        entities = []
        groups = match.groups()
        
        if action == ActionType.CLICK:
            if groups and groups[0]:
                entities.append(Entity(type="target", value=groups[0].strip()))
                
        elif action == ActionType.TYPE:
            if groups:
                if groups[0]:
                    entities.append(Entity(type="text", value=groups[0].strip()))
                if len(groups) > 1 and groups[1]:
                    entities.append(Entity(type="target", value=groups[1].strip()))
                    
        elif action == ActionType.SCROLL:
            if groups and groups[0]:
                direction = IntentPatterns.DIRECTION_MAP.get(groups[0].lower(), groups[0])
                entities.append(Entity(type="direction", value=direction))
                
        elif action in [ActionType.OPEN, ActionType.CLOSE, ActionType.NAVIGATE, ActionType.SEARCH]:
            if groups and groups[0]:
                value = groups[0].strip()
                # Check if it's a URL
                if re.match(r'^https?://|www\.', value, re.IGNORECASE):
                    entities.append(Entity(type="url", value=value))
                else:
                    entities.append(Entity(type="target", value=value))
                    
        elif action == ActionType.WAIT:
            if groups and groups[0]:
                entities.append(Entity(type="duration", value=groups[0]))
                
        return entities
        
    async def _llm_analyze(self, text: str, language: str, context: Optional[Dict]) -> Intent:
        """Use LLM for complex intent analysis"""
        # This would integrate with the Transformation Model
        # For now, return unknown intent
        
        # Check for question patterns
        question_words = ["what", "how", "why", "when", "where", "who", "which", "can", "could", "would"]
        question_words_vi = ["gì", "sao", "tại sao", "khi nào", "ở đâu", "ai", "nào", "có thể"]
        
        text_lower = text.lower()
        
        if language == "vi":
            if any(qw in text_lower for qw in question_words_vi) or text.endswith("?"):
                return Intent(
                    action=ActionType.QUESTION,
                    entities=[Entity(type="question", value=text)],
                    confidence=0.7,
                    raw_text=text,
                    language=language
                )
        else:
            if any(text_lower.startswith(qw) for qw in question_words) or text.endswith("?"):
                return Intent(
                    action=ActionType.QUESTION,
                    entities=[Entity(type="question", value=text)],
                    confidence=0.7,
                    raw_text=text,
                    language=language
                )
                
        return Intent(
            action=ActionType.UNKNOWN,
            confidence=0.3,
            raw_text=text,
            language=language
        )
        
    def _add_to_context(self, intent: Intent):
        """Add intent to conversation context"""
        self._context.append(intent)
        if len(self._context) > self._max_context:
            self._context.pop(0)
            
    def get_context(self) -> List[Intent]:
        """Get recent intent history"""
        return self._context.copy()
        
    def clear_context(self):
        """Clear conversation context"""
        self._context.clear()


# Convenience function
async def analyze_intent(text: str, language: str = "auto") -> Intent:
    """
    Quick intent analysis
    
    Args:
        text: User's speech text
        language: Language code or "auto"
        
    Returns:
        Parsed Intent
    """
    analyzer = IntentAnalyzer(language)
    return await analyzer.analyze(text)


# Test function
async def test_intent_analyzer():
    """Test intent analyzer"""
    print("🧪 Testing Intent Analyzer...")
    print("=" * 50)
    
    analyzer = IntentAnalyzer()
    
    # Test cases
    test_cases = [
        # English
        ("Click on the submit button", "en"),
        ("Type hello world in the search box", "en"),
        ("Open Chrome", "en"),
        ("Scroll down", "en"),
        ("Go to google.com", "en"),
        ("Search for weather forecast", "en"),
        ("Take a screenshot", "en"),
        ("What time is it?", "en"),
        
        # Vietnamese
        ("Bấm vào nút gửi", "vi"),
        ("Gõ xin chào vào ô tìm kiếm", "vi"),
        ("Mở Chrome", "vi"),
        ("Cuộn xuống", "vi"),
        ("Tìm kiếm thời tiết", "vi"),
        ("Chụp màn hình", "vi"),
    ]
    
    for text, expected_lang in test_cases:
        intent = await analyzer.analyze(text)
        status = "✅" if intent.action != ActionType.UNKNOWN else "⚠️"
        print(f"{status} [{expected_lang}] \"{text}\"")
        print(f"   → {intent}")
        print()
        
    print("=" * 50)
    print("✅ Intent analyzer test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_intent_analyzer())
