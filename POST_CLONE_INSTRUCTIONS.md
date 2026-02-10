# Dive AI - Post-Clone Instructions

After cloning this repository, run:

```bash
./install.sh
```

This will automatically:
1. ✅ Setup API keys
2. ✅ Run first-run setup
3. ✅ Test API connections
4. ✅ Run health checks
5. ✅ Load memory system

## Manual Installation

If you prefer manual setup:

```bash
# 1. Setup API keys
python3 setup_api_keys.py

# 2. First run
python3 first_run_complete.py

# 3. Test connections
python3 first_run_llm_test.py

# 4. Health checks
python3 dive_ai_startup.py

# 5. Start using
python3 dive_ai_complete_system.py
```

## Quick Start

```bash
python3 dive_ai_complete_system.py
```

See README_V20.4.0.md for complete documentation.
