# 🔐 Dive AI Security Guide

**Last Updated**: February 5, 2026  
**Version**: 2.0

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Security Overview](#security-overview)
3. [API Key Management](#api-key-management)
4. [Installation Security](#installation-security)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### First-Time Setup

```bash
# 1. Clone the repository
git clone https://github.com/duclm1x1/Dive-Ai.git
cd Dive-Ai

# 2. Run the automated setup (creates .env with your API keys)
python3 setup_api_keys.py

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start using Dive AI
python3 dive_ai_startup.py
```

**That's it!** Your API keys are now securely stored in `.env` and will never be committed to git.

---

## Security Overview

### What We've Implemented

✅ **Environment Variables**: All API keys stored in `.env` file  
✅ **Git Ignore**: `.env` and sensitive files automatically ignored  
✅ **Auto-Setup**: One-command setup creates `.env` with your keys  
✅ **File Permissions**: `.env` file set to 600 (owner read/write only)  
✅ **No Hardcoded Keys**: All code uses `os.getenv()` to load keys  
✅ **Example Templates**: `.env.example` provided for reference  

### Security Architecture

```
┌─────────────────────────────────────────┐
│  User runs: python3 setup_api_keys.py  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Creates .env file with API keys        │
│  (Permissions: 600 - owner only)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  .gitignore prevents .env from being    │
│  committed to repository                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  All Python code loads keys from .env   │
│  using os.getenv() with fallback        │
└─────────────────────────────────────────┘
```

---

## API Key Management

### Supported Providers

| Provider | Environment Variable | Required | Default Provided |
|----------|---------------------|----------|------------------|
| V98Store | `V98API_KEY` | ✅ Yes | ✅ Yes |
| AICoding | `AICODING_API_KEY` | ✅ Yes | ✅ Yes |
| OpenAI | `OPENAI_API_KEY` | ❌ Optional | ❌ No |
| Anthropic | `ANTHROPIC_API_KEY` | ❌ Optional | ❌ No |

### How API Keys Are Loaded

All Python files now use this pattern:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key with fallback
api_key = os.getenv("V98API_KEY", "default_key_here")
```

This ensures:
- ✅ Keys are loaded from `.env` if it exists
- ✅ Falls back to default if `.env` is missing
- ✅ No hardcoded keys in the codebase
- ✅ Easy to update keys without code changes

### Updating API Keys

**Method 1: Re-run Setup Script**
```bash
python3 setup_api_keys.py
# Follow prompts to enter new keys
```

**Method 2: Edit .env Directly**
```bash
nano .env
# Update the keys manually
```

**Method 3: Environment Variables**
```bash
export V98API_KEY="your_new_key_here"
export AICODING_API_KEY="your_new_key_here"
```

---

## Installation Security

### Automated Setup Process

The `setup_api_keys.py` script provides a secure, user-friendly setup:

**Features**:
- ✅ Interactive prompts for API keys
- ✅ Default keys pre-configured (press ENTER to use)
- ✅ Custom keys supported (enter your own)
- ✅ Automatic `.env` creation
- ✅ File permissions set to 600
- ✅ Verification after setup
- ✅ Clear next steps provided

**What It Creates**:

1. **`.env`** - Your actual API keys (NEVER commit this)
2. **`.env.example`** - Template without real keys (safe to commit)

### File Structure

```
Dive-Ai/
├── .env                    # ❌ NEVER COMMIT (your actual keys)
├── .env.example            # ✅ Safe to commit (template)
├── setup_api_keys.py       # ✅ Setup script
├── .gitignore              # ✅ Protects .env
└── ...
```

### What's Protected by .gitignore

The following files/patterns are automatically ignored:

```gitignore
# Environment files
.env
.env.local
.env.*.local
.env.production
.env.development
.env.test
*.env

# Configuration files with keys
config.json
config.local.json
account_pools.json

# Secrets
secrets/
*.key
*.pem
*.crt
*.secret
*.credentials
api_keys.txt
api_keys.json
credentials.json
```

---

## Best Practices

### ✅ DO

1. **Run setup script first**
   ```bash
   python3 setup_api_keys.py
   ```

2. **Keep .env local**
   - Never commit `.env` to git
   - Never share `.env` in messages/emails
   - Never upload `.env` to cloud storage

3. **Use .env.example for sharing**
   - Share `.env.example` with team members
   - They run `setup_api_keys.py` to create their own `.env`

4. **Rotate keys regularly**
   - Update keys every 90 days
   - Rotate immediately if compromised

5. **Set proper permissions**
   ```bash
   chmod 600 .env  # Owner read/write only
   ```

6. **Use different keys for different environments**
   - Development: `.env.development`
   - Production: `.env.production`
   - Testing: `.env.test`

### ❌ DON'T

1. **Never hardcode API keys**
   ```python
   # ❌ BAD
   api_key = "YOUR_V98_API_KEY_HERE"
   
   # ✅ GOOD
   api_key = os.getenv("V98API_KEY")
   ```

2. **Never commit .env to git**
   ```bash
   # Check before committing
   git status
   # If .env appears, it's NOT in .gitignore!
   ```

3. **Never share API keys in code**
   - Don't paste keys in issues
   - Don't include keys in pull requests
   - Don't share keys in chat messages

4. **Never use production keys in development**
   - Use separate keys for dev/test/prod
   - Limit permissions on development keys

---

## Troubleshooting

### Issue 1: .env file not found

**Symptom**: `FileNotFoundError: .env`

**Solution**:
```bash
python3 setup_api_keys.py
```

### Issue 2: API keys not loading

**Symptom**: `None` or empty string when loading keys

**Solution**:
```bash
# 1. Check .env exists
ls -la .env

# 2. Check .env content
cat .env

# 3. Verify python-dotenv is installed
pip install python-dotenv

# 4. Re-run setup
python3 setup_api_keys.py
```

### Issue 3: .env appears in git status

**Symptom**: `git status` shows `.env` as untracked

**Solution**:
```bash
# 1. Check .gitignore
cat .gitignore | grep .env

# 2. If not there, add it
echo ".env" >> .gitignore

# 3. Remove from git if already tracked
git rm --cached .env

# 4. Commit .gitignore
git add .gitignore
git commit -m "Add .env to .gitignore"
```

### Issue 4: Permission denied on .env

**Symptom**: `PermissionError: [Errno 13] Permission denied: '.env'`

**Solution**:
```bash
# Fix permissions
chmod 600 .env

# Verify
ls -l .env
# Should show: -rw------- (owner read/write only)
```

### Issue 5: Keys still hardcoded in some files

**Symptom**: Found hardcoded keys in code

**Solution**:
```bash
# Run the replacement script
python3 replace_hardcoded_keys.py

# Verify no hardcoded keys remain
grep -r "YOUR_V98_API_KEY_HERE" . --exclude-dir=.git
```

---

## Security Checklist

Before pushing to GitHub, verify:

- [ ] `.env` file exists locally
- [ ] `.env` is in `.gitignore`
- [ ] `.env` does NOT appear in `git status`
- [ ] `.env.example` exists (safe template)
- [ ] No hardcoded API keys in code
- [ ] All code uses `os.getenv()` to load keys
- [ ] File permissions on `.env` are 600
- [ ] `setup_api_keys.py` tested and working
- [ ] Documentation updated

---

## Emergency Response

### If API Keys Are Exposed

1. **IMMEDIATE**: Revoke exposed keys
   - V98Store: Contact @v98dev on Telegram
   - AICoding: Visit https://aicoding.io.vn

2. **Get new API keys** from providers

3. **Update .env** with new keys
   ```bash
   python3 setup_api_keys.py
   ```

4. **Clean git history** (if keys were committed)
   ```bash
   # Use BFG Repo-Cleaner or git filter-branch
   # Contact security team for assistance
   ```

5. **Force push** cleaned repository
   ```bash
   git push --force
   ```

6. **Notify team** to pull latest changes

---

## Additional Resources

### Documentation
- [V98Store Docs](https://v98store.com/docs/introduction)
- [AICoding Docs](https://docs.aicoding.io.vn/)
- [Dive AI Setup Guide](./README.md)

### Support
- GitHub Issues: https://github.com/duclm1x1/Dive-Ai/issues
- Security: Report to repository maintainer

### Tools
- [git-secrets](https://github.com/awslabs/git-secrets) - Prevent committing secrets
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) - Remove secrets from history
- [pre-commit](https://pre-commit.com/) - Git hooks for security checks

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-02-05 | Complete security overhaul with .env system |
| 1.0 | 2026-02-04 | Initial version with hardcoded keys (deprecated) |

---

**Remember**: Security is everyone's responsibility. When in doubt, ask!

🔐 **Keep your API keys safe!**
