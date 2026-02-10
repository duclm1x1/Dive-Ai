"""
Dive AI V29.4 Desktop App Builder
Uses existing LLM connection algorithms to generate code

This script orchestrates V98 and AICoding connections to:
1. Generate Electron app structure
2. Generate React components
3. Generate Backend APIs
4. Review and optimize code
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add project paths
sys.path.insert(0, r"D:\Antigravity\Dive-AI-v29 structle\Dive-AI-v29\src")
sys.path.insert(0, r"D:\Antigravity\Dive AI")

# Import existing algorithms
from core.algorithms.tactical.connection_v98 import ConnectionV98Algorithm, get_v98_connection
from core.algorithms.tactical.connection_aicoding import ConnectionAICodecAlgorithm, get_aicoding_connection
from core.algorithms.tactical.code_writer_v2 import CodeWriterV2Algorithm, generate_code

# Output directory
OUTPUT_DIR = Path(r"D:\Antigravity\Dive AI\desktop-app")


class DesktopAppBuilder:
    """
    Uses V98 and AICoding connections to build Dive AI Desktop App
    
    Task Distribution:
    - V98 (Claude 4.6 Opus): Primary code generation
    - AICoding (Claude 4.6): Code review and optimization
    """
    
    def __init__(self):
        self.v98_client = None
        self.aicoding_client = None
        self.code_writer = CodeWriterV2Algorithm()
        self.tasks_completed = 0
        self.tasks_failed = 0
        
        # Task definitions
        self.tasks = [
            # Phase 1: Core Infrastructure
            {
                "id": "1",
                "name": "Electron Main Process",
                "file": "electron/main.ts",
                "provider": "v98",
                "prompt": """Create a complete Electron main.ts for Dive AI V29.4 Desktop App with:
- BrowserWindow with dark theme (bg: #1a1a2e)
- IPC handlers for gateway communication (localhost:1879)
- Screenshot capture via IPC
- Automation action execution via IPC
- Window controls (minimize, maximize, close)
- Auto DevTools in development mode
Export as TypeScript module.""",
                "language": "typescript"
            },
            {
                "id": "2", 
                "name": "Preload Bridge",
                "file": "electron/preload.ts",
                "provider": "v98",
                "prompt": """Create Electron preload.ts for Dive AI with contextBridge exposing:
- gateway.request(endpoint, data) - POST to Gateway
- gateway.chat(message, context) - Chat API
- gateway.health() - Health check
- automation.screenshot() - Capture screen
- automation.execute(action, params) - Execute automation
- fs.readFile(path), fs.writeFile(path, content)
- terminal.execute(command, cwd)
Use TypeScript with proper types.""",
                "language": "typescript"
            },
            {
                "id": "3",
                "name": "Gateway Server",
                "file": "backend/gateway_server.py",
                "provider": "v98",
                "prompt": """Create FastAPI gateway_server.py for Dive AI Desktop:
- POST /chat - Chat with V98/AICoding Claude 4.6
- POST /chat/stream - Streaming response
- GET /health - Health check with LLM status
- GET /automation/screenshot - Capture via PIL ImageGrab
- POST /automation/execute - PyAutoGUI actions (click, type, keypress)
- POST /terminal/execute - subprocess.run commands
- POST /fs/read, POST /fs/write
- CORS enabled for Electron
- Use existing connection algorithms for LLM
Port 1879, include all imports and error handling.""",
                "language": "python"
            },
            
            # Phase 2: React Components
            {
                "id": "4",
                "name": "App.tsx",
                "file": "src/App.tsx",
                "provider": "v98",
                "prompt": """Create React App.tsx for Dive AI Desktop with:
- Tabbed interface: Chat, Browser, Code, Terminal, Desktop
- Sidebar with tab buttons and icons
- Gateway connection status indicator
- Import all components from ./components/
- CSS import from ./App.css
- Use TypeScript with proper types
Dark theme, modern UI design.""",
                "language": "typescript"
            },
            {
                "id": "5",
                "name": "AI Chat Component",
                "file": "src/components/AIChat/AIChat.tsx",
                "provider": "v98",
                "prompt": """Create React AIChat.tsx component:
- Message list with user/assistant messages
- Input field with send button
- Scroll to bottom on new messages
- Call window.diveAPI.gateway.chat()
- Show algorithm used in responses
- Loading state with typing indicator
- Welcome message when empty
CSS in separate file, TypeScript.""",
                "language": "typescript"
            },
            {
                "id": "6",
                "name": "Code Editor",
                "file": "src/components/CodeEditor/CodeEditor.tsx",
                "provider": "v98",
                "prompt": """Create React CodeEditor.tsx with Monaco editor:
- Monaco Editor integration (@monaco-editor/react)
- Language selector (python, javascript, typescript, etc.)
- File path input with Open/Save buttons
- AI assistant panel (ask AI about code)
- Quick prompts: Explain, Fix Bugs, Optimize, Comment
- Output display for AI responses
TypeScript, modern styling.""",
                "language": "typescript"
            },
            {
                "id": "7",
                "name": "Terminal Component",
                "file": "src/components/Terminal/Terminal.tsx",
                "provider": "v98",
                "prompt": """Create React Terminal.tsx component:
- Terminal-like interface with monospace font
- Command history with arrow key navigation
- Execute commands via window.diveAPI.terminal.execute()
- Display output with different colors for stdin/stdout/stderr
- Built-in commands: clear, cd
- Current working directory display
TypeScript, xterm-like styling.""",
                "language": "typescript"
            },
            {
                "id": "8",
                "name": "Desktop Controller",
                "file": "src/components/Desktop/DesktopController.tsx",
                "provider": "v98",
                "prompt": """Create React DesktopController.tsx:
- Screenshot preview area with refresh button
- Natural language instruction input
- Execute button to run UI-TARS automation
- Quick action buttons (screenshot, click, type, keypress)
- Result display (success/error)
- Capabilities list
Call window.diveAPI.automation APIs, TypeScript.""",
                "language": "typescript"
            },
            {
                "id": "9",
                "name": "Browser View",
                "file": "src/components/Browser/BrowserView.tsx",
                "provider": "v98",
                "prompt": """Create React BrowserView.tsx:
- URL bar with navigation buttons (back, forward, refresh)
- Iframe for web content display
- Automation panel with instruction input
- Quick actions: scrape, click, fill form, screenshot
- Results display
- Capabilities list
TypeScript, modern UI.""",
                "language": "typescript"
            },
            
            # Phase 3: Code Review
            {
                "id": "10",
                "name": "Review & Optimize All Code",
                "file": None,  # Review only
                "provider": "aicoding",
                "prompt": """Review the generated Dive AI Desktop App code for:
1. Best practices compliance
2. Error handling completeness
3. TypeScript type safety
4. Performance optimizations
5. Security considerations

Provide a summary of issues found and recommendations.""",
                "language": "text"
            }
        ]
    
    def initialize_connections(self):
        """Initialize V98 and AICoding connections"""
        print("🔌 Initializing LLM connections...")
        
        # V98 Connection
        v98_result = get_v98_connection(model="claude-opus-4-6-thinking", verify=True)
        if v98_result.status == "success":
            self.v98_client = v98_result.data["client"]
            print(f"   ✅ V98: {v98_result.data['selected_model']} ({v98_result.data['latency_ms']:.0f}ms)")
        else:
            print(f"   ❌ V98: {v98_result.data.get('error')}")
        
        # AICoding Connection
        aicoding_result = get_aicoding_connection(model="claude-opus-4.6", verify=True)
        if aicoding_result.status == "success":
            self.aicoding_client = aicoding_result.data["client"]
            print(f"   ✅ AICoding: {aicoding_result.data['selected_model']} ({aicoding_result.data['latency_ms']:.0f}ms)")
        else:
            print(f"   ❌ AICoding: {aicoding_result.data.get('error')}")
        
        return self.v98_client is not None or self.aicoding_client is not None
    
    def execute_task(self, task: dict) -> dict:
        """Execute a single task using assigned provider"""
        print(f"\n📝 Task {task['id']}: {task['name']} ({task['provider'].upper()})")
        
        try:
            # Select client
            if task["provider"] == "v98" and self.v98_client:
                client = self.v98_client
            elif task["provider"] == "aicoding" and self.aicoding_client:
                client = self.aicoding_client
            elif self.v98_client:
                client = self.v98_client
                print(f"   ⚠️ Using V98 as fallback")
            elif self.aicoding_client:
                client = self.aicoding_client
                print(f"   ⚠️ Using AICoding as fallback")
            else:
                return {"status": "failed", "error": "No LLM client available"}
            
            # Generate code
            response = client.chat_completion(
                messages=[
                    {"role": "system", "content": f"You are an expert {task['language']} developer. Generate production-ready code."},
                    {"role": "user", "content": task["prompt"]}
                ],
                temperature=0.2
            )
            
            # Write to file
            if task["file"]:
                file_path = OUTPUT_DIR / task["file"]
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract code from response
                code = self._extract_code(response, task["language"])
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                print(f"   ✅ Generated: {task['file']} ({len(code)} chars)")
                self.tasks_completed += 1
                return {"status": "success", "file": str(file_path), "size": len(code)}
            else:
                # Review task
                print(f"   📋 Review complete")
                self.tasks_completed += 1
                return {"status": "success", "review": response[:500]}
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.tasks_failed += 1
            return {"status": "failed", "error": str(e)}
    
    def _extract_code(self, response: str, language: str) -> str:
        """Extract code from LLM response"""
        import re
        
        # Try to find code block
        patterns = [
            rf'```{language}\n(.*?)```',
            rf'```{language[:2]}\n(.*?)```',
            r'```\n(.*?)```',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Return full response if no code block
        return response.strip()
    
    def build(self):
        """Build the complete Desktop App"""
        print("=" * 60)
        print("🦞 Dive AI V29.4 Desktop App Builder")
        print("=" * 60)
        print(f"   Output: {OUTPUT_DIR}")
        print(f"   Tasks: {len(self.tasks)}")
        print("=" * 60)
        
        # Initialize connections
        if not self.initialize_connections():
            print("\n❌ No LLM connections available. Aborting.")
            return
        
        # Execute tasks
        print(f"\n📋 Executing {len(self.tasks)} tasks...")
        
        results = []
        for task in self.tasks:
            result = self.execute_task(task)
            results.append({"task": task["id"], **result})
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 BUILD SUMMARY")
        print("=" * 60)
        print(f"   ✅ Completed: {self.tasks_completed}")
        print(f"   ❌ Failed: {self.tasks_failed}")
        print(f"   📂 Output: {OUTPUT_DIR}")
        print("=" * 60)
        
        return results


def main():
    """Main entry point"""
    builder = DesktopAppBuilder()
    builder.build()


if __name__ == "__main__":
    main()
