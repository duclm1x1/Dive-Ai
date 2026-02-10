# Dive AI V29.4 Desktop

AI-powered desktop app with **15 LLM connections** and desktop automation.

## 🦞 Features

- **AI Chat** - Claude 4.6, GPT-4, with automatic failover
- **Monaco Code Editor** - AI-assisted coding
- **Terminal** - Command execution
- **Desktop Automation** - UI-TARS integration
- **Browser Automation** - Web scraping

## 🔌 15 LLM Connections

| # | Provider | Model | Priority |
|---|----------|-------|----------|
| 1 | V98 | Claude 4.6 Opus Thinking 🧠 | 10 |
| 2 | V98 | Claude Sonnet 4.5 | 8 |
| 3 | V98 | Claude Haiku 3.5 | 6 |
| 4 | AICoding | Claude Opus 4.6 | 9 |
| 5 | AICoding | Claude Sonnet | 7 |
| 6 | AICoding | GPT-4 Turbo | 7 |
| 7 | OpenAI | GPT-4 Turbo 👁️ | 8 |
| 8 | OpenAI | GPT-4o 👁️ | 9 |
| 9 | OpenAI | o1 Preview 🧠 | 10 |
| 10 | Anthropic | Claude 3.5 Sonnet 👁️ | 9 |
| 11 | Anthropic | Claude 3 Opus | 8 |
| 12 | Anthropic | Claude 3.5 Haiku | 6 |
| 13 | Groq | LLaMA 3.1 70B | 5 |
| 14 | Together | Mixtral 8x22B | 4 |
| 15 | Ollama | LLaMA 3.1 (Local) | 1 |

🧠 = Thinking/Reasoning, 👁️ = Vision

## 🚀 Quick Start

### 1. Set API Keys

```powershell
# Windows
set V98_API_KEY=your_key
set AICODING_API_KEY=sk-dev-xxx
set OPENAI_API_KEY=sk-xxx
set ANTHROPIC_API_KEY=sk-ant-xxx
```

### 2. Start Backend

```bash
cd backend
pip install -r requirements.txt
python gateway_server.py
```

### 3. Start Desktop App

```bash
npm install
npm run dev
```

## 📁 Structure

```
desktop-app/
├── electron/           # Main + Preload
├── src/               # React App
│   ├── components/    # AIChat, Terminal, CodeEditor...
│   └── App.tsx
├── backend/           # FastAPI Gateway
│   ├── llm/          # 15 LLM Connections
│   └── gateway_server.py
└── package.json
```

## 🔧 API Endpoints

- `GET /health` - Server status + LLM availability
- `GET /connections` - List all 15 connections
- `POST /chat` - Chat with auto-failover
- `POST /chat/{connection_id}` - Chat with specific LLM
- `GET /automation/screenshot` - Capture screen
- `POST /automation/execute` - Click/Type/Keypress
- `POST /terminal/execute` - Run commands

## License

MIT
