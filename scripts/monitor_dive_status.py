#!/usr/bin/env python3
"""
Small Dive AI Status Monitor
Quick check on Dive AI execution status
"""

import json
import time
from pathlib import Path
from datetime import datetime

def check_status():
    """Check Dive AI status"""
    status_file = Path("/home/ubuntu/Dive-Ai/dive_status.json")
    
    print("🔍 Dive AI Status Check")
    print("="*50)
    
    if status_file.exists():
        with open(status_file) as f:
            status = json.load(f)
        
        print(f"📊 Status: {status.get('status', 'Unknown')}")
        print(f"⏰ Last Update: {status.get('last_update', 'Never')}")
        print(f"🤖 Active Agents: {status.get('active_agents', 0)}")
        print(f"✅ Completed Tasks: {status.get('completed_tasks', 0)}")
        print(f"❌ Failed Tasks: {status.get('failed_tasks', 0)}")
        print(f"📈 Progress: {status.get('progress', 0)}%")
        
        if 'current_phase' in status:
            print(f"🔄 Current Phase: {status['current_phase']}")
        
        if 'message' in status:
            print(f"💬 Message: {status['message']}")
    else:
        print("⚠️  No status file found")
        print("Dive AI may not be running yet")
    
    print("="*50)

if __name__ == "__main__":
    check_status()
