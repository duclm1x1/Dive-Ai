# 🚀 Dive AI - Quick Start with Secure Setup

## Installation (3 Simple Steps)

### Step 1: Clone Repository
```bash
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai
```

### Step 2: Setup API Keys (Automated)
```bash
python3 setup_api_keys.py
```

**What this does**:
- ✅ Creates `.env` file with your API keys
- ✅ Secures file with proper permissions (600)
- ✅ Provides default keys (just press ENTER)
- ✅ Or enter your own custom keys

**Example**:
```
🔐 DIVE AI - API KEY SETUP
======================================================================

1. V98API Key
   Default: sk-dBWRD0cFgIBLf36nP...
   Enter key (or press ENTER for default): [PRESS ENTER]

2. AICoding API Key
   Default: sk-dev-0kgTls1jmGOn3...
   Enter key (or press ENTER for default): [PRESS ENTER]

✅ Setup complete!
```

### Step 3: Install & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run Dive AI
python3 dive_ai_startup.py
```

---

## 🔐 Security Features

- **No Hardcoded Keys**: All API keys stored in `.env` (never committed)
- **Auto-Protected**: `.env` automatically ignored by git
- **One-Command Setup**: `python3 setup_api_keys.py` handles everything
- **Secure Permissions**: `.env` file set to owner-only access (600)
- **Safe Defaults**: Pre-configured keys included for instant setup

---

## 📋 What's Different?

### Old Way (Insecure) ❌
```python
# Hardcoded keys in code
api_key = "sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y"
```

### New Way (Secure) ✅
```python
# Keys loaded from .env
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("V98API_KEY")
```

---

## ⚠️ Important Notes

1. **Never commit `.env`** - It's automatically ignored by git
2. **Share `.env.example`** - Not your actual `.env` file
3. **Run setup first** - Before any other commands
4. **Keep keys secret** - Don't paste them in issues/chat

---

## 📚 Full Documentation

- **Security Guide**: See [SECURITY.md](./SECURITY.md)
- **Complete README**: See [README.md](./README.md)
- **API Providers**: See [PROVIDER_INSTRUCTION_MANUAL.md](./PROVIDER_INSTRUCTION_MANUAL.md)

---

## 🆘 Troubleshooting

**Problem**: API keys not loading  
**Solution**: Run `python3 setup_api_keys.py`

**Problem**: `.env` appears in git status  
**Solution**: It shouldn't! Check `.gitignore`

**Problem**: Permission denied on `.env`  
**Solution**: `chmod 600 .env`

---

## 🎉 That's It!

You're now ready to use Dive AI securely!

```bash
python3 dive_ai_startup.py
```

For detailed information, see [SECURITY.md](./SECURITY.md)
