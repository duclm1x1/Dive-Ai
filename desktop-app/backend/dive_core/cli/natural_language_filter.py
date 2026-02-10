"""
Dive AI Natural Language Command Filter
Converts natural language input to CLI commands
Example: "check orchestrator status" → "dive orchestrator status"
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CommandCategory(Enum):
    """Command categories"""
    ORCHESTRATOR = "orchestrator"
    CODER = "coder"
    MEMORY = "memory"
    SEARCH = "search"
    SKILLS = "skills"
    MULTIMODAL = "multimodal"
    COMPUTER = "computer"
    ASK = "ask"
    CODE = "code"
    STATUS = "status"


@dataclass
class ParsedCommand:
    """Parsed natural language command"""
    category: CommandCategory
    action: str
    parameters: Dict[str, str]
    confidence: float
    original_text: str
    cli_command: str


class NaturalLanguageFilter:
    """
    Natural Language Command Filter
    
    Converts natural language input to CLI commands
    Examples:
    - "check status" → "dive status"
    - "check orchestrator status" → "dive orchestrator status"
    - "analyze code quality" → "dive code --task analyze"
    - "generate test cases for user.py" → "dive code --task test --file user.py"
    - "search for database patterns" → "dive search --query database patterns"
    - "store memory about project" → "dive memory --action store"
    """
    
    def __init__(self):
        """Initialize filter with command mappings"""
        self.logger = logging.getLogger(f"{__name__}.NaturalLanguageFilter")
        
        # Command patterns: (pattern, category, action, parameter_extractor)
        self.patterns = [
            # Status commands
            (r"(check|show|get|display|view)\s+(status|health|state)", 
             CommandCategory.STATUS, "status", self._extract_status_params),
            
            # Orchestrator commands
            (r"(check|show|get|display)\s+orchestrator\s+(status|health|state|agents|clusters)",
             CommandCategory.ORCHESTRATOR, "status", self._extract_orchestrator_params),
            (r"(execute|run|start)\s+(\d+)\s+(tasks|jobs)",
             CommandCategory.ORCHESTRATOR, "execute_tasks", self._extract_execute_params),
            (r"(scale|resize)\s+agents?\s+to\s+(\d+)",
             CommandCategory.ORCHESTRATOR, "scale", self._extract_scale_params),
            (r"(list|show|get)\s+(idle\s+)?agents?",
             CommandCategory.ORCHESTRATOR, "idle_agents", self._extract_agents_params),
            
            # Code commands
            (r"(generate|create|write|build)\s+(code|function|class|api|endpoint)",
             CommandCategory.CODE, "generate", self._extract_code_params),
            (r"(analyze|review|check|examine)\s+(code|quality|performance)",
             CommandCategory.CODE, "analyze", self._extract_code_params),
            (r"(fix|debug|repair)\s+(bug|error|issue|code)",
             CommandCategory.CODE, "fix", self._extract_code_params),
            (r"(test|create\s+test|generate\s+test)\s+(cases?|suite)",
             CommandCategory.CODE, "test", self._extract_code_params),
            
            # Memory commands
            (r"(store|save|add)\s+(memory|knowledge|info|data)",
             CommandCategory.MEMORY, "store", self._extract_memory_params),
            (r"(recall|retrieve|get|fetch)\s+(memory|knowledge|info|data)",
             CommandCategory.MEMORY, "recall", self._extract_memory_params),
            (r"(search|find|query)\s+(memory|knowledge)",
             CommandCategory.MEMORY, "search", self._extract_memory_params),
            
            # Search commands
            (r"(search|find|look\s+for|query)\s+(?:for\s+)?(.*)",
             CommandCategory.SEARCH, "search", self._extract_search_params),
            
            # Multimodal commands
            (r"(analyze|process|read)\s+(image|photo|picture|screenshot)",
             CommandCategory.MULTIMODAL, "vision", self._extract_vision_params),
            (r"(transcribe|convert|extract)\s+(audio|sound|voice|speech)",
             CommandCategory.MULTIMODAL, "audio", self._extract_audio_params),
            (r"(transform|convert|change)\s+(format|data|file)",
             CommandCategory.MULTIMODAL, "transform", self._extract_transform_params),
            
            # Computer use commands
            (r"(take|capture|screenshot|snap)",
             CommandCategory.COMPUTER, "screenshot", self._extract_computer_params),
            (r"(analyze|understand|read)\s+(screen|desktop|window)",
             CommandCategory.COMPUTER, "analyze", self._extract_computer_params),
            (r"(click|press|tap)\s+(?:at\s+)?(\d+)[,\s]+(\d+)",
             CommandCategory.COMPUTER, "click", self._extract_click_params),
            (r"(type|write|input)\s+(?:text\s+)?'([^']*)'",
             CommandCategory.COMPUTER, "type", self._extract_type_params),
            (r"(scroll|swipe)\s+(up|down|left|right)",
             CommandCategory.COMPUTER, "scroll", self._extract_scroll_params),
            (r"(navigate|go\s+to|open|visit)\s+(https?://[^\s]+|[^\s]+)",
             CommandCategory.COMPUTER, "navigate", self._extract_navigate_params),
            
            # Ask commands
            (r"(what|why|how|explain|tell|describe)\s+(is|are|about|regarding)",
             CommandCategory.ASK, "ask", self._extract_ask_params),
            (r"^(.+)\?$",  # Anything ending with ?
             CommandCategory.ASK, "ask", self._extract_ask_params),
        ]
    
    def parse(self, text: str) -> Optional[ParsedCommand]:
        """
        Parse natural language text to command
        
        Args:
            text: Natural language input
            
        Returns:
            ParsedCommand or None if no match
        """
        text = text.strip().lower()
        
        self.logger.debug(f"Parsing: {text}")
        
        # Try each pattern
        for pattern, category, action, param_extractor in self.patterns:
            match = re.search(pattern, text)
            if match:
                # Extract parameters
                params = param_extractor(text, match)
                
                # Build CLI command
                cli_command = self._build_cli_command(category, action, params)
                
                result = ParsedCommand(
                    category=category,
                    action=action,
                    parameters=params,
                    confidence=0.95,  # High confidence for regex match
                    original_text=text,
                    cli_command=cli_command
                )
                
                self.logger.info(f"Parsed command: {result.cli_command}")
                return result
        
        # No pattern matched - try LLM-based parsing
        self.logger.warning(f"No pattern matched for: {text}")
        return None
    
    def _build_cli_command(self, category: CommandCategory, action: str, 
                          params: Dict[str, str]) -> str:
        """Build CLI command from parsed components"""
        cmd = ["dive"]
        
        # Add category if not status
        if category != CommandCategory.STATUS:
            cmd.append(category.value)
        
        # Add action if different from category
        if action != category.value:
            cmd.append(action.replace("_", "-"))
        
        # Add parameters
        for key, value in params.items():
            if value:
                cmd.append(f"--{key.replace('_', '-')}")
                cmd.append(str(value))
        
        return " ".join(cmd)
    
    # Parameter extractors
    def _extract_status_params(self, text: str, match) -> Dict[str, str]:
        """Extract status command parameters"""
        return {}
    
    def _extract_orchestrator_params(self, text: str, match) -> Dict[str, str]:
        """Extract orchestrator command parameters"""
        return {}
    
    def _extract_execute_params(self, text: str, match) -> Dict[str, str]:
        """Extract execute tasks parameters"""
        num_tasks = match.group(2)
        return {"num_tasks": num_tasks, "parallel": num_tasks}
    
    def _extract_scale_params(self, text: str, match) -> Dict[str, str]:
        """Extract scale parameters"""
        target_count = match.group(2)
        return {"target_count": target_count}
    
    def _extract_agents_params(self, text: str, match) -> Dict[str, str]:
        """Extract agents parameters"""
        return {}
    
    def _extract_code_params(self, text: str, match) -> Dict[str, str]:
        """Extract code command parameters"""
        # Extract task description
        task_desc = text.replace(match.group(0), "").strip()
        return {"task": task_desc} if task_desc else {}
    
    def _extract_memory_params(self, text: str, match) -> Dict[str, str]:
        """Extract memory command parameters"""
        action = match.group(1).lower()
        action_map = {
            "store": "store",
            "save": "store",
            "add": "store",
            "recall": "recall",
            "retrieve": "recall",
            "get": "recall",
            "fetch": "recall",
            "search": "search",
            "find": "search",
            "query": "search"
        }
        return {"action": action_map.get(action, "store")}
    
    def _extract_search_params(self, text: str, match) -> Dict[str, str]:
        """Extract search parameters"""
        query = match.group(1) if match.lastindex >= 1 else ""
        return {"query": query.strip()} if query.strip() else {}
    
    def _extract_vision_params(self, text: str, match) -> Dict[str, str]:
        """Extract vision parameters"""
        # Try to extract image path
        path_match = re.search(r"(?:image|photo|picture|screenshot)\s+(?:at|from|of)\s+([^\s]+)", text)
        if path_match:
            return {"image": path_match.group(1), "task": "analyze"}
        return {"task": "analyze"}
    
    def _extract_audio_params(self, text: str, match) -> Dict[str, str]:
        """Extract audio parameters"""
        path_match = re.search(r"(?:audio|sound|voice|speech)\s+(?:at|from|of)\s+([^\s]+)", text)
        if path_match:
            return {"audio": path_match.group(1), "task": "transcribe"}
        return {"task": "transcribe"}
    
    def _extract_transform_params(self, text: str, match) -> Dict[str, str]:
        """Extract transform parameters"""
        # Try to extract from/to formats
        from_match = re.search(r"from\s+(\w+)", text)
        to_match = re.search(r"to\s+(\w+)", text)
        
        params = {}
        if from_match:
            params["from_format"] = from_match.group(1)
        if to_match:
            params["to_format"] = to_match.group(1)
        
        return params
    
    def _extract_computer_params(self, text: str, match) -> Dict[str, str]:
        """Extract computer use parameters"""
        return {}
    
    def _extract_click_params(self, text: str, match) -> Dict[str, str]:
        """Extract click parameters"""
        return {"x": match.group(2), "y": match.group(3)}
    
    def _extract_type_params(self, text: str, match) -> Dict[str, str]:
        """Extract type parameters"""
        return {"text": match.group(1)}
    
    def _extract_scroll_params(self, text: str, match) -> Dict[str, str]:
        """Extract scroll parameters"""
        return {"direction": match.group(2)}
    
    def _extract_navigate_params(self, text: str, match) -> Dict[str, str]:
        """Extract navigate parameters"""
        url = match.group(2)
        # Add protocol if missing
        if not url.startswith("http"):
            url = "https://" + url
        return {"url": url}
    
    def _extract_ask_params(self, text: str, match) -> Dict[str, str]:
        """Extract ask parameters"""
        # Remove question mark if present
        question = text.rstrip("?").strip()
        return {"prompt": question}
    
    def get_suggestions(self, partial_text: str) -> List[str]:
        """Get command suggestions for partial input"""
        suggestions = []
        
        # Common commands
        common_commands = [
            "check status",
            "check orchestrator status",
            "execute 100 tasks",
            "generate code for",
            "analyze code quality",
            "search for",
            "store memory about",
            "take screenshot",
            "navigate to",
        ]
        
        partial_lower = partial_text.lower()
        for cmd in common_commands:
            if cmd.startswith(partial_lower):
                suggestions.append(cmd)
        
        return suggestions[:5]  # Return top 5 suggestions
