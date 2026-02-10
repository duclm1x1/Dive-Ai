# Dive AI V20.4.1 - Auto-Install System

**Release Date:** February 5, 2026

## 🎯 Overview

This release adds a complete auto-installation system that automatically executes all setup scripts when users clone Dive AI from GitHub. The system now provides a seamless, zero-configuration first-run experience.

## ✨ New Features

### Auto-Install System
- **`install.sh`**: Comprehensive auto-installation script that orchestrates the entire setup process
  - Automatic Python version detection
  - Non-interactive API key configuration with default values
  - Automatic execution of first-run setup
  - Memory system initialization
  - Health checks and validation
  - Installation summary report

### Seamless Setup Flow
1. **API Key Setup**: Automatically configures `.env` file with default API keys (users can customize later)
2. **First Run Setup**: Executes `first_run_complete.py` to initialize memory system and documentation
3. **Memory Loading**: Scans and loads existing memory files
4. **Ready to Use**: System is fully operational after installation completes

## 🔧 Technical Improvements

### Non-Interactive Mode
- Modified `setup_api_keys.py` to support non-interactive execution
- Default API keys are automatically used when no input is provided
- `.env` file is created with secure permissions (600)

### Installation Validation
- Python version check (requires 3.11+)
- Step-by-step progress reporting
- Error handling with graceful fallbacks
- Summary report showing system status

## 📦 Installation

```bash
# Clone and auto-install in one command
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai
chmod +x install.sh
./install.sh
```

## 🚀 Quick Start

After installation completes:

```bash
# Start Dive AI
python3 dive_ai_complete_system.py

# Or use the enhanced workflow
python3 core/dive_enhanced_workflow.py
```

## 📋 System Requirements

- Python 3.11+
- Linux/macOS (Windows via WSL)
- Internet connection for API access

## 🔐 Security

- API keys stored in `.env` file (never committed to git)
- `.env` file has secure permissions (600)
- `.gitignore` configured to exclude sensitive files

## 🐛 Bug Fixes

- Fixed EOFError when running setup scripts non-interactively
- Improved error handling in installation pipeline
- Better validation of memory system initialization

## 📚 Documentation

- Updated README with installation instructions
- Added installation troubleshooting guide
- Documented auto-install system architecture

## 🔄 Migration from V20.4.0

If you're upgrading from V20.4.0:

```bash
cd Dive-Ai
git pull origin main
./install.sh
```

Your existing memory files and configuration will be preserved.

## 🙏 Credits

Developed by the Dive AI team with focus on user experience and autonomous operation.

---

**Full Changelog**: https://github.com/duclm1x1/Dive-Ai/compare/v20.4.0...v20.4.1
