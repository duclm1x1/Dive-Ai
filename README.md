# Dive AI V29.4

🦞 **Complete AI-Powered Coding Assistant with Desktop & Web IDEs**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ Features

- 🤖 **AI Algorithm Selection** - Intelligently chooses the best algorithm for each task
- 🧬 **Self-Evolving System** - Automatically generates and optimizes algorithms
- 🖥️ **Desktop IDE** - Native PyQt6 application with full features
- 🌐 **Web IDE** - Beautiful browser-based interface (Monaco editor)
- 📊 **Database Integration** - Persistent chat history and analytics
- 🔌 **Multi-Channel Support** - Discord, Telegram, Zalo desktop integration
- ⚡ **Real-time Chat** - WebSocket support for instant responses
- 📝 **Code Editor** - Syntax highlighting and intelligent completion

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:

```env
V98_API_KEY=your_v98_api_key_here
AICODING_API_KEY=your_aicoding_key_here
DATABASE_URL=sqlite:///./dive_ai.db
```

### 3. Run Gateway Server

```bash
python gateway/gateway_server.py
```

The Gateway will start on `http://localhost:1879`

### 4. Access Interfaces

- **Web IDE**: Open <http://localhost:1879> in your browser
- **Desktop IDE**: Run `python desktop_ide.py`
- **API Documentation**: <http://localhost:1879/docs>
- **System Tray**: Run `python diveai_tray.py` for background service

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Multi-Channel Gateway              │
│  (Web, Desktop, Discord, Telegram, Zalo)    │
└────────────────┬────────────────────────────┘
                 │
         ┌───────▼────────┐
         │  Gateway Server │
         │  (Port 1879)    │
         └───────┬────────┘
                 │
    ┌────────────┴──────────────┐
    │                           │
┌───▼──────────┐    ┌──────────▼────────┐
│ AI Algorithm  │    │  AlgorithmManager│
│   Selector    │───►│   (50+ algos)    │
└──────────────┘    └──────────┬────────┘
                                │
                    ┌───────────▼──────────┐
                    │  Database Storage    │
                    │  (Chat + Analytics)  │
                    └──────────────────────┘
```

---

## 📦 Project Structure

```
Dive-AI2/
├── gateway/
│   └── gateway_server.py          # Main FastAPI server
├── core/
│   ├── algorithms/                # 50+ built-in algorithms
│   ├── ai_algorithm_selector.py   # AI-powered selection
│   └── self_evolving_algorithms.py# Auto-generation system
├── channels/
│   ├── discord_desktop_channel.py # Discord integration
│   ├── telegram_desktop_channel.py# Telegram integration
│   └── zalo_desktop_channel.py    # Zalo integration
├── database/
│   ├── config.py                  # Database setup
│   └── models.py                  # SQLAlchemy models
├── web_ide/
│   └── index.html                 # Web IDE interface
├── desktop_ide.py                 # PyQt6 desktop app
├── diveai_tray.py                # System tray app
├── first_run_setup.py            # Setup wizard
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

---

## 🔌 API Endpoints

### Chat

```bash
POST /chat
{
  "message": "Create a Python REST API",
  "channel": "web",
  "user_id": "user_123"
}
```

### Health Check

```bash
GET /health
```

### Statistics

```bash
GET /statistics
```

### List Algorithms

```bash
GET /algorithms
```

### WebSocket

```bash
WS /ws/{session_id}
```

---

## 💾 Database

Dive AI uses SQLAlchemy with support for:

- **SQLite** (default, no setup required)
- **PostgreSQL** (for production)

### Database Models

- `ChatSession` - User chat sessions
- `ChatMessage` - Individual messages
- `AlgorithmExecution` - Execution logs
- `GeneratedAlgorithm` - Self-evolved algorithms

### Connect to PostgreSQL

```env
DATABASE_URL=postgresql://user:password@localhost:5432/diveai
```

---

## 🖥️ Desktop Applications

### Web IDE (Browser)

Open <http://localhost:1879> for:

- AI Chat interface
- Monaco code editor
- Integrated terminal
- File management

### Desktop IDE (Native)

Run `python desktop_ide.py` for:

- Standalone application
- Embedded web view
- Native file operations
- System integration

### System Tray

Run `python diveai_tray.py` for:

- Background service
- Quick start/stop
- Status monitoring
- Settings access

---

## 🧬 Self-Evolving System

The AI can:

1. **Detect capability gaps** - Identifies missing algorithms
2. **Generate new algorithms** - Creates Python code automatically
3. **Optimize existing code** - Improves performance based on metrics
4. **Learn from results** - Adapts selection based on success rates

### View Evolution Status

```bash
curl http://localhost:1879/evolution/status
```

---

## 🎨 Desktop Channels

Control desktop messaging apps via UI automation:

### Discord Desktop

- Auto-login and channel monitoring
- Send/receive messages
- React to messages

### Telegram Desktop

- Full Vietnamese support
- Group chat integration
- Media handling

### Zalo PC

- Native Vietnamese app
- No API needed
- Full feature access

Configure in `config/channels.json`

---

## 🧪 Development

### Run Demo

```bash
python demo.py
```

### Run Tests

```bash
pytest test_complete_system.py
```

### Build Desktop App

```bash
python build.bat
```

Creates:

- `DiveAI-Tray.exe` - System tray app
- `DiveAI-Setup-Wizard.exe` - First-run setup
- `dist/DiveAI/` - Complete distribution

---

## 📊 System Requirements

- **OS**: Windows 10/11, macOS, Linux
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB free space
- **Network**: Internet connection for AI APIs

---

## 🔧 Configuration

### Environment Variables

```env
# LLM API Keys
V98_API_KEY=your_key_here
AICODING_API_KEY=your_key_here

# Gateway Settings
GATEWAY_PORT=1879
GATEWAY_HOST=127.0.0.1

# Database
DATABASE_URL=sqlite:///./dive_ai.db

# Desktop Channels (optional)
DISCORD_PATH=C:\Users\...\Discord\Discord.exe
TELEGRAM_PATH=C:\Users\...\Telegram Desktop\Telegram.exe
ZALO_PATH=C:\Users\...\Zalo\Zalo.exe

# Self-Evolution
AUTO_OPTIMIZE_ENABLED=true
AUTO_OPTIMIZE_THRESHOLD=50
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **Issues**: <https://github.com/duclm1x1/Dive-AI2/issues>
- **Discussions**: <https://github.com/duclm1x1/Dive-AI2/discussions>

---

## 🎯 Roadmap

- [ ] VSCode extension
- [ ] Cloud deployment support
- [ ] Multi-user collaboration
- [ ] Plugin system
- [ ] Mobile companion app

---

**Made with 🧬 by Dive AI Self-Evolving System**  
**Version 29.4 - The Future of Agentic AI**

---

## ⭐ Star History

[![Stargazers over time](https://starchart.cc/duclm1x1/Dive-AI2.svg)](https://starchart.cc/duclm1x1/Dive-AI2)
