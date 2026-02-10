# Dive AI Desktop - Quick Start Guide

## 🚀 Installation

### Option 1: Using Build Script (Recommended for Development)

1. **Run build script:**

   ```bash
   build.bat
   ```

2. **Run setup wizard:**

   ```bash
   dist\DiveAI-Setup-Wizard.exe
   ```

3. **Start system tray:**

   ```bash
   dist\DiveAI-Tray.exe
   ```

### Option 2: Manual Installation

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install pystray Pillow requests
   ```

2. **Run setup wizard:**

   ```bash
   python first_run_setup.py
   ```

3. **Start system tray:**

   ```bash
   python diveai_tray.py
   ```

---

## 📋 First-Time Setup

The setup wizard will guide you through:

1. **Welcome** - Introduction to Dive AI
2. **API Keys** - Configure V98 and AICoding (optional)
3. **Desktop Channels** - Select Discord/Telegram/Zalo paths (optional)
4. **Complete** - Ready to use!

All settings are saved to `.env` file.

---

## 🎯 Using the System Tray

After installation, look for the **Dive AI icon** in your system tray (bottom-right corner).

**Right-click the icon** for options:

- 🚀 **Start Gateway** - Launches the Gateway Server on port 1879
- ⏹️ **Stop Gateway** - Stops the Gateway Server
- 📊 **Check Status** - View system statistics
- 🌐 **Open Web UI** - Opens <http://localhost:1879/docs> in browser
- ⚙️ **Settings** - Edit `.env` configuration
- 📁 **Open Folder** - Open installation directory
- ❌ **Quit** - Exit Dive AI

---

## 🌐 Using the Gateway

Once the Gateway is running, you can access it at:

- **Web UI**: <http://localhost:1879/docs>
- **Health Check**: <http://localhost:1879/health>
- **Statistics**: <http://localhost:1879/statistics>
- **Algorithms List**: <http://localhost:1879/algorithms>

### Example API Request

```bash
curl -X POST http://localhost:1879/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a Python function for binary search",
    "channel": "web",
    "user_id": "test_user"
  }'
```

---

## 🖥️ Desktop Channels

To use Discord/Telegram/Zalo channels:

1. Install the desktop apps:
   - Discord Desktop: <https://discord.com/download>
   - Telegram Desktop: <https://desktop.telegram.org/>
   - Zalo PC: <https://zalo.me/pc>

2. Configure paths in Settings or during setup wizard

3. Channels will auto-launch and monitor specified chats

---

## 🧬 Self-Evolving System

The self-evolving system runs automatically:

- **Algorithm Generation** - Creates new algorithms when needed
- **Algorithm Optimization** - Improves performance over time
- **Statistics Tracking** - Monitors all executions

View evolution status at: <http://localhost:1879/evolution/status>

---

## 🔧 Configuration

Edit `.env` file for configuration:

```ini
# LLM API Keys
V98_API_KEY=your_key_here
AICODING_API_KEY=your_key_here

# Desktop Channels
DISCORD_PATH=C:\Path\To\Discord.exe
TELEGRAM_PATH=C:\Path\To\Telegram.exe
ZALO_PATH=C:\Path\To\Zalo.exe

# Optional Settings
GATEWAY_PORT=1879
AUTO_START=true
```

---

## 📊 System Requirements

- **OS**: Windows 10/11
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB free space

---

## 🆘 Troubleshooting

### Gateway won't start

- Check if port 1879 is already in use
- Check Python installation
- View logs in console window

### Desktop channels not working

- Verify app paths in `.env`
- Ensure apps are installed
- Check app permissions

### API errors

- Verify API keys in `.env`
- Check internet connection
- Confirm API quota/limits

---

## 🎓 Next Steps

1. **Try the Demo**: Run `python demo.py` for interactive demo
2. **Read Documentation**: Check `walkthrough.md` for full system overview
3. **Customize**: Add your own algorithms to `core/algorithms/`
4. **Integrate**: Connect your channels and workflows

---

## 📞 Support

- **Documentation**: See `walkthrough.md` and other `.md` files
- **Issues**: Check logs and error messages
- **Updates**: System auto-updates algorithms

---

**Made with 🧬 by Dive AI Self-Evolving System**  
**Version 29.3 - The Future of Agentic AI**
