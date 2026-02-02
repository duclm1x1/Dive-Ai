#!/usr/bin/env python3
import sys
import os
import argparse
import json
from pathlib import Path

# Fix path to include src to allow imports from infrastructure/
root_dir = Path(__file__).parent.absolute()
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "infrastructure"))

from infrastructure.orchestrator.orchestrator import DiveOrchestratorV19_3, OrchestratorConfigV19_3

__version__ = "19.5"
__codename__ = "The Enhanced One"

def main():
    parser = argparse.ArgumentParser(description=f"Dive Coder V{__version__} - {__codename__}")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check system status')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process a request')
    process_parser.add_argument('--prompt', required=True, help='User prompt/goal')
    process_parser.add_argument('--scale', default='small', choices=['small', 'medium', 'large'], help='Fleet scale')

    args = parser.parse_args()

    if args.command == 'status':
        coder = DiveOrchestratorV19_3()
        status = {
            "version": __version__,
            "codename": __codename__,
            "agents": len(coder.agents),
            "total_capabilities": coder.get_total_capabilities(),
            "skills": 29,
            "api_configured": bool(coder.api_key and coder.api_base)
        }
        print(json.dumps(status, indent=2))
        return

    if args.command == 'process':
        coder = DiveOrchestratorV19_3()
        print(f"🚀 Dive Coder V{__version__} starting...")
        print(f"Scale: {args.scale}")
        result = coder.process_prompt(args.prompt)
        print("\n" + "="*60)
        print("FINAL RESULT")
        print("="*60)
        # Save output
        output_file = Path("output_v19_5.py")
        with open(output_file, "w") as f:
            f.write(result["codebase"])
        print(f"Code saved to: {output_file}")
        print(f"Project ID: {result['project_id']}")
        return

    if not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
