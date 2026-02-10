"""
Dive AI — Identity & Persona System
Surpasses OpenClaw's IDENTITY.md + SOUL.md + USER.md with:
  - Dynamic persona switching (multiple personas)
  - Live reload of personality rules
  - Conversation style adaptation
  - Relationship memory (tracks rapport over time)
  - Mood-aware response tuning
"""

import time
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class Mood(Enum):
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    EMPATHETIC = "empathetic"


@dataclass
class PersonaConfig:
    """Configuration for an agent persona."""
    name: str = "Dive AI"
    role: str = "AI coding assistant"
    emoji: str = "🤿"
    tone: str = "friendly and professional"
    humor_level: float = 0.5  # 0=none, 1=maximum
    verbosity: str = "balanced"  # terse, balanced, verbose
    language: str = "en"
    values: List[str] = field(default_factory=lambda: [
        "accuracy", "helpfulness", "honesty", "creativity",
    ])
    boundaries: List[str] = field(default_factory=lambda: [
        "No harmful content", "Respect privacy", "Acknowledge limitations",
    ])
    communication_rules: List[str] = field(default_factory=lambda: [
        "Use backticks for code references",
        "Explain reasoning before conclusions",
        "Ask for clarification when uncertain",
    ])
    custom_instructions: str = ""

    def to_system_prompt(self) -> str:
        """Generate system prompt from persona config."""
        lines = [
            f"You are {self.name}, a {self.role}.",
            f"Your communication style is {self.tone}.",
        ]

        if self.values:
            lines.append(f"Core values: {', '.join(self.values)}.")

        if self.communication_rules:
            lines.append("Communication rules:")
            for rule in self.communication_rules:
                lines.append(f"  - {rule}")

        if self.boundaries:
            lines.append("Boundaries:")
            for boundary in self.boundaries:
                lines.append(f"  - {boundary}")

        if self.custom_instructions:
            lines.append(f"\n{self.custom_instructions}")

        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Export persona to IDENTITY.md format."""
        lines = [
            "# Agent Identity",
            "",
            f"**Name**: {self.name}",
            f"**Role**: {self.role}",
            f"**Emoji**: {self.emoji}",
            f"**Tone**: {self.tone}",
            f"**Humor Level**: {self.humor_level}",
            f"**Verbosity**: {self.verbosity}",
            "",
            "## Values",
            "",
        ]
        for v in self.values:
            lines.append(f"- {v}")
        lines.extend(["", "## Communication Rules", ""])
        for r in self.communication_rules:
            lines.append(f"- {r}")
        lines.extend(["", "## Boundaries", ""])
        for b in self.boundaries:
            lines.append(f"- {b}")
        return "\n".join(lines)


@dataclass
class UserProfile:
    """User profile with preferences and patterns."""
    name: str = ""
    timezone: str = "UTC"
    language: str = "en"
    preferences: Dict[str, str] = field(default_factory=dict)
    work_patterns: List[str] = field(default_factory=list)
    communication_style: str = "default"
    expertise_level: str = "intermediate"
    frequently_used_tools: List[str] = field(default_factory=list)
    relationship_score: float = 0.5  # 0=new, 1=close
    interaction_count: int = 0

    def update_relationship(self):
        """Update relationship score based on interactions."""
        self.interaction_count += 1
        # Asymptotic growth toward 1.0
        self.relationship_score = min(
            0.95, 0.5 + 0.45 * (1 - 2 ** (-self.interaction_count / 20))
        )

    def to_markdown(self) -> str:
        """Export to USER.md format."""
        lines = [
            "# User Profile",
            "",
            f"**Name**: {self.name or 'Unknown'}",
            f"**Timezone**: {self.timezone}",
            f"**Language**: {self.language}",
            f"**Expertise**: {self.expertise_level}",
            f"**Relationship Score**: {self.relationship_score:.2f}",
            f"**Interactions**: {self.interaction_count}",
            "",
            "## Preferences",
            "",
        ]
        for k, v in self.preferences.items():
            lines.append(f"- **{k}**: {v}")
        if self.work_patterns:
            lines.extend(["", "## Work Patterns", ""])
            for p in self.work_patterns:
                lines.append(f"- {p}")
        return "\n".join(lines)


class IdentitySystem:
    """
    Manages agent identity, user profiles, and conversation personas.

    Surpasses OpenClaw by adding:
      - Multiple switchable personas (not just one IDENTITY.md)
      - Dynamic mood adaptation
      - Relationship tracking
      - Live persona reload
      - Conversation style learning
    """

    def __init__(self):
        self._personas: Dict[str, PersonaConfig] = {}
        self._active_persona: str = "default"
        self._user_profile = UserProfile()
        self._mood = Mood.NEUTRAL
        self._style_history: List[Dict] = []
        self._total_switches = 0

        # Register default persona
        self.register_persona("default", PersonaConfig())

    def register_persona(self, name: str, config: PersonaConfig):
        """Register a named persona."""
        self._personas[name] = config

    def switch_persona(self, name: str) -> bool:
        """Switch to a different persona."""
        if name in self._personas:
            self._active_persona = name
            self._total_switches += 1
            return True
        return False

    def get_active_persona(self) -> PersonaConfig:
        """Get the currently active persona config."""
        return self._personas.get(self._active_persona, PersonaConfig())

    def set_mood(self, mood: Mood):
        """Set the current conversation mood."""
        self._mood = mood

    def get_mood(self) -> Mood:
        """Get current mood."""
        return self._mood

    def adapt_to_user(self, message: str):
        """Adapt persona based on user message tone."""
        self._user_profile.update_relationship()

        msg_lower = message.lower()
        if any(w in msg_lower for w in ["thanks", "great", "awesome", "love"]):
            self._mood = Mood.FRIENDLY
        elif any(w in msg_lower for w in ["urgent", "critical", "asap", "broken"]):
            self._mood = Mood.SERIOUS
        elif any(w in msg_lower for w in ["help", "stuck", "confused", "frustrated"]):
            self._mood = Mood.EMPATHETIC
        elif any(w in msg_lower for w in ["lol", "haha", "funny", "joke"]):
            self._mood = Mood.PLAYFUL

        self._style_history.append({
            "mood": self._mood.value,
            "time": time.time(),
            "trigger": message[:50],
        })

    def get_system_prompt(self) -> str:
        """Get the full system prompt (persona + user context + mood)."""
        persona = self.get_active_persona()
        base = persona.to_system_prompt()

        # Add user context
        user = self._user_profile
        if user.name:
            base += f"\n\nUser: {user.name}"
        if user.timezone != "UTC":
            base += f" (timezone: {user.timezone})"
        if user.expertise_level != "intermediate":
            base += f"\nExpertise: {user.expertise_level}"

        # Mood modifier
        mood_mods = {
            Mood.FRIENDLY: "\nBe warm and encouraging.",
            Mood.SERIOUS: "\nBe direct and concise. Focus on solutions.",
            Mood.EMPATHETIC: "\nBe understanding and patient. Guide step-by-step.",
            Mood.PLAYFUL: "\nLighten the mood when appropriate.",
            Mood.PROFESSIONAL: "\nMaintain formal tone.",
        }
        if self._mood != Mood.NEUTRAL:
            base += mood_mods.get(self._mood, "")

        return base

    def set_user_profile(self, **kwargs):
        """Update user profile."""
        for key, value in kwargs.items():
            if hasattr(self._user_profile, key):
                setattr(self._user_profile, key, value)

    def get_user_profile(self) -> UserProfile:
        """Get user profile."""
        return self._user_profile

    def export_all(self) -> Dict[str, str]:
        """Export identity, soul, and user to markdown."""
        persona = self.get_active_persona()
        return {
            "IDENTITY.md": persona.to_markdown(),
            "USER.md": self._user_profile.to_markdown(),
            "SOUL.md": self._generate_soul_md(persona),
        }

    def _generate_soul_md(self, persona: PersonaConfig) -> str:
        """Generate SOUL.md from persona config."""
        lines = [
            "# Agent Soul",
            "",
            f"**Tone**: {persona.tone}",
            f"**Humor Level**: {persona.humor_level}",
            f"**Verbosity**: {persona.verbosity}",
            f"**Current Mood**: {self._mood.value}",
            "",
            "## Personality Rules",
            "",
        ]
        for rule in persona.communication_rules:
            lines.append(f"- {rule}")
        return "\n".join(lines)

    def get_stats(self) -> Dict:
        return {
            "total_personas": len(self._personas),
            "active_persona": self._active_persona,
            "current_mood": self._mood.value,
            "total_switches": self._total_switches,
            "user_interactions": self._user_profile.interaction_count,
            "relationship_score": round(self._user_profile.relationship_score, 3),
            "style_adaptations": len(self._style_history),
        }
