# Dive AI V25 - Voice-Controlled Computer Automation with UI-TARS

## 🎤 Overview

This integration combines **DIVE AI V25** with **UI-TARS Desktop** to create a voice-controlled computer automation system with **continuous, non-blocking voice interaction**.

### Key Features

✅ **Continuous Voice Conversation** - AI maintains ongoing dialogue while executing tasks  
✅ **Non-Blocking Execution** - Voice input/output continues during automation  
✅ **Natural Language Control** - Control computer through conversational commands  
✅ **A-Z Automation** - Commands execute automatically from start to finish  
✅ **Real-time Feedback** - Continuous audio updates during task execution  
✅ **Multi-threaded Architecture** - Separate threads for voice, tasks, and UI control  

---

## 🚀 Quick Start

### 1. Installation

```bash
cd DIVE_AI_V25_TRULY_COMPLETE
./install_voice_uitars.sh
```

This will install:
- Python voice processing libraries (SpeechRecognition, pyttsx3, PyAudio)
- UI automation libraries (PyAutoGUI, pynput)
- UI-TARS Desktop (cloned from GitHub)
- All system dependencies

### 2. Configuration

Edit `.env` file:

```bash
# Add your OpenAI API key (for Whisper STT)
OPENAI_API_KEY=sk-your-key-here

# Voice settings
VOICE_STT_PROVIDER=google     # or whisper
VOICE_TTS_PROVIDER=pyttsx3    # or openai
VOICE_WAKE_WORD=hey dive
VOICE_LANGUAGE=en-US

# UI-TARS settings
UITARS_PATH=/home/ubuntu/UI-TARS-desktop
UITARS_API_URL=http://localhost:8080
```

### 3. Launch

```bash
./start_voice_control.sh
```

Or with custom settings:

```bash
./start_voice_control.sh --stt whisper --tts openai --wake-word "hey dive"
```

### 4. Usage

1. **Activate**: Say "**hey dive**" to wake up the AI
2. **Command**: Give natural language commands
3. **Converse**: Ask questions or chat while tasks execute

---

## 📋 Example Commands

### Opening Applications
```
"Hey Dive, open Chrome"
"Hey Dive, launch VS Code"
"Hey Dive, start Terminal"
```

### Web Navigation
```
"Hey Dive, go to GitHub"
"Hey Dive, navigate to google.com"
"Hey Dive, open YouTube"
```

### Search
```
"Hey Dive, search for UI-TARS documentation"
"Hey Dive, find Python tutorials"
```

### Complex Tasks
```
"Hey Dive, open Chrome and go to my GitHub repository"
"Hey Dive, search for weather in Hanoi and take a screenshot"
```

### Conversation During Tasks
```
User: "Hey Dive, install the project dependencies"
AI: "Starting installation..." [npm install runs]
User: "How long will this take?"
AI: "About 2-3 minutes. I'm at 30% now."
[Installation continues in background]
AI: "Installation complete!"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Voice Input  │  │ Voice Output │  │ Visual Feed  │          │
│  │  (STT)       │  │  (TTS)       │  │   back       │          │
│  └──────┬───────┘  └──────▲───────┘  └──────▲───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
┌─────────▼──────────────────┼──────────────────┼─────────────────┐
│              Voice Processing Layer (Continuous)                 │
│  • Real-time speech recognition                                  │
│  • Wake word detection                                           │
│  • Streaming TTS output                                          │
│  • Non-blocking audio playback                                   │
└─────────┬──────────────────▲──────────────────▲─────────────────┘
          │                  │                  │
┌─────────▼──────────────────┼──────────────────┼─────────────────┐
│           DIVE AI Orchestration Layer                            │
│  • Thread 1: Voice conversation handler                          │
│  • Thread 2: Task execution handler                              │
│  • Thread 3: UI-TARS control handler                             │
│  • Shared queue for command passing                              │
└─────────┬──────────────────▲──────────────────▲─────────────────┘
          │                  │                  │
┌─────────▼──────────────────┼──────────────────┼─────────────────┐
│              UI-TARS Integration Layer                           │
│  • Screenshot capture & analysis                                 │
│  • Mouse/keyboard control                                        │
│  • Application automation                                        │
│  • Browser automation                                            │
└─────────┬──────────────────▲──────────────────────────────────────┘
          │                  │
┌─────────▼──────────────────┴─────────────────────────────────────┐
│                    Operating System Layer                         │
│  • Windows/macOS/Linux automation                                │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Components

### 1. Voice Processing (`dive_voice_continuous.py`)

**ContinuousVoiceProcessor**
- Continuous speech recognition (Whisper/Google/Sphinx)
- Wake word detection
- Non-blocking TTS (pyttsx3/OpenAI)
- Multi-threaded audio processing

**VoiceCommandParser**
- Natural language command parsing
- Intent classification (command vs. conversation)
- LLM-based or rule-based parsing

### 2. UI-TARS Integration (`dive_uitars_client.py`)

**UITARSClient**
- Computer control automation
- Application launching
- Browser navigation
- Mouse/keyboard control
- Screenshot capture

**UITARSVisionClient** (Extended)
- Visual element detection
- Screen understanding
- Click-by-description

### 3. Orchestrator (`dive_voice_orchestrator.py`)

**DiveVoiceOrchestrator**
- Multi-threaded coordination
- Task queue management
- Real-time feedback
- Conversation context management
- Session persistence

---

## 🎯 Technical Details

### Multi-threaded Architecture

```python
class DiveVoiceOrchestrator:
    def __init__(self):
        # Thread 1: Continuous voice listening
        self.voice_thread = Thread(target=self.voice_handler)
        
        # Thread 2: Task execution
        self.task_thread = Thread(target=self.task_handler)
        
        # Thread 3: UI-TARS control
        self.uitars_thread = Thread(target=self.uitars_handler)
        
        # Shared queue for inter-thread communication
        self.shared_queue = Queue()
```

### Non-Blocking Voice Processing

```python
# Voice input continues during task execution
def voice_handler(self):
    while self.conversation_active:
        audio = self.listen()
        text = self.stt(audio)
        
        if self.is_command(text):
            self.task_queue.put(text)
        else:
            response = self.generate_response(text)
            self.tts_stream(response)  # Non-blocking

# Tasks execute in parallel
def task_handler(self):
    while True:
        task = self.task_queue.get()
        self.execute_task(task)
        self.tts_stream(f"Completed: {task}")  # Real-time feedback
```

---

## 🔐 Security & Privacy

### Voice Authentication (Optional)
- Voice biometric authentication
- User verification before sensitive actions

### Command Confirmation
- Require confirmation for:
  - File deletion
  - System changes
  - Financial transactions

### Local Processing
- All voice processing can be done locally
- Use local Whisper model (no API calls)
- No data sent to external servers

### Audit Logging
- All commands logged to Dive Memory
- Full audit trail of actions
- Session replay capability

---

## 📊 Performance

### Latency
- **Wake word detection**: < 500ms
- **Speech recognition**: 1-2 seconds
- **Command execution**: Varies by task
- **TTS response**: < 1 second (streaming)

### Resource Usage
- **CPU**: 10-20% (voice processing)
- **Memory**: ~500MB
- **Disk**: Minimal (logs only)

### Optimization Tips
1. Use local Whisper model for faster STT
2. Enable GPU acceleration for Whisper
3. Use streaming TTS for lower latency
4. Cache common UI-TARS action sequences

---

## 🐛 Troubleshooting

### Voice Recognition Issues

**Problem**: "Speech recognition not working"

**Solutions**:
```bash
# Check microphone
arecord -l  # Linux
# or
system_profiler SPAudioDataType  # macOS

# Test PyAudio
python3 -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count())"

# Reinstall dependencies
sudo apt-get install python3-pyaudio portaudio19-dev
sudo pip3 install --upgrade SpeechRecognition pyaudio
```

### TTS Not Working

**Problem**: "Text-to-speech not speaking"

**Solutions**:
```bash
# Test pyttsx3
python3 -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"

# Install espeak (Linux)
sudo apt-get install espeak

# Check audio output
speaker-test -t wav -c 2
```

### UI-TARS Connection Failed

**Problem**: "Cannot connect to UI-TARS"

**Solutions**:
```bash
# Check if UI-TARS is running
curl http://localhost:8080/health

# Start UI-TARS manually
cd ~/UI-TARS-desktop
pnpm run dev

# Check port availability
netstat -tuln | grep 8080
```

### Permission Errors

**Problem**: "Permission denied for automation"

**Solutions**:
```bash
# Linux: Grant accessibility permissions
# macOS: System Preferences > Security & Privacy > Accessibility

# Test PyAutoGUI
python3 -c "import pyautogui; pyautogui.moveTo(100, 100)"
```

---

## 🔄 Integration with Dive Memory

### Automatic Logging

All voice interactions and commands are automatically logged to Dive Memory:

```python
# Voice commands stored
{
    "timestamp": "2026-02-05T18:30:00Z",
    "type": "voice_command",
    "command": "open Chrome and go to GitHub",
    "actions": [...],
    "results": [...],
    "duration": 3.2
}

# Conversations stored
{
    "timestamp": "2026-02-05T18:30:15Z",
    "type": "conversation",
    "user": "How long will this take?",
    "assistant": "About 2-3 minutes. I'm at 30% now.",
    "context": {...}
}
```

### Context Retrieval

The orchestrator consults Dive Memory for:
- Previous similar commands
- User preferences
- Common workflows
- Error patterns

---

## 🌍 Multi-language Support

### Supported Languages

Currently supported:
- English (en-US)
- Vietnamese (vi-VN) - Coming soon
- Chinese (zh-CN) - Coming soon

### Configuration

```bash
# In .env
VOICE_LANGUAGE=vi-VN
```

```python
# In code
processor = ContinuousVoiceProcessor(
    language="vi-VN",
    wake_word="xin chào dive"
)
```

---

## 🚧 Future Enhancements

### Planned Features

1. **Emotion Detection** - Detect user emotion from voice tone
2. **Proactive Assistance** - AI suggests actions based on context
3. **Multi-modal Input** - Combine voice with gesture/eye tracking
4. **Collaborative Mode** - Multiple users control together
5. **Custom Wake Words** - User-defined activation phrases
6. **Voice Profiles** - Per-user voice settings and preferences
7. **Advanced Vision** - Full UI-TARS vision model integration
8. **Mobile Control** - Control desktop from mobile device

---

## 📚 API Reference

### ContinuousVoiceProcessor

```python
processor = ContinuousVoiceProcessor(
    stt_provider="whisper",      # STT engine
    tts_provider="pyttsx3",      # TTS engine
    wake_word="hey dive",        # Activation phrase
    language="en-US",            # Language code
    api_key="sk-..."             # OpenAI API key
)

# Start processing
processor.start()

# Set callbacks
processor.on_command = handle_command
processor.on_conversation = handle_conversation

# Speak (non-blocking)
processor.speak("Hello!", priority=True)

# Stop processing
processor.stop()
```

### UITARSClient

```python
client = UITARSClient(
    uitars_path="/path/to/UI-TARS-desktop",
    api_url="http://localhost:8080",
    model="ui-tars-1.5"
)

# Execute command
for result in client.execute_command("open Chrome", stream_feedback=True):
    print(result)

# Direct actions
client._open_app("chrome")
client._navigate("https://github.com")
client._click(100, 200)
client._type_text("Hello World")
client._screenshot()
```

### DiveVoiceOrchestrator

```python
orchestrator = DiveVoiceOrchestrator(
    stt_provider="whisper",
    tts_provider="pyttsx3",
    wake_word="hey dive",
    api_key="sk-...",
    uitars_path="/path/to/UI-TARS-desktop"
)

# Start orchestrator
orchestrator.start()

# Get status
status = orchestrator.get_status()

# Save session
orchestrator.save_session("session.json")

# Stop orchestrator
orchestrator.stop()
```

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:

1. **Better NLP** - Improve command parsing accuracy
2. **More Languages** - Add support for more languages
3. **UI-TARS Vision** - Full integration with UI-TARS vision model
4. **Performance** - Optimize latency and resource usage
5. **Documentation** - Improve docs and examples

---

## 📄 License

This project is part of DIVE AI V25 and follows the same license.

---

## 🙏 Acknowledgments

- **UI-TARS** by ByteDance - Desktop automation framework
- **OpenAI Whisper** - Speech recognition
- **pyttsx3** - Text-to-speech
- **PyAutoGUI** - UI automation

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the architecture documentation
3. Open an issue on GitHub
4. Join our Discord community

---

**Happy voice controlling! 🎤🤖**
