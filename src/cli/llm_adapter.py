#!/usr/bin/env python3
"""
Dive AI CLI - LLM Adapter
===========================
Lightweight LLM client that connects directly to OpenAI-compatible APIs.
Supports smart routing: simple tasks → cheap model, complex → powerful model.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("dive-llm")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class DiveLLM:
    """
    Lightweight LLM adapter with smart model routing.

    Routes tasks to appropriate models based on complexity:
    - nano: Simple Q&A, formatting, classification (~$0.0001/call)
    - mini: Standard coding, analysis, generation (~$0.001/call)
    - flash: Complex reasoning, multi-step, architecture (~$0.005/call)
    """

    COMPLEXITY_KEYWORDS = {
        "simple": ["format", "list", "count", "name", "what is", "define", "translate"],
        "complex": ["architect", "design system", "refactor entire", "security audit",
                     "optimize performance", "debug complex", "multi-step", "compare and contrast"],
    }

    def __init__(self, config=None):
        if not HAS_OPENAI:
            raise ImportError("openai package required. Install: pip install openai")

        from src.cli.config import DiveConfig
        self.config = config or DiveConfig.load()

        client_kwargs = {}
        if self.config.llm.api_key:
            client_kwargs["api_key"] = self.config.llm.api_key
        if self.config.llm.base_url:
            client_kwargs["base_url"] = self.config.llm.base_url

        self.client = OpenAI(**client_kwargs)

        self.models = {
            "fast": self.config.llm.fast_model,
            "standard": self.config.llm.standard_model,
            "power": self.config.llm.power_model,
        }

    def _assess_complexity(self, prompt: str) -> str:
        """Assess task complexity to route to appropriate model."""
        prompt_lower = prompt.lower()
        word_count = len(prompt.split())

        # Short prompts are usually simple
        if word_count < 20:
            for kw in self.COMPLEXITY_KEYWORDS["simple"]:
                if kw in prompt_lower:
                    return "fast"

        # Complex keywords
        for kw in self.COMPLEXITY_KEYWORDS["complex"]:
            if kw in prompt_lower:
                return "power"

        # Default to standard
        return "standard"

    def _select_model(self, prompt: str, model_override: Optional[str] = None) -> str:
        """Select the best model for the task."""
        if model_override:
            return model_override

        tier = self._assess_complexity(prompt)
        model = self.models.get(tier, self.config.llm.model)
        logger.debug(f"Complexity: {tier} → Model: {model}")
        return model

    def chat(self, prompt: str, system: Optional[str] = None,
             model: Optional[str] = None, temperature: Optional[float] = None,
             max_tokens: Optional[int] = None, json_mode: bool = False) -> Dict[str, Any]:
        """
        Send a chat completion request with smart model routing.

        Returns:
            dict with keys: content, model, usage, tier
        """
        selected_model = self._select_model(prompt, model)
        messages = []

        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature or self.config.llm.temperature,
            "max_tokens": max_tokens or self.config.llm.max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return {
                "content": content,
                "model": selected_model,
                "usage": usage,
                "tier": self._assess_complexity(prompt),
            }

        except Exception as e:
            logger.error(f"LLM error: {e}")
            return {
                "content": None,
                "model": selected_model,
                "error": str(e),
                "tier": "error",
            }

    def code(self, task: str, language: str = "python",
             context: Optional[str] = None, action: str = "generate") -> Dict[str, Any]:
        """
        Specialized coding endpoint.
        Actions: generate, review, debug, refactor, test, explain
        """
        system_prompts = {
            "generate": f"You are Dive AI Coder, an expert {language} developer. Generate clean, production-ready code. Include comments and type hints. Output ONLY the code, no explanations.",
            "review": f"You are Dive AI Code Reviewer. Review the following {language} code. Identify bugs, security issues, performance problems, and style issues. Output a structured review.",
            "debug": f"You are Dive AI Debugger. Analyze the following {language} code and identify the bug. Explain the root cause and provide the fix.",
            "refactor": f"You are Dive AI Refactorer. Refactor the following {language} code to improve readability, performance, and maintainability. Preserve all functionality.",
            "test": f"You are Dive AI Test Engineer. Generate comprehensive unit tests for the following {language} code. Use pytest for Python, jest for JavaScript.",
            "explain": f"You are Dive AI Code Explainer. Explain the following {language} code in detail, including its purpose, logic flow, and key patterns used.",
        }

        system = system_prompts.get(action, system_prompts["generate"])
        prompt = task
        if context:
            prompt = f"Context:\n```{language}\n{context}\n```\n\nTask: {task}"

        # Code tasks are at least standard complexity
        model = self.models["standard"] if action == "generate" else self.models["power"]

        return self.chat(prompt, system=system, model=model)

    def quick(self, prompt: str) -> str:
        """Quick answer using the fastest/cheapest model. Returns just the text."""
        result = self.chat(prompt, model=self.models["fast"], max_tokens=500)
        return result.get("content", "")
