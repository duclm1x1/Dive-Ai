"""
LLM Connection - Core Skill #1

Universal LLM provider connection with Three-Mode Communication.
Supports ANY LLM provider with optimal performance.

Version: V26.0
Status: Core Skill (Foundation)
"""

from .llm_connection import (
    LLMClientThreeMode as LLMConnection,
    LLMRequest,
    LLMResponse,
    CommunicationMode
)

from .three_mode_core import (
    ThreeModeCore,
    VisionThreeMode,
    HearThreeMode,
    TransformerThreeMode
)

__all__ = [
    'LLMConnection',
    'LLMRequest',
    'LLMResponse',
    'CommunicationMode',
    'ThreeModeCore',
    'VisionThreeMode',
    'HearThreeMode',
    'TransformerThreeMode'
]

__version__ = '26.0'
__status__ = 'Core Skill'
