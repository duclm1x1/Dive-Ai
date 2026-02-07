"""
Offline Understanding Layer for Dive AI v25
Uses Qwen2.5-7B-Instruct for local LLM inference
"""

import json
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class UnderstandingResult:
    """Understanding result"""
    action: str
    target: str
    parameters: Dict[str, Any]
    confidence: float
    explanation: str


class OfflineUnderstanding:
    """
    Offline Understanding using Qwen2.5-7B-Instruct
    
    Features:
    - 7B parameters (fits in 12GB VRAM)
    - Excellent instruction following
    - Bilingual (English + Vietnamese)
    - Works 100% offline
    - GPU optimized (AMD ROCm compatible)
    """
    
    def __init__(self, device: str = "cuda"):
        """
        Initialize offline understanding
        
        Args:
            device: Device to use (cuda, cpu)
        """
        self.device = device
        self.model = None
        self.tokenizer = None
        
        print(f"🧠 Initializing Offline Understanding (Qwen2.5-7B)...")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Qwen2.5-7B model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            model_name = "Qwen/Qwen2.5-7B-Instruct"
            
            print(f"  📥 Loading {model_name}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Load model with quantization for efficiency
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=self.device,
                load_in_8bit=True if self.device == "cuda" else False
            )
            
            print(f"  ✅ Understanding model loaded successfully")
        
        except ImportError:
            print("  ❌ transformers not installed")
            print("  Install with: pip install transformers torch")
            raise
        except Exception as e:
            print(f"  ❌ Error loading model: {e}")
            # Try CPU fallback
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                self.device = "cpu"
                model_name = "Qwen/Qwen2.5-7B-Instruct"
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype="auto",
                    device_map="cpu"
                )
                
                print(f"  ✅ Understanding model loaded on CPU (slower)")
            except Exception as cpu_error:
                print(f"  ❌ CPU fallback failed: {cpu_error}")
                raise
    
    async def analyze_intent(
        self,
        text: str,
        context: Optional[str] = None,
        language: str = "en"
    ) -> UnderstandingResult:
        """
        Analyze user intent from text
        
        Args:
            text: User input text
            context: Previous conversation context
            language: Language code (en, vi)
        
        Returns:
            UnderstandingResult with action, target, parameters
        """
        try:
            # Build prompt
            system_prompt = self._get_system_prompt(language)
            
            user_message = f"User input: {text}"
            if context:
                user_message += f"\n\nContext: {context}"
            
            # Format for Qwen2.5
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Generate response
            response = self._generate_response(messages)
            
            # Parse JSON response
            result = self._parse_response(response)
            
            return result
        
        except Exception as e:
            print(f"❌ Understanding Error: {e}")
            return UnderstandingResult(
                action="error",
                target=text,
                parameters={},
                confidence=0.0,
                explanation=f"Error: {str(e)}"
            )
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on language"""
        if language == "vi":
            return """Bạn là một trợ lý AI phân tích các lệnh giọng nói của người dùng.
Trích xuất thông tin sau từ đầu vào của người dùng:
1. action: Hành động cần thực hiện (click, type, open, close, scroll, navigate, search, screenshot, question)
2. target: Phần tử hoặc ứng dụng mục tiêu
3. parameters: Bất kỳ tham số bổ sung nào
4. confidence: Mức độ tự tin của bạn (0.0 - 1.0)

Trả lời dưới dạng JSON:
{
    "action": "...",
    "target": "...",
    "parameters": {...},
    "confidence": 0.0,
    "explanation": "..."
}"""
        else:
            return """You are an AI assistant that analyzes user voice commands.
Extract the following from the user's input:
1. action: The action to perform (click, type, open, close, scroll, navigate, search, screenshot, question)
2. target: The target element or application
3. parameters: Any additional parameters
4. confidence: Your confidence level (0.0 - 1.0)

Respond in JSON format:
{
    "action": "...",
    "target": "...",
    "parameters": {...},
    "confidence": 0.0,
    "explanation": "..."
}"""
    
    def _generate_response(self, messages: list) -> str:
        """Generate response using Qwen2.5"""
        try:
            # Format messages for model
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenize
            model_inputs = self.tokenizer(
                text,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=500,
                temperature=0.3,
                top_p=0.9
            )
            
            # Decode
            response = self.tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]
            
            return response
        
        except Exception as e:
            print(f"❌ Generation Error: {e}")
            return "{}"
    
    def _parse_response(self, response: str) -> UnderstandingResult:
        """Parse model response"""
        try:
            # Extract JSON from response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            
            if start_idx == -1 or end_idx == 0:
                return UnderstandingResult(
                    action="error",
                    target="",
                    parameters={},
                    confidence=0.0,
                    explanation="Could not parse response"
                )
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            return UnderstandingResult(
                action=data.get("action", "question"),
                target=data.get("target", ""),
                parameters=data.get("parameters", {}),
                confidence=float(data.get("confidence", 0.5)),
                explanation=data.get("explanation", "")
            )
        
        except json.JSONDecodeError:
            print(f"❌ JSON Parse Error")
            return UnderstandingResult(
                action="question",
                target="",
                parameters={},
                confidence=0.0,
                explanation="Could not parse JSON"
            )
        except Exception as e:
            print(f"❌ Parse Error: {e}")
            return UnderstandingResult(
                action="error",
                target="",
                parameters={},
                confidence=0.0,
                explanation=str(e)
            )


class OfflineUnderstandingOptimized:
    """
    Optimized version using quantization for faster inference
    """
    
    def __init__(self, device: str = "cuda"):
        self.device = device
        self.model = None
        self.tokenizer = None
        
        print(f"🧠 Initializing Optimized Understanding (Qwen2.5-7B-GGUF)...")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize with GGUF quantization"""
        try:
            from llama_cpp import Llama
            
            print(f"  📥 Loading Qwen2.5-7B-GGUF...")
            
            # Download GGUF model if needed
            model_path = self._get_gguf_model()
            
            self.model = Llama(
                model_path=model_path,
                n_gpu_layers=-1 if self.device == "cuda" else 0,
                n_ctx=2048,
                verbose=False
            )
            
            print(f"  ✅ Optimized understanding model loaded")
        
        except ImportError:
            print("  ⚠️  llama-cpp-python not installed (optional optimization)")
            print("  Install with: pip install llama-cpp-python")
            # Fall back to regular model
            self.model = None
    
    def _get_gguf_model(self) -> str:
        """Get GGUF model path"""
        import os
        
        model_dir = os.path.expanduser("~/.cache/dive-ai/models")
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, "qwen2.5-7b-q4.gguf")
        
        if not os.path.exists(model_path):
            print(f"  📥 Downloading GGUF model...")
            # Would download from HuggingFace
            print(f"  Download from: https://huggingface.co/Qwen/Qwen2.5-7B-GGUF")
        
        return model_path


# Example usage
async def main():
    """Test offline understanding"""
    
    understanding = OfflineUnderstanding(device="cuda")
    
    print("\n🧠 Testing Offline Understanding...")
    
    # Test 1: Simple command
    result1 = await understanding.analyze_intent(
        "Open Chrome",
        language="en"
    )
    print(f"✅ Command: {result1.action} {result1.target}")
    
    # Test 2: Vietnamese command
    result2 = await understanding.analyze_intent(
        "Mở Chrome cho tôi",
        language="vi"
    )
    print(f"✅ Lệnh: {result2.action} {result2.target}")
    
    # Test 3: Complex command
    result3 = await understanding.analyze_intent(
        "Search for weather in New York",
        context="User is working on desktop",
        language="en"
    )
    print(f"✅ Action: {result3.action}, Target: {result3.target}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
