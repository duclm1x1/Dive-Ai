#!/usr/bin/env python3
"""
Replace hardcoded API keys with environment variable loading
"""

import os
import re
from pathlib import Path

# API keys to replace
KEYS_TO_REPLACE = {
    "sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y": ("V98API_KEY", "V98API"),
    "sk-dev-0kgTls1jmGOn3K4Fdl7Rdudkl7QSCJCk": ("AICODING_API_KEY", "AICoding"),
}

# Code template for environment variable loading
ENV_LOAD_TEMPLATE = '''import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()'''

def should_process_file(file_path):
    """Check if file should be processed"""
    # Skip certain directories
    skip_dirs = {'.git', '__pycache__', 'venv', 'env', 'node_modules', '.venv'}
    if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
        return False
    
    # Only process Python files and JSON files
    if file_path.suffix not in {'.py', '.json'}:
        return False
    
    # Skip this script itself
    if file_path.name == 'replace_hardcoded_keys.py':
        return False
    
    return True

def replace_in_python_file(file_path, content):
    """Replace hardcoded keys in Python files"""
    original_content = content
    changes = []
    
    # Check if file has hardcoded keys
    has_keys = any(key in content for key in KEYS_TO_REPLACE.keys())
    
    if not has_keys:
        return content, changes
    
    # Add dotenv import if not present
    if 'from dotenv import load_dotenv' not in content:
        # Find the first import statement
        import_match = re.search(r'^import\s+\w+', content, re.MULTILINE)
        if import_match:
            insert_pos = import_match.start()
            content = content[:insert_pos] + ENV_LOAD_TEMPLATE + '\n\n' + content[insert_pos:]
            changes.append("Added dotenv import")
    
    # Replace hardcoded keys with os.getenv()
    for key, (env_var, provider) in KEYS_TO_REPLACE.items():
        if key in content:
            # Replace in various contexts
            patterns = [
                (f'"{key}"', f'os.getenv("{env_var}", "{key}")'),
                (f"'{key}'", f'os.getenv("{env_var}", "{key}")'),
                (f'api_key = "{key}"', f'api_key = os.getenv("{env_var}", "{key}")'),
                (f"api_key = '{key}'", f'api_key = os.getenv("{env_var}", "{key}")'),
                (f'self.api_key = "{key}"', f'self.api_key = os.getenv("{env_var}", "{key}")'),
                (f"self.api_key = '{key}'", f'self.api_key = os.getenv("{env_var}", "{key}")'),
                (f'self.v98api_key = "{key}"', f'self.v98api_key = os.getenv("{env_var}", "{key}")'),
                (f"self.v98api_key = '{key}'", f'self.v98api_key = os.getenv("{env_var}", "{key}")'),
                (f'self.aicoding_key = "{key}"', f'self.aicoding_key = os.getenv("{env_var}", "{key}")'),
                (f"self.aicoding_key = '{key}'", f'self.aicoding_key = os.getenv("{env_var}", "{key}")'),
            ]
            
            for old_pattern, new_pattern in patterns:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    changes.append(f"Replaced {provider} key with env var")
    
    return content, changes

def replace_in_json_file(file_path, content):
    """Replace hardcoded keys in JSON files"""
    changes = []
    
    # For JSON files, replace keys with placeholder
    for key, (env_var, provider) in KEYS_TO_REPLACE.items():
        if key in content:
            content = content.replace(key, f"${{ENV:{env_var}}}")
            changes.append(f"Replaced {provider} key with env placeholder")
    
    return content, changes

def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        if file_path.suffix == '.py':
            content, changes = replace_in_python_file(file_path, content)
        elif file_path.suffix == '.json':
            content, changes = replace_in_json_file(file_path, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        
        return False, []
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False, []

def main():
    """Main function"""
    print("=" * 70)
    print("🔒 REPLACING HARDCODED API KEYS")
    print("=" * 70)
    print()
    
    root_path = Path('.')
    files_processed = 0
    files_updated = 0
    
    # Find all files
    all_files = list(root_path.rglob('*'))
    python_files = [f for f in all_files if should_process_file(f)]
    
    print(f"Found {len(python_files)} files to check")
    print()
    
    for file_path in python_files:
        updated, changes = process_file(file_path)
        files_processed += 1
        
        if updated:
            files_updated += 1
            print(f"✅ Updated: {file_path}")
            for change in changes:
                print(f"   - {change}")
    
    print()
    print("=" * 70)
    print(f"SUMMARY: Processed {files_processed} files, updated {files_updated} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
