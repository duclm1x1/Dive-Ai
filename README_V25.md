# Dive AI V25 - Complete Edition

**Production-Ready Autonomous AI Platform with Continuous Voice Interaction and UI-TARS Integration**

[![GitHub](https://img.shields.io/badge/GitHub-duclm1x1%2FDive--Ai-blue)](https://github.com/duclm1x1/Dive-Ai)
[![Version](https://img.shields.io/badge/version-25.0-green)](https://github.com/duclm1x1/Dive-Ai)
[![Status](https://img.shields.io/badge/status-production--ready-success)](https://github.com/duclm1x1/Dive-Ai)

---

## 🎯 What's New in V25

### 🎤 Continuous Voice Interaction
- **Non-blocking voice conversation** during task execution
- **Wake word activation** ("Hey Dive")
- **Real-time feedback** via speech synthesis
- **Multi-threaded architecture** for parallel processing

### 🖥️ UI-TARS Desktop Integration
- **Natural language computer control**
- **A-Z automation** - commands execute automatically
- **Cross-platform support** (Windows/macOS/Linux)
- **Visual element detection** and interaction

### 🔄 Enhanced Architecture
```
Voice Input → Continuous Processing → Multi-threaded Orchestrator
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                            Task Execution      Voice Conversation
                                    ↓                   ↓
                            UI-TARS Control    Real-time Feedback
```

---

## ⚡ Key Features

### 🎤 Voice Control
- **Continuous listening** with wake word detection
- **Natural language commands** - "open Chrome and go to GitHub"
- **Conversational AI** - ask questions during task execution
- **Multiple STT/TTS providers** - Whisper, Google, pyttsx3, OpenAI

### 🖥️ Computer Automation
- **Application control** - open, close, switch apps
- **Browser automation** - navigate, search, interact
- **Mouse & keyboard** - precise control via natural language
- **Screenshot & vision** - see and understand screen content

### 🧠 AI Intelligence
- **Memory Loop Architecture** - continuous learning
- **128 Specialized Agents** - 1,968 capabilities
- **Multi-Provider LLM** - OpenAI, Anthropic, V98, AICoding
- **Context-aware** - remembers past interactions

### 🔐 Security & Privacy
- **Local processing** - optional local Whisper model
- **Command confirmation** - for sensitive actions
- **Audit logging** - full history in Dive Memory
- **Voice authentication** - optional biometric verification

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai
```

### 2. Install Voice + UI-TARS

```bash
./install_voice_uitars.sh
```

This installs:
- ✅ Python voice processing (SpeechRecognition, pyttsx3, PyAudio)
- ✅ UI automation (PyAutoGUI, pynput)
- ✅ UI-TARS Desktop (from ByteDance)
- ✅ All system dependencies

### 3. Configure

Edit `.env`:

```bash
# OpenAI API Key (for Whisper STT)
OPENAI_API_KEY=sk-your-key-here

# V98 API (alternative LLM provider)
V98_API_KEY=YOUR_V98_API_KEY_HERE
V98_BASE_URL=https://v98store.com/v1

# Voice settings
VOICE_STT_PROVIDER=google     # or whisper
VOICE_TTS_PROVIDER=pyttsx3    # or openai
VOICE_WAKE_WORD=hey dive
```

### 4. Launch

```bash
./start_voice_control.sh
```

### 5. Use

1. **Activate**: Say "**hey dive**"
2. **Command**: "open Chrome and go to GitHub"
3. **Converse**: "How's the progress?" (while task runs)

---

## 📋 Example Commands

### Basic Commands
```
"Hey Dive, open Chrome"
"Hey Dive, go to GitHub"
"Hey Dive, search for UI-TARS"
"Hey Dive, take a screenshot"
```

### Complex Workflows
```
"Hey Dive, open VS Code and create a new Python file"
"Hey Dive, search for weather in Hanoi and save the results"
"Hey Dive, open my GitHub repository and check the latest issues"
```

### Continuous Conversation
```
User: "Hey Dive, install the project dependencies"
AI: "Starting installation..." [npm install runs]
User: "How long will this take?"
AI: "About 2-3 minutes. I'm at 30% now."
[Installation continues...]
AI: "Installation complete! All dependencies ready."
```

---

## 🏗️ Architecture

### Multi-threaded Voice Control

```python
class DiveVoiceOrchestrator:
    def __init__(self):
        # Thread 1: Continuous voice listening
        self.voice_thread = Thread(target=self.voice_handler)
        
        # Thread 2: Task execution (UI-TARS)
        self.task_thread = Thread(target=self.task_handler)
        
        # Thread 3: Real-time feedback
        self.feedback_thread = Thread(target=self.feedback_handler)
        
        # Shared queue for commands
        self.command_queue = Queue()
```

### Voice Processing Flow

```
Microphone → STT → Wake Word Detection → Intent Classification
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                              Command              Conversation
                                    ↓                   ↓
                            Task Queue          Generate Response
                                    ↓                   ↓
                            UI-TARS Execute      TTS Output
```

---

## 📊 Performance Benchmarks

| Metric | V20.2.1 | V25.0 | Improvement |
|--------|---------|-------|-------------|
| Memory Add (2K) | 242/sec | 300/sec | **24% faster** |
| Voice Latency | N/A | 1-2s | **New** |
| Task Execution | Manual | Voice | **Hands-free** |
| Concurrent Operations | 1 | 3+ | **3x parallel** |

---

## 🔧 Components

### Core Modules

1. **`dive_voice_continuous.py`** - Continuous voice processing
   - Wake word detection
   - Non-blocking STT/TTS
   - Multi-threaded audio handling

2. **`dive_uitars_client.py`** - UI-TARS integration
   - Natural language → computer actions
   - Application control
   - Browser automation

3. **`dive_voice_orchestrator.py`** - Main coordinator
   - Multi-threaded task management
   - Real-time feedback
   - Context management

### Supporting Systems

- **Dive Memory** - Persistent context and learning
- **Dive Orchestrator** - Agent coordination
- **Dive Coder** - Code generation and execution
- **Claims Ledger** - Verification and trust

---

## 📚 Documentation

### Quick Links

- 📖 [Voice + UI-TARS README](docs/VOICE_UITARS_README.md)
- 🏗️ [Architecture Documentation](docs/CONTINUOUS_VOICE_UITARS_ARCHITECTURE.md)
- 🔧 [Installation Guide](docs/INSTALLATION.md)
- 🐛 [Troubleshooting](docs/TROUBLESHOOTING.md)

### API Reference

- [Voice Processor API](docs/api/voice_processor.md)
- [UI-TARS Client API](docs/api/uitars_client.md)
- [Orchestrator API](docs/api/orchestrator.md)

---

## 🎯 Use Cases

### 1. Hands-free Development
```
"Hey Dive, open VS Code"
"Create a new Python file called main.py"
"Write a function to calculate fibonacci"
"Run the file"
```

### 2. Research & Documentation
```
"Hey Dive, search for UI-TARS documentation"
"Open the GitHub repository"
"Check the latest issues"
"Take a screenshot of the README"
```

### 3. System Administration
```
"Hey Dive, check system status"
"Open terminal and show disk usage"
"Install the latest updates"
"Restart the service"
```

### 4. Productivity Automation
```
"Hey Dive, open my email"
"Check for messages from GitHub"
"Reply with: Thanks for the update"
"Schedule a meeting for tomorrow"
```

---

## 🔐 Security Features

### Voice Authentication (Optional)
- Biometric voice verification
- User-specific voice profiles
- Multi-factor authentication

### Command Confirmation
Automatic confirmation required for:
- File deletion
- System changes
- Financial transactions
- Sensitive data access

### Privacy Protection
- **Local processing** - No data sent to cloud (optional)
- **Encrypted storage** - All logs encrypted
- **Audit trail** - Complete history in Dive Memory
- **Selective logging** - Control what gets recorded

---

## 🌍 Multi-language Support

### Currently Supported
- 🇺🇸 English (en-US)
- 🇻🇳 Vietnamese (vi-VN) - Coming soon
- 🇨🇳 Chinese (zh-CN) - Coming soon

### Configuration
```bash
# In .env
VOICE_LANGUAGE=vi-VN
VOICE_WAKE_WORD=xin chào dive
```

---

## 🐛 Troubleshooting

### Voice Recognition Not Working

```bash
# Check microphone
arecord -l  # Linux
system_profiler SPAudioDataType  # macOS

# Test PyAudio
python3 -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count())"

# Reinstall
sudo apt-get install python3-pyaudio portaudio19-dev
sudo pip3 install --upgrade SpeechRecognition pyaudio
```

### UI-TARS Connection Failed

```bash
# Check if running
curl http://localhost:8080/health

# Start manually
cd ~/UI-TARS-desktop
pnpm run dev
```

### Permission Errors

```bash
# Linux: Grant accessibility permissions
# macOS: System Preferences > Security & Privacy > Accessibility
```

---

## 🚧 Roadmap

### V25.1 (Next)
- [ ] Full UI-TARS vision model integration
- [ ] Vietnamese language support
- [ ] Custom wake word training
- [ ] Mobile app for remote control

### V25.2 (Future)
- [ ] Emotion detection from voice
- [ ] Proactive assistance
- [ ] Multi-user collaboration
- [ ] Advanced gesture control

### V26.0 (Long-term)
- [ ] Multi-modal AI (voice + vision + gesture)
- [ ] Autonomous task planning
- [ ] Self-improvement through reinforcement learning
- [ ] Distributed multi-agent system

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:

1. **Voice Processing** - Better STT/TTS engines
2. **UI-TARS Integration** - Full vision model support
3. **Multi-language** - Add more languages
4. **Performance** - Optimize latency
5. **Documentation** - Improve guides and examples

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- **UI-TARS** by ByteDance - Desktop automation framework
- **OpenAI Whisper** - Speech recognition
- **pyttsx3** - Text-to-speech
- **PyAutoGUI** - UI automation
- **Dive AI Community** - Continuous feedback and support

---

## 📞 Support

- 📧 Email: support@dive-ai.com
- 💬 Discord: [Join our community](https://discord.gg/dive-ai)
- 🐛 Issues: [GitHub Issues](https://github.com/duclm1x1/Dive-Ai/issues)
- 📖 Docs: [Documentation](https://docs.dive-ai.com)

---

## 🌟 Star History

If you find DIVE AI useful, please give us a star ⭐ on GitHub!

---

**Built with ❤️ by the Dive AI Team**

**Happy voice controlling! 🎤🤖**
