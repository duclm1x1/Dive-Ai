#!/bin/bash
###############################################################################
# Dive AI V25 - Full-Duplex Voice Installation
# Installs streaming TTS, VAD barge-in, talk-while-act, and UI-TARS
###############################################################################

set -e

echo "=========================================================================="
echo "Dive AI V25 - Full-Duplex Voice Installation"
echo "=========================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS${NC}"
echo ""

###############################################################################
# 1. System Dependencies
###############################################################################

echo -e "${BLUE}[1/6] Installing system dependencies...${NC}"

if [ "$OS" == "linux" ]; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        python3-pyaudio \
        portaudio19-dev \
        flac \
        espeak \
        ffmpeg \
        xdotool \
        scrot \
        python3-tk \
        python3-dev \
        libasound2-dev \
        libportaudio2 \
        libportaudiocpp0 \
        2>/dev/null
    
    echo -e "${GREEN}✓ System dependencies installed${NC}"
    
elif [ "$OS" == "macos" ]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    brew install portaudio flac espeak ffmpeg 2>/dev/null || true
    echo -e "${GREEN}✓ System dependencies installed${NC}"
fi

echo ""

###############################################################################
# 2. Python Dependencies
###############################################################################

echo -e "${BLUE}[2/6] Installing Python dependencies...${NC}"

# Core voice processing
sudo pip3 install --system --quiet \
    SpeechRecognition \
    pyttsx3 \
    pyaudio \
    openai \
    pygame \
    webrtcvad \
    numpy

# UI automation
sudo pip3 install --system --quiet \
    pyautogui \
    pynput \
    pillow \
    opencv-python

# Additional
sudo pip3 install --system --quiet \
    requests \
    python-dotenv

echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

###############################################################################
# 3. UI-TARS Desktop
###############################################################################

echo -e "${BLUE}[3/6] Installing UI-TARS Desktop...${NC}"

UITARS_PATH="$HOME/UI-TARS-desktop"

if [ -d "$UITARS_PATH" ]; then
    echo -e "${YELLOW}UI-TARS already exists${NC}"
else
    git clone --quiet https://github.com/bytedance/UI-TARS-desktop.git "$UITARS_PATH" 2>/dev/null || true
    
    if [ -d "$UITARS_PATH" ]; then
        cd "$UITARS_PATH"
        pnpm install --silent 2>/dev/null || npm install --silent 2>/dev/null || true
        echo -e "${GREEN}✓ UI-TARS Desktop installed${NC}"
    else
        echo -e "${YELLOW}⚠ UI-TARS installation skipped${NC}"
    fi
fi

cd "$(dirname "$0")"
echo ""

###############################################################################
# 4. Configure Environment
###############################################################################

echo -e "${BLUE}[4/6] Configuring environment...${NC}"

ENV_FILE="$(dirname "$0")/.env"

if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
# Dive AI V25 - Full-Duplex Voice Configuration

# OpenAI API Key (for Whisper STT and GPT)
OPENAI_API_KEY=your-api-key-here

# V98 API Configuration
V98_API_KEY=sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y
V98_BASE_URL=https://v98store.com/v1

# AI Coding API Configuration
AICODING_API_KEY=sk-dev-0kgTls1jmGOn3K4Fdl7Rdudkl7QSCJCk
AICODING_BASE_URL=https://aicoding.io.vn/v1

# Voice Configuration
VOICE_STT_PROVIDER=google
VOICE_TTS_PROVIDER=pyttsx3
VOICE_WAKE_WORD=hey dive
VOICE_LANGUAGE=en-US

# Full-Duplex Features
ENABLE_STREAMING_TTS=true
ENABLE_VAD_BARGEIN=true
ENABLE_TALK_WHILE_ACT=true
NARRATION_STYLE=detailed

# UI-TARS Configuration
UITARS_PATH=$HOME/UI-TARS-desktop
UITARS_API_URL=http://localhost:8080
UITARS_MODEL=ui-tars-1.5

# Dive Memory
DIVE_MEMORY_PATH=./memory/dive_memory.db
EOF
    
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""

###############################################################################
# 5. Test Installation
###############################################################################

echo -e "${BLUE}[5/6] Testing installation...${NC}"

python3 << 'EOF'
import sys

modules = {
    "speech_recognition": "SpeechRecognition",
    "pyttsx3": "pyttsx3",
    "pyaudio": "PyAudio",
    "openai": "OpenAI",
    "pyautogui": "PyAutoGUI",
    "webrtcvad": "WebRTC VAD",
    "pygame": "Pygame",
    "numpy": "NumPy"
}

failed = []
for module, name in modules.items():
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError:
        print(f"✗ {name}")
        failed.append(name)

if failed:
    print(f"\n⚠ Optional modules not installed: {', '.join(failed)}")
    print("  Some features may not work")
else:
    print("\n✓ All modules imported successfully")
EOF

echo ""

###############################################################################
# 6. Create Launch Scripts
###############################################################################

echo -e "${BLUE}[6/6] Creating launch scripts...${NC}"

# Full-duplex launcher
cat > "$(dirname "$0")/start_fullduplex.sh" << 'EOF'
#!/bin/bash
# Launch Dive AI Full-Duplex Voice Control

cd "$(dirname "$0")"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start full-duplex orchestrator
python3 core/dive_fullduplex_orchestrator.py "$@"
EOF

chmod +x "$(dirname "$0")/start_fullduplex.sh"

echo -e "${GREEN}✓ Launch script created: start_fullduplex.sh${NC}"

echo ""

###############################################################################
# Summary
###############################################################################

echo "=========================================================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=========================================================================="
echo ""
echo "Features installed:"
echo "  ✓ Streaming TTS (chunk-based audio output)"
echo "  ✓ VAD Barge-in (voice interruption)"
echo "  ✓ Talk-While-Act (real-time narration)"
echo "  ✓ UI-TARS Desktop integration"
echo "  ✓ 128 Agent Fleet"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OpenAI API key"
echo "  2. Run: ./start_fullduplex.sh"
echo "  3. Say 'hey dive' to activate"
echo ""
echo "Examples:"
echo "  User: 'Hey Dive, open Chrome'"
echo "  AI:   'Opening Chrome' [opens Chrome] 'Chrome is now open'"
echo ""
echo "  User: 'Search for UI-TARS'"
echo "  AI:   'Searching for UI-TARS' [searches] 'Search results found'"
echo ""
echo "  [AI is speaking...]"
echo "  User: [starts speaking]"
echo "  AI:   [immediately stops and listens]"
echo ""
echo "Documentation:"
echo "  - docs/CONTINUOUS_VOICE_UITARS_ARCHITECTURE.md"
echo "  - docs/VOICE_UITARS_README.md"
echo "  - README_V25.md"
echo ""
echo "=========================================================================="
