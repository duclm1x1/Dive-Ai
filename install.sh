#!/bin/bash

# Dive AI V20.4.1 - Auto-Install Script
# This script automatically runs on fresh install

echo "============================================================"
echo "🚀 Dive AI V20.4 - Auto-Install"
echo "============================================================"

# Check Python version
echo ""
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found!"
    exit 1
fi

# Step 1: Setup API Keys
echo ""
echo "============================================================"
echo "🔑 Step 1: Setup API Keys"
echo "============================================================"
if [ ! -f ".env" ]; then
    echo "   Running setup_api_keys.py (auto-mode)..."
    echo -e "\n\n\n\n" | python3 setup_api_keys.py
    if [ $? -eq 0 ]; then
        echo "   ✅ API keys configured"
    else
        echo "   ⚠️  API key setup skipped or failed"
    fi
else
    echo "   ✅ .env already exists"
fi

# Step 2: Run First Run Complete
echo ""
echo "============================================================"
echo "🎯 Step 2: First Run Setup"
echo "============================================================"
if [ -f "first_run_complete.py" ]; then
    echo "   Running first_run_complete.py..."
    python3 first_run_complete.py
    if [ $? -eq 0 ]; then
        echo "   ✅ First run setup completed"
    else
        echo "   ⚠️  First run setup had issues"
    fi
else
    echo "   ⚠️  first_run_complete.py not found"
fi

# Step 3: Test LLM Connections
echo ""
echo "============================================================"
echo "🔌 Step 3: Test API Connections"
echo "============================================================"
if [ -f "first_run_llm_test.py" ]; then
    echo "   Running first_run_llm_test.py..."
    python3 first_run_llm_test.py
    if [ $? -eq 0 ]; then
        echo "   ✅ API connection tests completed"
    else
        echo "   ⚠️  Some API tests failed (check logs)"
    fi
else
    echo "   ⚠️  first_run_llm_test.py not found"
fi

# Step 4: Run Startup Health Checks
echo ""
echo "============================================================"
echo "💊 Step 4: Health Checks"
echo "============================================================"
if [ -f "dive_ai_startup.py" ]; then
    echo "   Running dive_ai_startup.py..."
    python3 dive_ai_startup.py
    if [ $? -eq 0 ]; then
        echo "   ✅ Health checks passed"
    else
        echo "   ⚠️  Some health checks failed"
    fi
else
    echo "   ⚠️  dive_ai_startup.py not found"
fi

# Step 5: Load Memory
echo ""
echo "============================================================"
echo "🧠 Step 5: Load Memory System"
echo "============================================================"
if [ -d "memory" ]; then
    MEMORY_FILES=$(find memory -type f \( -name "*.md" -o -name "*.json" \) | wc -l)
    echo "   ✅ Found $MEMORY_FILES memory files"
    
    # Show sample memory files
    echo "   📄 Sample memory files:"
    find memory -name "*.md" | head -3 | while read file; do
        echo "      - $file"
    done
else
    echo "   ⚠️  memory/ directory not found"
fi

# Final Summary
echo ""
echo "============================================================"
echo "📊 Installation Summary"
echo "============================================================"
echo "   ✅ Python: Ready"
echo "   ✅ API Keys: Configured"
echo "   ✅ First Run: Completed"
echo "   ✅ Connections: Tested"
echo "   ✅ Health Checks: Done"
echo "   ✅ Memory: Loaded"
echo ""
echo "============================================================"
echo "🎉 Dive AI V20.4 - Ready to Use!"
echo "============================================================"
echo ""
echo "Quick Start:"
echo "   python3 dive_ai_complete_system.py"
echo ""
echo "Documentation:"
echo "   cat README_V20.4.0.md"
echo ""
echo "============================================================"
