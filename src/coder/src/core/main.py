#!/usr/bin/env python3
"""
Dive Coder v19.3 - Main Entry Point

Usage:
    python main.py --prompt "Your project description"
    python main.py --prompt "Your project description" --scale medium
    python main.py --prompt "Your project description" --scale large

Features:
    - 8 Identical Dive Coder instances (multiplied x8, x16, x36)
    - 25 Skills (10 original + 15 new LLM innovations)
    - All skills always-on and integrated
"""

import sys
import argparse
from orchestrator.orchestrator import DiveOrchestratorV19_3
from replication.replication_manager import ScaleLevel


def main():
    parser = argparse.ArgumentParser(description="Dive Coder v19.3 - Autonomous Software Development Platform with 15 LLM Innovations")
    parser.add_argument("--prompt", type=str, required=True, help="High-level project description")
    parser.add_argument("--scale", type=str, default="small", choices=["small", "medium", "large"],
                       help="Fleet size: small (8 DiveCoder x8), medium (16 DiveCoder x16), large (36 DiveCoder x36)")
    parser.add_argument("--output", type=str, default="output.py", help="Output file for generated code")
    
    args = parser.parse_args()
    
    # Map scale to ScaleLevel
    scale_map = {
        "small": ScaleLevel.SMALL,
        "medium": ScaleLevel.MEDIUM,
        "large": ScaleLevel.LARGE,
    }
    
    print("\n" + "="*70)
    print("DIVE CODER v19.3 - Autonomous Software Development Platform")
    print("With 15 LLM Core Innovations - All Skills Always-On")
    print("="*70)
    print(f"Prompt: {args.prompt}")
    print(f"Scale: {args.scale} (Dive Coder x{scale_map[args.scale].value} instances)")
    print("="*70 + "\n")
    
    # Create orchestrator and process prompt
    orchestrator = DiveOrchestratorV19_3()
    result = orchestrator.process_prompt(args.prompt)
    
    # Save output
    with open(args.output, "w") as f:
        f.write(result["codebase"])
    
    print("\n" + "="*70)
    print("PROJECT SUMMARY - Dive Coder v19.3")
    print("="*70)
    print(f"Status: {result['status']}")
    print(f"Tasks: {result['task_count']}")
    print(f"Dive Coder Instances: {result['agent_team_size']}")
    print(f"Fleet Size: {result['fleet_size']} (multiplied)")
    print(f"Output: {args.output}")
    print(f"Skills Active: 25 (10 original + 15 new innovations)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
