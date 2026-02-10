#!/usr/bin/env python3
"""
Dive Update CLI
Command-line interface for Dive Update System
"""

import sys
import argparse
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from dive_update_memory_integration import DiveUpdateMemoryIntegration


def cmd_analyze(args):
    """Analyze impact of changes"""
    integration = DiveUpdateMemoryIntegration()
    
    result = integration.track_change_and_update(
        changed_files=args.files,
        new_version=args.version,
        breaking=args.breaking,
        description=args.description or "",
        auto_apply=False,  # Only analyze, don't apply
        dry_run=True
    )
    
    print(f"\n{'='*80}")
    print("📊 ANALYSIS SUMMARY")
    print(f"{'='*80}")
    print(f"   Total Affected Files: {result['total_affected']}")
    print(f"   Manual Review Required: {result['manual_review']}")
    print(f"\n✅ Analysis complete. Check memory/updates/ for detailed reports.")


def cmd_update(args):
    """Analyze and apply updates"""
    integration = DiveUpdateMemoryIntegration()
    
    result = integration.track_change_and_update(
        changed_files=args.files,
        new_version=args.version,
        breaking=args.breaking,
        description=args.description or "",
        auto_apply=True,
        dry_run=args.dry_run
    )
    
    print(f"\n{'='*80}")
    print("📊 UPDATE SUMMARY")
    print(f"{'='*80}")
    print(f"   Total Affected Files: {result['total_affected']}")
    print(f"   Auto-Applied: {result['auto_applied']}")
    print(f"   Manual Review Required: {result['manual_review']}")
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN - No files were actually modified")
    else:
        print(f"\n✅ Updates applied successfully")


def cmd_breakthrough(args):
    """Handle version breakthrough"""
    integration = DiveUpdateMemoryIntegration()
    
    major_changes = args.changes.split(',') if args.changes else []
    
    result = integration.version_breakthrough(
        from_version=args.from_version,
        to_version=args.to_version,
        major_changes=major_changes,
        auto_apply=not args.no_auto,
        dry_run=args.dry_run
    )
    
    print(f"\n{'='*80}")
    print("🚀 BREAKTHROUGH SUMMARY")
    print(f"{'='*80}")
    print(f"   Version: {args.from_version} → {args.to_version}")
    print(f"   Total Affected Files: {result['total_affected']}")
    print(f"   Auto-Applied: {result['auto_applied']}")
    print(f"   Manual Review Required: {result['manual_review']}")
    
    if args.dry_run:
        print(f"\n🔍 DRY RUN - No files were actually modified")
    else:
        print(f"\n✅ Breakthrough complete")


def cmd_scan(args):
    """Scan project and build dependency graph"""
    integration = DiveUpdateMemoryIntegration()
    
    result = integration.update_system.scan_and_track()
    
    print(f"\n{'='*80}")
    print("📊 SCAN SUMMARY")
    print(f"{'='*80}")
    print(f"   Total Files: {result['total_files']}")
    print(f"   Graph Nodes: {result['graph_nodes']}")
    print(f"   Graph Edges: {result['graph_edges']}")
    print(f"\n✅ Dependency graph saved to memory/file_tracking/")


def cmd_history(args):
    """Show update history"""
    integration = DiveUpdateMemoryIntegration()
    
    history = integration.get_update_history(limit=args.limit)
    
    print(f"\n{'='*80}")
    print("📜 UPDATE HISTORY")
    print(f"{'='*80}\n")
    
    for entry in history:
        print(f"   {entry.get('title', 'Unknown')}")
        if args.verbose and 'content' in entry:
            for line in entry['content'][:5]:  # Show first 5 lines
                print(f"      {line}")
        print()
    
    print(f"✅ Showing {len(history)} most recent updates")


def main():
    parser = argparse.ArgumentParser(
        description="Dive Update System - Intelligent code update management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze impact of changes
  python3 dive_update_cli.py analyze -f core/dive_memory.py -v 21.0.0
  
  # Analyze and apply updates
  python3 dive_update_cli.py update -f first_run_complete.py -v 21.0.0 --breaking
  
  # Version breakthrough
  python3 dive_update_cli.py breakthrough --from 20.4.1 --to 21.0.0 \\
      --changes "New memory system,Knowledge graph,Enhanced workflow"
  
  # Scan project dependencies
  python3 dive_update_cli.py scan
  
  # Show update history
  python3 dive_update_cli.py history --limit 10
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Analyze impact of changes')
    parser_analyze.add_argument('-f', '--files', nargs='+', required=True,
                               help='Files that were changed')
    parser_analyze.add_argument('-v', '--version', required=True,
                               help='New version number')
    parser_analyze.add_argument('-b', '--breaking', action='store_true',
                               help='Mark as breaking change')
    parser_analyze.add_argument('-d', '--description',
                               help='Description of changes')
    parser_analyze.set_defaults(func=cmd_analyze)
    
    # Update command
    parser_update = subparsers.add_parser('update', help='Analyze and apply updates')
    parser_update.add_argument('-f', '--files', nargs='+', required=True,
                              help='Files that were changed')
    parser_update.add_argument('-v', '--version', required=True,
                              help='New version number')
    parser_update.add_argument('-b', '--breaking', action='store_true',
                              help='Mark as breaking change')
    parser_update.add_argument('-d', '--description',
                              help='Description of changes')
    parser_update.add_argument('--dry-run', action='store_true',
                              help='Preview changes without applying')
    parser_update.set_defaults(func=cmd_update)
    
    # Breakthrough command
    parser_breakthrough = subparsers.add_parser('breakthrough',
                                               help='Handle version breakthrough')
    parser_breakthrough.add_argument('--from', dest='from_version', required=True,
                                    help='Previous version')
    parser_breakthrough.add_argument('--to', dest='to_version', required=True,
                                    help='New version')
    parser_breakthrough.add_argument('-c', '--changes',
                                    help='Comma-separated list of major changes')
    parser_breakthrough.add_argument('--no-auto', action='store_true',
                                    help='Disable auto-apply')
    parser_breakthrough.add_argument('--dry-run', action='store_true',
                                    help='Preview changes without applying')
    parser_breakthrough.set_defaults(func=cmd_breakthrough)
    
    # Scan command
    parser_scan = subparsers.add_parser('scan', help='Scan project dependencies')
    parser_scan.set_defaults(func=cmd_scan)
    
    # History command
    parser_history = subparsers.add_parser('history', help='Show update history')
    parser_history.add_argument('-l', '--limit', type=int, default=10,
                               help='Number of entries to show')
    parser_history.add_argument('-v', '--verbose', action='store_true',
                               help='Show detailed information')
    parser_history.set_defaults(func=cmd_history)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
