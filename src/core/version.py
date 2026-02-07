#!/usr/bin/env python3
"""
Dive AI Version Manager

Manages version information and changelog
"""

import os
from pathlib import Path
from typing import Tuple

# Version information
MAJOR = 20
MINOR = 3
PATCH = 0

VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
VERSION_INFO = (MAJOR, MINOR, PATCH)

# Version history
VERSION_HISTORY = {
    "20.3.0": {
        "date": "2026-02-05",
        "type": "feature",
        "features": [
            "Smart Orchestrator with 7-phase intelligent prompt processing",
            "Intent detection and task decomposition",
            "Multi-model routing (Claude Opus/Sonnet, GPT Codex, Gemini)",
            "Interrupt handling with quick analysis (< 100ms)",
            "Adaptive execution (merge/pause/resume)",
            "Context merging for user interrupts",
            "Event stream management"
        ],
        "improvements": [
            "Intelligent task prioritization",
            "Parallel execution planning",
            "Memory-aware decision making"
        ]
    },
    "20.2.1": {
        "date": "2026-02-04",
        "type": "feature",
        "features": [
            "3-file memory system (FULL, CRITERIA, CHANGELOG)",
            "Auto-loading memory on startup",
            "Doc-first workflow implementation",
            "Enhanced security with .env system"
        ]
    },
    "20.2.0": {
        "date": "2026-02-03",
        "type": "major",
        "features": [
            "Dive Memory V3 (13.9x faster)",
            "128 specialized agents",
            "20+ specialized skills",
            "Memory Loop architecture"
        ]
    }
}

def get_version() -> str:
    """Get current version string"""
    return VERSION

def get_version_info() -> Tuple[int, int, int]:
    """Get version tuple"""
    return VERSION_INFO

def get_version_file_path() -> Path:
    """Get path to VERSION file"""
    return Path(__file__).parent.parent / "VERSION"

def read_version_file() -> str:
    """Read version from VERSION file"""
    version_file = get_version_file_path()
    if version_file.exists():
        return version_file.read_text().strip()
    return VERSION

def write_version_file(version: str):
    """Write version to VERSION file"""
    version_file = get_version_file_path()
    version_file.write_text(f"{version}\n")

def get_changelog(version: str = None) -> dict:
    """Get changelog for specific version or current"""
    if version is None:
        version = VERSION
    return VERSION_HISTORY.get(version, {})

def get_all_versions() -> list:
    """Get list of all versions"""
    return list(VERSION_HISTORY.keys())

def print_version_info():
    """Print version information"""
    print(f"Dive AI v{VERSION}")
    print(f"Version Info: {VERSION_INFO}")
    
    changelog = get_changelog()
    if changelog:
        print(f"\nRelease Date: {changelog.get('date', 'Unknown')}")
        print(f"Type: {changelog.get('type', 'Unknown')}")
        
        if 'features' in changelog:
            print("\nNew Features:")
            for feature in changelog['features']:
                print(f"  • {feature}")
        
        if 'improvements' in changelog:
            print("\nImprovements:")
            for improvement in changelog['improvements']:
                print(f"  • {improvement}")

if __name__ == "__main__":
    print_version_info()
