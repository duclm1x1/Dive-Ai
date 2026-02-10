# Continuous Voice Interaction with UI-TARS Architecture

## Overview

This document describes the architecture for integrating UI-TARS desktop automation with DIVE AI V25, enabling continuous voice interaction for computer control.

## Key Requirements

1. **Continuous Voice Interaction**: AI maintains ongoing conversation while executing tasks
2. **Non-Blocking Voice Processing**: Voice input/output continues during task execution
3. **Computer Control**: AI can control computer through natural language commands
4. **A-Z Automation**: Commands like "open [application]" execute automatically from start to finish
5. **Real-time Feedback**: User receives continuous audio feedback during task execution

## System Architecture

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
│  ┌────────────────────────────────────────────────────┐         │
│  │  Continuous Speech Recognition (Whisper/Deepgram)  │         │
│  │  - Real-time transcription                         │         │
│  │  - Wake word detection                             │         │
│  │  - Intent classification                           │         │
│  └────────────────────────────────────────────────────┘         │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Continuous Speech Synthesis (ElevenLabs/Azure)    │         │
│  │  - Streaming TTS output                            │         │
│  │  - Non-blocking audio playback                     │         │
│  │  - Emotion/tone modulation                         │         │
│  └────────────────────────────────────────────────────┘         │
└─────────┬──────────────────▲──────────────────▲─────────────────┘
          │                  │                  │
┌─────────▼──────────────────┼──────────────────┼─────────────────┐
│           DIVE AI Orchestration Layer                            │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Dive Orchestrator (Multi-threaded)                │         │
│  │  - Thread 1: Voice conversation handler            │         │
│  │  - Thread 2: Task execution handler                │         │
│  │  - Thread 3: UI-TARS control handler               │         │
│  │  - Shared memory: Task queue & status              │         │
│  └────────────────────────────────────────────────────┘         │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Dive Memory (Context Management)                  │         │
│  │  - Conversation history                            │         │
│  │  - Task execution state                            │         │
│  │  - UI-TARS action logs                             │         │
│  └────────────────────────────────────────────────────┘         │
└─────────┬──────────────────▲──────────────────▲─────────────────┘
          │                  │                  │
┌─────────▼──────────────────┼──────────────────┼─────────────────┐
│              UI-TARS Integration Layer                           │
│  ┌────────────────────────────────────────────────────┐         │
│  │  UI-TARS Desktop Agent (Modified)                  │         │
│  │  - Screenshot capture & analysis                   │         │
│  │  - Mouse/keyboard control                          │         │
│  │  - Application automation                          │         │
│  │  - Browser automation                              │         │
│  └────────────────────────────────────────────────────┘         │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Action Execution Engine                           │         │
│  │  - Parse natural language commands                 │         │
│  │  - Generate UI-TARS action sequences               │         │
│  │  - Execute with real-time feedback                 │         │
│  └────────────────────────────────────────────────────┘         │
└─────────┬──────────────────▲──────────────────────────────────────┘
          │                  │
┌─────────▼──────────────────┴─────────────────────────────────────┐
│                    Operating System Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Windows     │  │   macOS      │  │    Linux     │           │
│  │  Automation  │  │  Automation  │  │  Automation  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Voice Processing Layer

#### Continuous Speech Recognition
- **Technology**: Whisper API (OpenAI) or Deepgram for real-time STT
- **Features**:
  - Continuous audio stream processing
  - Wake word detection ("Hey DIVE", "DIVE AI")
  - Intent classification (command vs. conversation)
  - Multi-language support

#### Continuous Speech Synthesis
- **Technology**: ElevenLabs Streaming API or Azure TTS
- **Features**:
  - Streaming audio output (low latency)
  - Non-blocking playback (continues during task execution)
  - Emotion/tone modulation based on context
  - Background conversation during automation

### 2. DIVE AI Orchestration Layer

#### Multi-threaded Architecture
```python
class DiveVoiceOrchestrator:
    def __init__(self):
        self.voice_thread = Thread(target=self.voice_handler)
        self.task_thread = Thread(target=self.task_handler)
        self.uitars_thread = Thread(target=self.uitars_handler)
        self.shared_queue = Queue()
        self.conversation_active = True
        
    def voice_handler(self):
        """Continuous voice conversation"""
        while self.conversation_active:
            # Listen for voice input
            audio = self.listen()
            text = self.stt(audio)
            
            # Classify intent
            if self.is_command(text):
                self.shared_queue.put(('command', text))
            else:
                # Continue conversation
                response = self.generate_response(text)
                self.tts_stream(response)
    
    def task_handler(self):
        """Process commands from queue"""
        while True:
            msg_type, content = self.shared_queue.get()
            if msg_type == 'command':
                # Parse and execute
                self.execute_command(content)
                # Provide voice feedback
                self.tts_stream(f"Executing: {content}")
    
    def uitars_handler(self):
        """Control UI-TARS actions"""
        while True:
            if self.has_pending_actions():
                action = self.get_next_action()
                result = self.uitars_client.execute(action)
                # Provide real-time feedback
                self.tts_stream(f"Completed: {action}")
```

### 3. UI-TARS Integration

#### Modified UI-TARS Client
```python
class DiveUITARSClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def execute_command(self, natural_language_command: str):
        """
        Execute natural language command through UI-TARS
        Example: "open Chrome and go to GitHub"
        """
        # Step 1: Parse command into UI-TARS actions
        actions = self.parse_to_actions(natural_language_command)
        
        # Step 2: Execute each action with feedback
        for action in actions:
            result = self.execute_action(action)
            yield result  # Stream results back
            
    def parse_to_actions(self, command: str) -> List[Dict]:
        """Use LLM to convert natural language to UI-TARS actions"""
        prompt = f"""
        Convert this command to UI-TARS actions:
        Command: {command}
        
        Available actions:
        - screenshot: Capture screen
        - click: Click at coordinates or element
        - type: Type text
        - open_app: Open application
        - navigate: Navigate browser
        
        Return JSON array of actions.
        """
        # Call LLM to generate action sequence
        return self.llm_client.generate(prompt)
```

## Implementation Phases

### Phase 1: Voice Processing Setup
1. Install speech recognition libraries (Whisper, SpeechRecognition)
2. Install TTS libraries (pyttsx3, gTTS, or ElevenLabs SDK)
3. Create continuous audio stream handlers
4. Implement wake word detection

### Phase 2: DIVE AI Integration
1. Create multi-threaded orchestrator
2. Implement shared queue for command passing
3. Integrate with Dive Memory for context
4. Add conversation state management

### Phase 3: UI-TARS Integration
1. Set up UI-TARS desktop agent
2. Create API client for UI-TARS
3. Implement natural language to action parser
4. Add real-time feedback mechanism

### Phase 4: End-to-End Testing
1. Test voice recognition accuracy
2. Test command execution reliability
3. Test continuous conversation during automation
4. Optimize latency and performance

## Technical Stack

### Voice Processing
- **STT**: OpenAI Whisper API / Deepgram
- **TTS**: ElevenLabs Streaming API / Azure TTS / pyttsx3
- **Audio**: PyAudio, sounddevice

### DIVE AI
- **Orchestration**: Python threading/asyncio
- **Memory**: Dive Memory (SQLite/ChromaDB)
- **LLM**: OpenAI GPT-4, Anthropic Claude, or V98 models

### UI-TARS
- **Desktop Agent**: UI-TARS Desktop (Node.js/Electron)
- **API**: REST API or WebSocket
- **Automation**: Playwright, Puppeteer

## Configuration

### Environment Variables
```bash
# Voice Processing
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
DEEPGRAM_API_KEY=...

# DIVE AI
DIVE_MEMORY_PATH=/path/to/memory
DIVE_ORCHESTRATOR_PORT=8000

# UI-TARS
UITARS_API_URL=http://localhost:8080
UITARS_MODEL=ui-tars-1.5
```

### Configuration File
```yaml
# config/voice_uitars.yaml
voice:
  stt_provider: whisper  # whisper, deepgram
  tts_provider: elevenlabs  # elevenlabs, azure, pyttsx3
  wake_word: "hey dive"
  language: en-US
  continuous_mode: true

orchestrator:
  threads: 3
  queue_size: 100
  memory_enabled: true
  
uitars:
  api_url: http://localhost:8080
  model: ui-tars-1.5
  screenshot_interval: 1.0
  action_delay: 0.5
```

## Usage Examples

### Example 1: Open Application
```
User: "Hey DIVE, open Chrome"
DIVE: "Opening Chrome for you..." [executes]
DIVE: "Chrome is now open. What would you like to do?"
```

### Example 2: Complex Task
```
User: "Go to GitHub and check my Dive-Ai repository"
DIVE: "Sure, navigating to GitHub..." [opens browser]
DIVE: "I'm on GitHub now, searching for your Dive-Ai repository..." [searches]
DIVE: "Found it! The repository has 26.7k stars. Would you like me to check the issues?"
```

### Example 3: Continuous Conversation During Task
```
User: "Install the dependencies for the project"
DIVE: "Starting installation..." [runs npm install]
User: "How long will this take?"
DIVE: "Based on the package.json, it should take about 2-3 minutes. I'm at 30% now."
[Installation continues in background]
DIVE: "Installation complete! All dependencies are ready."
```

## Security Considerations

1. **Voice Authentication**: Optional voice biometric authentication
2. **Command Confirmation**: Require confirmation for sensitive actions
3. **Sandbox Execution**: Run UI-TARS actions in isolated environment
4. **Audit Logging**: Log all voice commands and actions to Dive Memory
5. **Privacy**: All voice processing can be done locally (Whisper local model)

## Performance Optimization

1. **Streaming TTS**: Use streaming APIs to reduce latency
2. **Parallel Processing**: Run voice and automation in separate threads
3. **Caching**: Cache common UI-TARS action sequences
4. **Memory Management**: Limit conversation history to last N turns
5. **GPU Acceleration**: Use GPU for local Whisper inference

## Future Enhancements

1. **Multi-language Support**: Support Vietnamese, Chinese, etc.
2. **Emotion Detection**: Detect user emotion from voice tone
3. **Proactive Assistance**: AI suggests actions based on context
4. **Multi-modal Input**: Combine voice with gesture/eye tracking
5. **Collaborative Mode**: Multiple users can control together
