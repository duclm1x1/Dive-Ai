"""
V98 Highest Tier Model Client
Only uses the most advanced models available

Allowed Models (Priority Order):
1. ChatGPT 5.2 Pro (Latest)
2. Thinking Models
3. Gemini 3.0 Pro
4. Claude Opus 4.5
5. Claude Sonnet 4.5

DO NOT USE: gpt-3.5, gpt-4, claude-2, claude-3, gemini-1, gemini-2
"""

import os
import logging
from typing import Optional, List, Dict, Any, AsyncIterator
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class V98HighestTierClient:
    """
    V98 API Client that only uses highest-tier models.
    
    Model Selection Strategy:
    - always_latest: Use the newest model available
    - performance: Balance speed and quality
    - quality: Prioritize highest quality
    """
    
    # Highest tier models only (in priority order)
    ALLOWED_MODELS = [
        "chatgpt-5.2-pro",
        "o1-pro",  # Thinking model
        "o1",      # Thinking model
        "gemini-3.0-pro",
        "claude-opus-4.5",
        "claude-sonnet-4.5",
    ]
    
    # Blocked models (too old or low quality)
    BLOCKED_MODELS = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "claude-2",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3.5-sonnet",
        "gemini-1.0-pro",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        strategy: str = "always_latest"
    ):
        """
        Initialize V98 Highest Tier Client.
        
        Args:
            api_key: V98 API key (defaults to env var)
            base_url: V98 base URL (defaults to env var)
            model: Preferred model (must be in ALLOWED_MODELS)
            strategy: Model selection strategy
        """
        self.api_key = api_key or os.getenv("V98_API_KEY")
        self.base_url = base_url or os.getenv("V98_BASE_URL", "https://v98store.com/v1")
        self.strategy = strategy or os.getenv("MODEL_SELECTION_STRATEGY", "always_latest")
        
        # Validate and set model
        self.model = self._validate_model(model or os.getenv("V98_MODEL", "chatgpt-5.2-pro"))
        
        # Fallback models
        self.fallback_models = [
            os.getenv("V98_MODEL_FALLBACK_1", "gemini-3.0-pro"),
            os.getenv("V98_MODEL_FALLBACK_2", "claude-opus-4.5"),
            os.getenv("V98_MODEL_FALLBACK_3", "claude-sonnet-4.5"),
        ]
        
        # Initialize clients
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(f"V98 Highest Tier Client initialized with model: {self.model}")
        logger.info(f"Strategy: {self.strategy}")
        logger.info(f"Fallback models: {self.fallback_models}")
    
    def _validate_model(self, model: str) -> str:
        """
        Validate model is in allowed list.
        
        Args:
            model: Model name to validate
            
        Returns:
            Validated model name
            
        Raises:
            ValueError: If model is blocked or not allowed
        """
        # Check if blocked
        for blocked in self.BLOCKED_MODELS:
            if blocked in model.lower():
                raise ValueError(
                    f"Model '{model}' is BLOCKED. "
                    f"Only highest-tier models allowed: {self.ALLOWED_MODELS}"
                )
        
        # Check if allowed
        if model not in self.ALLOWED_MODELS:
            logger.warning(
                f"Model '{model}' not in allowed list. "
                f"Using default: {self.ALLOWED_MODELS[0]}"
            )
            return self.ALLOWED_MODELS[0]
        
        return model
    
    def _select_model(self, requested_model: Optional[str] = None) -> str:
        """
        Select best model based on strategy.
        
        Args:
            requested_model: Specific model requested
            
        Returns:
            Selected model name
        """
        if requested_model:
            return self._validate_model(requested_model)
        
        if self.strategy == "always_latest":
            # Always use the first model in ALLOWED_MODELS (newest)
            return self.ALLOWED_MODELS[0]
        
        elif self.strategy == "performance":
            # Balance speed and quality - use Gemini 3.0 Pro
            return "gemini-3.0-pro"
        
        elif self.strategy == "quality":
            # Prioritize quality - use Claude Opus 4.5
            return "claude-opus-4.5"
        
        else:
            return self.model
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Generate response using highest-tier model.
        
        Args:
            prompt: User prompt
            model: Specific model to use (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments
            
        Returns:
            Generated response text
        """
        selected_model = self._select_model(model)
        
        try:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            logger.info(f"✅ Generated response with {selected_model}")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error with {selected_model}: {e}")
            
            # Try fallback models
            for fallback in self.fallback_models:
                try:
                    logger.info(f"Trying fallback model: {fallback}")
                    response = self.client.chat.completions.create(
                        model=fallback,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    logger.info(f"✅ Generated response with fallback {fallback}")
                    return response.choices[0].message.content
                    
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback {fallback} also failed: {fallback_error}")
                    continue
            
            # All models failed
            raise Exception(f"All models failed. Last error: {e}")
    
    async def generate_async(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Async generate response using highest-tier model.
        
        Args:
            prompt: User prompt
            model: Specific model to use (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments
            
        Returns:
            Generated response text
        """
        selected_model = self._select_model(model)
        
        try:
            response = await self.async_client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            logger.info(f"✅ Generated async response with {selected_model}")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Async error with {selected_model}: {e}")
            
            # Try fallback models
            for fallback in self.fallback_models:
                try:
                    logger.info(f"Trying async fallback model: {fallback}")
                    response = await self.async_client.chat.completions.create(
                        model=fallback,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    logger.info(f"✅ Generated async response with fallback {fallback}")
                    return response.choices[0].message.content
                    
                except Exception as fallback_error:
                    logger.error(f"❌ Async fallback {fallback} also failed: {fallback_error}")
                    continue
            
            # All models failed
            raise Exception(f"All async models failed. Last error: {e}")
    
    async def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream generate response using highest-tier model.
        
        Args:
            prompt: User prompt
            model: Specific model to use (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments
            
        Yields:
            Response chunks
        """
        selected_model = self._select_model(model)
        
        try:
            stream = await self.async_client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ Stream error with {selected_model}: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available highest-tier models."""
        return self.ALLOWED_MODELS.copy()
    
    def get_blocked_models(self) -> List[str]:
        """Get list of blocked models."""
        return self.BLOCKED_MODELS.copy()
    
    def is_model_allowed(self, model: str) -> bool:
        """Check if model is allowed."""
        try:
            self._validate_model(model)
            return True
        except ValueError:
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create client
    client = V98HighestTierClient()
    
    print(f"Using model: {client.model}")
    print(f"Available models: {client.get_available_models()}")
    print(f"Blocked models: {client.get_blocked_models()}")
    
    # Test generation
    try:
        response = client.generate("What is 2+2?", max_tokens=50)
        print(f"\nResponse: {response}")
    except Exception as e:
        print(f"\nError: {e}")
