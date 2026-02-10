"""
📥 USER INPUT VALIDATOR - Enhanced
Validates user input and asks clarifying questions if needed

Part of Dive AI Workflow V2
"""

import os
import sys
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm,
    AlgorithmResult,
    AlgorithmSpec,
    AlgorithmIOSpec,
    IOField
)


class InputStatus(Enum):
    """Status of input validation"""
    CLEAR = "clear"           # ✅ Good to proceed
    AMBIGUOUS = "ambiguous"   # ⚠️ Need clarification
    UNCLEAR = "unclear"       # ❌ Cannot understand
    DANGEROUS = "dangerous"   # 🚨 Potentially harmful


@dataclass
class ValidationResult:
    """Result of input validation"""
    status: InputStatus
    original_input: str
    clarifying_questions: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    detected_intent: Optional[str] = None
    detected_entities: Dict[str, str] = field(default_factory=dict)


class UserInputValidator:
    """
    📥 Enhanced User Input Validator for Dive AI
    
    Features:
    - Gibberish detection
    - Intent recognition
    - Entity extraction
    - Clarifying question generation
    - Confidence scoring
    """
    
    # Keywords that indicate intent
    INTENT_KEYWORDS = {
        "create": ["tạo", "create", "make", "build", "generate", "new", "viết", "code", "làm"],
        "delete": ["xóa", "delete", "remove", "clear", "drop", "bỏ"],
        "edit": ["sửa", "edit", "modify", "change", "update", "fix", "thay đổi"],
        "search": ["tìm", "search", "find", "look", "query", "kiếm"],
        "explain": ["giải thích", "explain", "what", "how", "why", "describe", "là gì"],
        "run": ["chạy", "run", "execute", "start", "launch", "khởi động"],
        "install": ["cài", "install", "setup", "download", "tải"],
        "deploy": ["deploy", "publish", "upload", "host", "đẩy lên"],
        "test": ["test", "kiểm tra", "verify", "check", "thử"],
        "analyze": ["phân tích", "analyze", "review", "inspect", "xem"],
    }
    
    # Entity types
    ENTITY_PATTERNS = {
        "app_type": ["web app", "mobile app", "desktop app", "api", "website", "bot", "cli", "app"],
        "language": ["python", "javascript", "typescript", "java", "go", "rust", "c++", "c#", "php"],
        "framework": ["react", "vue", "angular", "next", "express", "django", "flask", "fastapi"],
        "style": ["giống iphone", "như iphone", "modern", "minimal", "đẹp", "ios", "android"],
    }
    
    # Vague patterns
    VAGUE_PATTERNS = [
        r"^tạo\s*(app|web|code)?$",
        r"^làm$",
        r"^fix$",
        r"^sửa$",
        r"^tìm$",
        r"^đẹp\s*hơn$",
        r"^tốt\s*hơn$",
        r"^ok$",
        r"^được$",
    ]
    
    def validate(self, user_input: str, context: Dict = None) -> ValidationResult:
        """Validate user input"""
        context = context or {}
        input_clean = user_input.strip()
        input_lower = input_clean.lower()
        
        # Check gibberish
        if self._is_gibberish(input_lower):
            return ValidationResult(
                status=InputStatus.UNCLEAR,
                original_input=user_input,
                clarifying_questions=[
                    f"Mình không hiểu '{user_input}'. Bạn có thể mô tả rõ hơn không?",
                    "Bạn muốn: tạo, sửa, xóa, hay tìm kiếm gì?"
                ],
                suggestions=["Viết rõ hơn bạn cần gì"],
                confidence=0.0
            )
        
        # Check too short
        if len(input_clean) < 3:
            return ValidationResult(
                status=InputStatus.UNCLEAR,
                original_input=user_input,
                clarifying_questions=["Input quá ngắn. Bạn muốn làm gì?"],
                confidence=0.1
            )
        
        # Detect intent and entities
        intent = self._detect_intent(input_lower)
        entities = self._detect_entities(input_lower)
        
        # Check vague
        if self._is_vague(input_lower):
            questions = self._generate_questions(intent, entities, input_clean)
            return ValidationResult(
                status=InputStatus.AMBIGUOUS,
                original_input=user_input,
                clarifying_questions=questions,
                suggestions=self._generate_suggestions(intent),
                confidence=0.3,
                detected_intent=intent,
                detected_entities=entities
            )
        
        # Check dangerous
        if self._is_dangerous(input_lower):
            return ValidationResult(
                status=InputStatus.DANGEROUS,
                original_input=user_input,
                clarifying_questions=[
                    "⚠️ Hành động này có thể nguy hiểm. Bạn chắc chắn chứ?",
                ],
                confidence=0.5,
                detected_intent=intent,
                detected_entities=entities
            )
        
        # Calculate confidence
        confidence = self._calculate_confidence(input_lower, intent, entities)
        
        # Somewhat clear but needs more detail
        if confidence < 0.6:
            questions = self._generate_optional_questions(intent, entities)
            return ValidationResult(
                status=InputStatus.AMBIGUOUS,
                original_input=user_input,
                clarifying_questions=questions,
                confidence=confidence,
                detected_intent=intent,
                detected_entities=entities
            )
        
        # Clear - good to proceed!
        return ValidationResult(
            status=InputStatus.CLEAR,
            original_input=user_input,
            confidence=confidence,
            detected_intent=intent,
            detected_entities=entities
        )
    
    def _is_gibberish(self, text: str) -> bool:
        """Check for gibberish input"""
        # Many consecutive consonants
        if re.search(r'[bcdfghjklmnpqrstvwxz]{5,}', text):
            return True
        # No vowels in long string
        if len(text) > 10 and not re.search(r'[aeiouàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]', text):
            return True
        return False
    
    def _is_vague(self, text: str) -> bool:
        """Check for vague input"""
        for pattern in self.VAGUE_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        if len(text.split()) <= 2 and not any(e in text for patterns in self.ENTITY_PATTERNS.values() for e in patterns):
            return True
        return False
    
    def _is_dangerous(self, text: str) -> bool:
        """Check for dangerous commands"""
        dangerous = ["format", "delete all", "xóa hết", "rm -rf", "drop database"]
        return any(d in text for d in dangerous)
    
    def _detect_intent(self, text: str) -> Optional[str]:
        """Detect intent from text"""
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return intent
        return None
    
    def _detect_entities(self, text: str) -> Dict[str, str]:
        """Detect entities from text"""
        entities = {}
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    entities[entity_type] = pattern
                    break
        return entities
    
    def _calculate_confidence(self, text: str, intent: str, entities: Dict) -> float:
        """Calculate confidence score"""
        score = 0.3
        if intent:
            score += 0.2
        if entities:
            score += 0.15 * len(entities)
        if len(text.split()) >= 5:
            score += 0.1
        if len(text.split()) >= 10:
            score += 0.1
        return min(score, 1.0)
    
    def _generate_questions(self, intent: str, entities: Dict, original: str) -> List[str]:
        """Generate clarifying questions"""
        questions = []
        
        if intent == "create":
            if "app_type" not in entities:
                questions.append("Bạn muốn tạo loại gì? (web app, mobile app, API...)")
            if "language" not in entities:
                questions.append("Dùng ngôn ngữ nào? (Python, JavaScript...)")
            questions.append("Chức năng chính là gì?")
        elif intent == "edit":
            questions.append("Sửa file/project nào?")
            questions.append("Cần thay đổi gì cụ thể?")
        elif intent == "delete":
            questions.append("Xóa gì? Ở đâu?")
        elif intent == "search":
            questions.append("Tìm ở đâu? Tìm gì?")
        else:
            questions.append(f"Bạn có thể mô tả chi tiết '{original}' hơn không?")
        
        return questions[:3]
    
    def _generate_suggestions(self, intent: str) -> List[str]:
        """Generate suggestions"""
        suggestions = {
            "create": ["VD: 'Tạo calculator app giống iPhone với HTML/CSS/JS'"],
            "edit": ["VD: 'Sửa file index.html, thêm nút submit'"],
            "delete": ["VD: 'Xóa folder temp trong project'"],
        }
        return suggestions.get(intent, ["Mô tả chi tiết hơn"])
    
    def _generate_optional_questions(self, intent: str, entities: Dict) -> List[str]:
        """Generate optional questions for somewhat clear inputs"""
        if intent == "create" and entities:
            return [f"Có yêu cầu đặc biệt nào cho {list(entities.values())[0]} không?"]
        return ["Có thêm yêu cầu gì không?"]


class UserInputValidatorAlgorithm(BaseAlgorithm):
    """User Input Validator Algorithm"""
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="UserInputValidator",
            name="User Input Validator",
            level="operational",
            category="core",
            version="2.0",
            description="Validates user input and generates clarifying questions if needed",
            
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("user_input", "string", True, "Raw user input"),
                    IOField("context", "object", False, "Conversation context")
                ],
                outputs=[
                    IOField("status", "string", True, "clear/ambiguous/unclear/dangerous"),
                    IOField("questions", "array", False, "Clarifying questions"),
                    IOField("confidence", "number", True, "Confidence 0-1"),
                    IOField("intent", "string", False, "Detected intent")
                ]
            ),
            
            steps=[
                "1. Check for gibberish",
                "2. Detect intent and entities",
                "3. Check for vague patterns",
                "4. Calculate confidence",
                "5. Generate questions if needed"
            ],
            
            tags=["input", "validation", "clarification", "core"]
        )
        
        self.validator = UserInputValidator()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        """Execute validation"""
        user_input = params.get("user_input", "")
        context = params.get("context", {})
        
        if not user_input:
            return AlgorithmResult(status="error", error="No input")
        
        result = self.validator.validate(user_input, context)
        
        return AlgorithmResult(
            status="success",
            data={
                "validation_status": result.status.value,
                "original_input": result.original_input,
                "clarifying_questions": result.clarifying_questions,
                "suggestions": result.suggestions,
                "confidence": result.confidence,
                "detected_intent": result.detected_intent,
                "detected_entities": result.detected_entities,
                "should_proceed": result.status == InputStatus.CLEAR,
                "needs_clarification": result.status in [InputStatus.AMBIGUOUS, InputStatus.UNCLEAR]
            }
        )


def register(algorithm_manager):
    """Register algorithm"""
    algo = UserInputValidatorAlgorithm()
    algorithm_manager.register("UserInputValidator", algo)
    print("✅ UserInputValidator Algorithm registered")


# ========================================
# TEST
# ========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📥 USER INPUT VALIDATOR TEST")
    print("="*60)
    
    validator = UserInputValidator()
    
    tests = [
        "asdjfaklsjdflkasjdf",            # ❌ Gibberish
        "tạo app",                         # ⚠️ Vague
        "fix",                             # ⚠️ Too short
        "tạo calculator app giống iPhone", # ✅ Clear
        "delete all",                      # 🚨 Dangerous
        "làm đẹp hơn",                     # ⚠️ Vague
        "tạo web app todo với React",      # ✅ Clear
    ]
    
    emoji_map = {
        InputStatus.CLEAR: "✅",
        InputStatus.AMBIGUOUS: "⚠️",
        InputStatus.UNCLEAR: "❌",
        InputStatus.DANGEROUS: "🚨"
    }
    
    for t in tests:
        r = validator.validate(t)
        print(f"\n   '{t}'")
        print(f"   → {emoji_map[r.status]} {r.status.value} ({r.confidence:.0%})")
        if r.clarifying_questions:
            print(f"   → Q: {r.clarifying_questions[0]}")
    
    print("\n" + "="*60)
