"""
Dive AI V29.4 Desktop App Builder - Standalone Version
Uses V98 and AICoding APIs directly to generate code

Run: python build_desktop_app_v2.py
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime

# Configuration
V98_API_KEY = os.getenv("V98_API_KEY", "")
AICODING_API_KEY = os.getenv("AICODING_API_KEY", "YOUR_AICODING_API_KEY_HERECJCk")  # Fallback from project

V98_BASE_URL = "https://v98store.com/v1"
AICODING_BASE_URL = "https://api.aicoding.world/v1"


OUTPUT_DIR = Path(r"D:\Antigravity\Dive AI\desktop-app")


def call_llm(provider: str, prompt: str, system: str = None) -> str:
    """Call LLM API (V98 or AICoding)"""
    
    if provider == "v98":
        url = f"{V98_BASE_URL}/chat/completions"
        api_key = V98_API_KEY
        model = "claude-sonnet-4-20250514"
    else:  # aicoding
        url = f"{AICODING_BASE_URL}/chat/completions"
        api_key = AICODING_API_KEY
        model = "claude-opus-4.6"
    
    if not api_key:
        raise ValueError(f"{provider.upper()}_API_KEY not set")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 8192
    }
    
    print(f"   🔌 Calling {provider.upper()} ({model})...")
    start = time.time()
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    
    latency = (time.time() - start) * 1000
    print(f"   ⏱️ {latency:.0f}ms, {len(content)} chars")
    
    return content


def extract_code(response: str, lang: str) -> str:
    """Extract code block from response"""
    import re
    
    # Try language-specific blocks
    patterns = [
        rf'```{lang}\n(.*?)```',
        rf'```{lang[:2]}\n(.*?)```',  # e.g. ts, py
        r'```typescript\n(.*?)```',
        r'```python\n(.*?)```',
        r'```tsx\n(.*?)```',
        r'```\n(.*?)```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return response.strip()


def build_task(task: dict, fallback_provider: str = "v98") -> bool:
    """Execute a single build task"""
    
    provider = task.get("provider", "v98")
    
    # Check if API key available, fallback if not
    if provider == "v98" and not V98_API_KEY:
        if AICODING_API_KEY:
            provider = "aicoding"
            print(f"   ⚠️ V98 key missing, using AICoding")
        else:
            print(f"   ❌ No API keys available!")
            return False
    elif provider == "aicoding" and not AICODING_API_KEY:
        if V98_API_KEY:
            provider = "v98"
            print(f"   ⚠️ AICoding key missing, using V98")
        else:
            print(f"   ❌ No API keys available!")
            return False
    
    try:
        # Call LLM
        response = call_llm(
            provider=provider,
            prompt=task["prompt"],
            system=f"You are an expert {task['language']} developer. Generate production-ready code only. No explanations needed."
        )
        
        # Extract and save code
        if task.get("file"):
            code = extract_code(response, task["language"])
            
            file_path = OUTPUT_DIR / task["file"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            print(f"   ✅ Saved: {task['file']} ({len(code)} chars)")
            return True
        else:
            print(f"   📋 Review: {response[:200]}...")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


# ============================================================
# TASK DEFINITIONS
# ============================================================

TASKS = [
    # ==================== PHASE 1: ELECTRON ====================
    {
        "id": "1",
        "name": "Electron Main Process",
        "file": "electron/main.ts",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate electron/main.ts for Dive AI V29.4:

import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';

Requirements:
1. createWindow() - BrowserWindow 1400x900, dark bg #1a1a2e
2. Load localhost:5173 in dev, file path in production
3. IPC handlers:
   - 'gateway:request' - POST to http://127.0.0.1:1879
   - 'automation:screenshot' - GET screenshot endpoint
   - 'automation:execute' - POST automation action
   - 'terminal:execute' - POST terminal command
4. DevTools auto-open in development
5. app.whenReady() and window-all-closed handlers

Complete TypeScript code only."""
    },
    {
        "id": "2",
        "name": "Preload Bridge",
        "file": "electron/preload.ts",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate electron/preload.ts for Dive AI:

import { contextBridge, ipcRenderer } from 'electron';

Expose window.diveAPI with:
1. gateway: { request(endpoint, data), chat(message), health() }
2. automation: { screenshot(), execute(action, params) }
3. terminal: { execute(command, cwd) }
4. fs: { readFile(path), writeFile(path, content) }

All methods return Promise, use ipcRenderer.invoke().
Complete TypeScript code only."""
    },
    
    # ==================== PHASE 2: BACKEND ====================
    {
        "id": "3",
        "name": "Gateway Server",
        "file": "backend/gateway_server.py",
        "provider": "v98",
        "language": "python",
        "prompt": """Generate backend/gateway_server.py - FastAPI server:

Endpoints:
1. GET /health - return {"status": "ok", "llm": {"v98": true}}
2. POST /chat - {"message": str} -> call V98 API, return response
3. POST /chat/stream - streaming SSE response
4. GET /automation/screenshot - PIL ImageGrab, base64 PNG
5. POST /automation/execute - {"action": "click|type|keypress", "params": {...}}
6. POST /terminal/execute - {"command": str, "cwd": str}
7. POST /fs/read, POST /fs/write

Include:
- CORS middleware for localhost
- V98_API_KEY from env
- Error handling
- Uvicorn run on port 1879

Complete Python code only."""
    },
    {
        "id": "4",
        "name": "Requirements",
        "file": "backend/requirements.txt",
        "provider": "v98",
        "language": "text",
        "prompt": """Generate backend/requirements.txt:

fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.0.0
requests>=2.31.0
aiohttp>=3.9.0
python-multipart>=0.0.6
Pillow>=10.0.0
pyautogui>=0.9.54
sse-starlette>=1.8.0

Just the file content, no markdown."""
    },
    
    # ==================== PHASE 3: REACT APP ====================
    {
        "id": "5",
        "name": "Package.json",
        "file": "package.json",
        "provider": "v98",
        "language": "json",
        "prompt": """Generate package.json for Dive AI Desktop:

{
  "name": "dive-ai-desktop",
  "version": "29.4.0",
  "main": "dist/main/main.js",
  "scripts": {
    "dev": "electron-vite dev",
    "build": "electron-vite build",
    "preview": "electron-vite preview"
  },
  "dependencies": {
    "@monaco-editor/react": "^4.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "electron": "^28.0.0",
    "electron-vite": "^2.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}

Just JSON, no markdown."""
    },
    {
        "id": "6",
        "name": "App.tsx",
        "file": "src/App.tsx",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate src/App.tsx for Dive AI Desktop:

React app with:
1. Tabbed interface: 'chat' | 'browser' | 'code' | 'terminal' | 'desktop'
2. Sidebar with icon buttons
3. Gateway status indicator (connected/disconnected)
4. Import components: AIChat, BrowserView, CodeEditor, Terminal, DesktopController
5. CSS import from ./App.css

Use useState for activeTab and gatewayStatus.
Check gateway health on mount.
Modern dark theme styling inline or via CSS classes.

Complete TSX code only."""
    },
    {
        "id": "7",
        "name": "App.css",
        "file": "src/App.css",
        "provider": "v98",
        "language": "css",
        "prompt": """Generate src/App.css for Dive AI Desktop:

Dark theme with:
- --primary: #0f3460
- --secondary: #16213e
- --accent: #00d9ff
- --bg-dark: #1a1a2e
- --text: #e4e4e7
- --success: #10b981
- --error: #ef4444

Styles for:
1. .app - flex container, 100vh
2. .sidebar - 80px width, dark bg, column flex
3. .tab-btn - icon buttons with hover effects
4. .tab-btn.active - accent border
5. .content - flex 1, padding
6. .status-indicator - small circle with colors
7. .header - flex between

Modern, clean design. Complete CSS only."""
    },
    {
        "id": "8",
        "name": "main.tsx",
        "file": "src/main.tsx",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate src/main.tsx:

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

Just the code."""
    },
    {
        "id": "9",
        "name": "index.html",
        "file": "src/index.html",
        "provider": "v98",
        "language": "html",
        "prompt": """Generate src/index.html:

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'">
  <title>Dive AI V29.4</title>
  <style>
    body { margin: 0; background: #1a1a2e; color: white; font-family: system-ui; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="./main.tsx"></script>
</body>
</html>

Just the HTML."""
    },
    
    # ==================== PHASE 4: COMPONENTS ====================
    {
        "id": "10",
        "name": "AIChat Component",
        "file": "src/components/AIChat/AIChat.tsx",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate src/components/AIChat/AIChat.tsx:

React component with:
1. messages state: {role: 'user'|'assistant', content: string}[]
2. input state for user message
3. loading state
4. sendMessage() - call window.diveAPI.gateway.chat()
5. Message list with scroll to bottom
6. Input with send button
7. Welcome message when empty
8. Typing indicator when loading

Import CSS from ./AIChat.css
Complete TSX with proper types."""
    },
    {
        "id": "11",
        "name": "AIChat CSS",
        "file": "src/components/AIChat/AIChat.css",
        "provider": "v98",
        "language": "css",
        "prompt": """Generate src/components/AIChat/AIChat.css:

Styles for chat component:
- .chat-container - full height flex column
- .messages - flex 1, overflow scroll
- .message - padding, margin, border-radius
- .message.user - align right, accent bg
- .message.assistant - align left, dark bg
- .input-area - flex row, gap
- .input - flex 1, dark bg, white text
- .send-btn - accent bg, hover effect
- .typing-indicator - animated dots
- .welcome - centered, muted text

Dark theme. Complete CSS only."""
    },
    {
        "id": "12",
        "name": "Terminal Component",
        "file": "src/components/Terminal/Terminal.tsx",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate src/components/Terminal/Terminal.tsx:

React component with:
1. history state: {type: 'input'|'output'|'error', content: string}[]
2. command state for current input
3. cwd state (current directory)
4. handleCommand() - process input
5. Built-in 'clear' and 'cd' commands
6. Call window.diveAPI.terminal.execute() for other commands
7. Arrow up for history
8. Monospace font, dark bg

Import CSS from ./Terminal.css
Complete TSX."""
    },
    {
        "id": "13",
        "name": "Terminal CSS",
        "file": "src/components/Terminal/Terminal.css",
        "provider": "v98",
        "language": "css",
        "prompt": """Generate Terminal.css:

Styles:
- .terminal - full height, black bg, monospace font
- .output - flex 1, overflow scroll
- .line - white-space pre-wrap
- .line.input - color #00d9ff
- .line.output - color #e4e4e7
- .line.error - color #ef4444
- .prompt - flex row
- .prompt-symbol - color #10b981
- .prompt-cwd - color #00d9ff
- .input - flex 1, transparent bg, white text, no outline

Complete CSS only."""
    },
    {
        "id": "14",
        "name": "CodeEditor Component",
        "file": "src/components/CodeEditor/CodeEditor.tsx",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate CodeEditor.tsx with Monaco:

import Editor from '@monaco-editor/react';

Component with:
1. code state for editor content
2. language state selector
3. filePath state
4. aiOutput state for AI responses
5. Monaco Editor with dark theme
6. Toolbar: language select, file path input, Open/Save buttons
7. AI panel with quick prompts: Explain, Fix Bugs, Optimize
8. askAI() - call gateway.chat with code context

Dark theme. Complete TSX."""
    },
    {
        "id": "15",
        "name": "CodeEditor CSS",
        "file": "src/components/CodeEditor/CodeEditor.css",
        "provider": "v98",
        "language": "css",
        "prompt": """Generate CodeEditor.css:

- .editor-container - flex row, full height
- .editor-main - flex 3
- .ai-panel - flex 1, dark bg, padding
- .toolbar - flex row, gap, padding
- .select, .input - dark bg, white text
- .btn - padding, border-radius
- .btn-primary - accent bg
- .quick-prompts - flex row, gap
- .ai-output - bg darker, padding, overflow auto

Complete CSS."""
    },
    {
        "id": "16",
        "name": "Desktop Controller",
        "file": "src/components/Desktop/DesktopController.tsx",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate DesktopController.tsx:

Component with:
1. screenshot state (base64 image)
2. instruction state for natural language
3. result state for action results
4. captureScreen() - call automation.screenshot()
5. executeInstruction() - call gateway.request('/automation/ui-tars')
6. Quick actions: Screenshot, Click, Type
7. Screenshot preview area
8. Instruction input + Execute button
9. Result display

Import CSS. Complete TSX."""
    },
    {
        "id": "17",
        "name": "Desktop CSS",
        "file": "src/components/Desktop/DesktopController.css",
        "provider": "v98",
        "language": "css",
        "prompt": """Generate DesktopController.css:

- .desktop-controller - grid layout
- .preview-area - bg darker, border
- .screenshot - max-width 100%
- .controls - flex column, gap
- .instruction-input - full width
- .quick-actions - flex row, gap
- .action-btn - padding, icon
- .result - bg darker, padding

Complete CSS."""
    },
    {
        "id": "18",
        "name": "Browser View",
        "file": "src/components/Browser/BrowserView.tsx",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate BrowserView.tsx:

Component with:
1. url state
2. instruction state for AI automation
3. result state
4. URL bar with go button
5. iframe for web content (or placeholder)
6. Automation panel with instruction input
7. Quick actions: Scrape, Click Element, Fill Form

Import CSS. Complete TSX."""
    },
    {
        "id": "19",
        "name": "Browser CSS",
        "file": "src/components/Browser/BrowserView.css",
        "provider": "v98",
        "language": "css",
        "prompt": """Generate BrowserView.css:

- .browser-view - flex column, full height
- .url-bar - flex row, padding
- .url-input - flex 1
- .go-btn - padding
- .browser-frame - flex 1, bg white
- .automation-panel - padding
- .action-btns - flex row, gap

Complete CSS."""
    },
    
    # ==================== PHASE 5: CONFIG ====================
    {
        "id": "20",
        "name": "Vite Config",
        "file": "electron-vite.config.ts",
        "provider": "v98",
        "language": "typescript",
        "prompt": """Generate electron-vite.config.ts:

import { defineConfig } from 'electron-vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  main: {
    build: { outDir: 'dist/main' }
  },
  preload: {
    build: { outDir: 'dist/preload' }
  },
  renderer: {
    root: 'src',
    build: { outDir: '../dist/renderer' },
    plugins: [react()],
    resolve: {
      alias: { '@': resolve(__dirname, 'src') }
    }
  }
});

Just the code."""
    },
    {
        "id": "21",
        "name": "TypeScript Config",
        "file": "tsconfig.json",
        "provider": "v98",
        "language": "json",
        "prompt": """Generate tsconfig.json:

{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["src/**/*", "electron/**/*"]
}

Just JSON."""
    },
    
    # ==================== PHASE 6: README ====================
    {
        "id": "22",
        "name": "README",
        "file": "README.md",
        "provider": "aicoding",
        "language": "markdown",
        "prompt": """Generate README.md for Dive AI V29.4 Desktop:

# Dive AI V29.4 Desktop

AI-powered desktop app with chat, code editor, terminal, browser, and desktop automation.

## Features
- AI Chat (V98/AICoding Claude 4.6)
- Monaco Code Editor with AI assist
- Terminal emulator
- Desktop automation (UI-TARS)
- Browser automation

## Quick Start
1. Set API keys: V98_API_KEY, AICODING_API_KEY
2. Start backend: cd backend && pip install -r requirements.txt && python gateway_server.py
3. Start app: npm install && npm run dev

## Architecture
Electron + React + FastAPI + V98/AICoding APIs

## License
MIT

Keep it short and clear."""
    }
]


def main():
    """Main build process"""
    print("=" * 70)
    print("🦞 DIVE AI V29.4 DESKTOP APP BUILDER")
    print("=" * 70)
    print(f"   📂 Output: {OUTPUT_DIR}")
    print(f"   📋 Tasks: {len(TASKS)}")
    print(f"   🔑 V98: {'✅' if V98_API_KEY else '❌ Missing'}")
    print(f"   🔑 AICoding: {'✅' if AICODING_API_KEY else '❌ Missing'}")
    print("=" * 70)
    
    if not V98_API_KEY and not AICODING_API_KEY:
        print("\n❌ No API keys available! Set V98_API_KEY or AICODING_API_KEY")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Execute tasks
    success = 0
    failed = 0
    
    for task in TASKS:
        print(f"\n[{task['id']}/{len(TASKS)}] {task['name']}")
        
        if build_task(task):
            success += 1
        else:
            failed += 1
            # Try with backup provider
            if task["provider"] == "v98" and AICODING_API_KEY:
                print("   🔄 Retrying with AICoding...")
                task["provider"] = "aicoding"
                if build_task(task):
                    success += 1
                    failed -= 1
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 BUILD COMPLETE")
    print("=" * 70)
    print(f"   ✅ Success: {success}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📂 Output: {OUTPUT_DIR}")
    print("\n🚀 Next steps:")
    print("   1. cd desktop-app/backend && pip install -r requirements.txt")
    print("   2. python gateway_server.py")
    print("   3. cd desktop-app && npm install && npm run dev")
    print("=" * 70)


if __name__ == "__main__":
    main()
