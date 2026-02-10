#!/bin/bash
###############################################################################
# Dive AI V25 - Voice + UI-TARS Installation Script
# Installs all dependencies for continuous voice interaction and UI-TARS
###############################################################################

set -e  # Exit on error

echo "=================================="
echo "Dive AI V25 - Voice + UI-TARS Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

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
# 1. Install System Dependencies
###############################################################################

echo "📦 Installing system dependencies..."

if [ "$OS" == "linux" ]; then
    sudo apt-get update
    sudo apt-get install -y \
        python3-pyaudio \
        portaudio19-dev \
        flac \
        espeak \
        ffmpeg \
        xdotool \
        scrot \
        python3-tk \
        python3-dev
    
    echo -e "${GREEN}✓ System dependencies installed${NC}"
    
elif [ "$OS" == "macos" ]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    brew install portaudio
    brew install flac
    brew install espeak
    brew install ffmpeg
    
    echo -e "${GREEN}✓ System dependencies installed${NC}"
fi

echo ""

###############################################################################
# 2. Install Python Dependencies
###############################################################################

echo "🐍 Installing Python dependencies..."

# Upgrade pip
sudo pip3 install --upgrade pip

# Voice processing
sudo pip3 install --system \
    SpeechRecognition \
    pyttsx3 \
    pyaudio \
    openai \
    pygame

# UI automation
sudo pip3 install --system \
    pyautogui \
    pynput \
    pillow \
    opencv-python

# Additional dependencies
sudo pip3 install --system \
    requests \
    python-dotenv

echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

###############################################################################
# 3. Install UI-TARS Desktop
###############################################################################

echo "🖥️ Installing UI-TARS Desktop..."

# Check if UI-TARS is already installed
UITARS_PATH="$HOME/UI-TARS-desktop"

if [ -d "$UITARS_PATH" ]; then
    echo -e "${YELLOW}UI-TARS already exists at $UITARS_PATH${NC}"
    read -p "Do you want to reinstall? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$UITARS_PATH"
    else
        echo "Skipping UI-TARS installation"
    fi
fi

if [ ! -d "$UITARS_PATH" ]; then
    echo "Cloning UI-TARS repository..."
    git clone https://github.com/bytedance/UI-TARS-desktop.git "$UITARS_PATH"
    
    cd "$UITARS_PATH"
    
    # Install Node.js dependencies
    echo "Installing Node.js dependencies..."
    pnpm install
    
    echo -e "${GREEN}✓ UI-TARS Desktop installed${NC}"
else
    echo -e "${GREEN}✓ UI-TARS Desktop already installed${NC}"
fi

echo ""

###############################################################################
# 4. Configure Environment
###############################################################################

echo "⚙️ Configuring environment..."

# Create .env file if it doesn't exist
ENV_FILE="$(dirname "$0")/.env"

if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
# Dive AI V25 - Voice + UI-TARS Configuration

# OpenAI API Key (for Whisper STT and GPT)
OPENAI_API_KEY=your-api-key-here

# V98 API Configuration
V98_API_KEY=YOUR_V98_API_KEY_HERE
V98_BASE_URL=https://v98store.com/v1

# AI Coding API Configuration
AICODING_API_KEY=YOUR_AICODING_API_KEY_HERECJCk
AICODING_BASE_URL=https://aicoding.io.vn/v1

# Voice Configuration
VOICE_STT_PROVIDER=google  # whisper, google, sphinx
VOICE_TTS_PROVIDER=pyttsx3  # pyttsx3, openai
VOICE_WAKE_WORD=hey dive
VOICE_LANGUAGE=en-US

# UI-TARS Configuration
UITARS_PATH=$HOME/UI-TARS-desktop
UITARS_API_URL=http://localhost:8080
UITARS_MODEL=ui-tars-1.5

# Dive Memory Configuration
DIVE_MEMORY_PATH=./memory/dive_memory.db
EOF
    
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your OpenAI API key${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""

###############################################################################
# 5. Test Installation
###############################################################################

echo "🧪 Testing installation..."

# Test Python imports
python3 << 'EOF'
import sys

modules = [
    "speech_recognition",
    "pyttsx3",
    "pyaudio",
    "openai",
    "pyautogui",
    "requests"
]

failed = []
for module in modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError:
        print(f"✗ {module}")
        failed.append(module)

if failed:
    print(f"\n⚠ Failed to import: {', '.join(failed)}")
    sys.exit(1)
else:
    print("\n✓ All Python modules imported successfully")
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation test passed${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    exit 1
fi

echo ""

###############################################################################
# 6. Create Launch Scripts
###############################################################################

echo "🚀 Creating launch scripts..."

# Voice orchestrator launcher
cat > "$(dirname "$0")/start_voice_control.sh" << 'EOF'
#!/bin/bash
# Launch Dive AI Voice Control

cd "$(dirname "$0")"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start voice orchestrator
python3 core/dive_voice_orchestrator.py "$@"
EOF

chmod +x "$(dirname "$0")/start_voice_control.sh"

echo -e "${GREEN}✓ Launch script created: start_voice_control.sh${NC}"

echo ""

###############################################################################
# 7. Summary
###############################################################################

echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Run: ./start_voice_control.sh"
echo "3. Say 'hey dive' to activate voice control"
echo ""
echo "Examples:"
echo "  - 'Hey Dive, open Chrome'"
echo "  - 'Hey Dive, go to GitHub'"
echo "  - 'Hey Dive, search for UI-TARS'"
echo ""
echo "For more information, see:"
echo "  - docs/CONTINUOUS_VOICE_UITARS_ARCHITECTURE.md"
echo "  - README.md"
echo ""
echo "=================================="
