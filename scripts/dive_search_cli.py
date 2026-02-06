#!/usr/bin/env python3
"""
Dive Search CLI - Command-line interface for Dive Search Engine

Usage:
    dive-search <query>                    # Basic search
    dive-search --source memory <query>    # Search specific source
    dive-search --breaking                 # Show breaking changes
    dive-search --deps <file>              # Show dependencies
    dive-search --impact <file>            # Analyze impact
"""

import os
import sys
import argparse
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from core.dive_search_engine import get_search_engine
from core.dive_update_search_enhanced import DiveUpdateSearchEnhanced
from core.dive_memory_search_enhanced import DiveMemorySearchEnhanced


def init_search_engine():
    """Initialize search engine"""
    project_root = Path(__file__).parent
    engine = get_search_engine(str(project_root))
    
    if not engine.ready:
        print("🔍 Initializing search engine...")
        engine.initialize(str(project_root))
    
    return engine


def cmd_search(args):
    """Execute search command"""
    engine = init_search_engine()
    
    # Build sources list
    sources = None
    if args.source:
        sources = [args.source]
    
    # Build filters
    filters = {}
    if args.breaking:
        filters = {'update': {'breaking': True}}
    if args.version:
        filters['update'] = filters.get('update', {})
        filters['update']['version'] = args.version
    if args.file_type:
        filters['file'] = {'file_type': args.file_type}
    
    # Search
    results = engine.search(
        query=args.query,
        sources=sources,
        filters=filters if filters else None,
        limit=args.limit
    )
    
    # Display results
    print(f"\n🔍 Search: '{args.query}'")
    print(f"Found {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result.source.upper()}] Score: {result.score}")
        
        if result.source == 'file':
            print(f"   File: {os.path.basename(result.data['file_path'])}")
            if result.data['classes']:
                print(f"   Classes: {', '.join(result.data['classes'][:3])}")
            if result.data['functions']:
                print(f"   Functions: {', '.join(result.data['functions'][:3])}")
        
        elif result.source == 'memory':
            print(f"   Section: {result.data['section_title']}")
            print(f"   Type: {result.data['file_type']}")
            print(f"   Preview: {result.data['content'][:100]}...")
        
        elif result.source == 'update':
            print(f"   Change: {result.data['description']}")
            print(f"   Type: {result.data['change_type']} | Category: {result.data['category']}")
            if result.data['breaking']:
                print(f"   ⚠️  BREAKING CHANGE")
        
        print()


def cmd_dependencies(args):
    """Show dependencies"""
    engine = init_search_engine()
    
    file_path = args.file
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n📊 Dependencies for: {os.path.basename(file_path)}\n")
    
    # Get dependencies
    if args.direction in ['deps', 'dependencies']:
        deps = engine.search_dependencies(file_path, direction='dependencies', transitive=args.transitive)
        print(f"Dependencies ({len(deps)}):")
        for dep in deps[:args.limit]:
            print(f"  → {os.path.basename(dep)}")
    
    elif args.direction in ['dependents', 'rdeps']:
        deps = engine.search_dependencies(file_path, direction='dependents', transitive=args.transitive)
        print(f"Dependents ({len(deps)}):")
        for dep in deps[:args.limit]:
            print(f"  ← {os.path.basename(dep)}")
    
    else:  # both
        deps_out = engine.search_dependencies(file_path, direction='dependencies')
        deps_in = engine.search_dependencies(file_path, direction='dependents')
        
        print(f"Dependencies ({len(deps_out)}):")
        for dep in deps_out[:args.limit]:
            print(f"  → {os.path.basename(dep)}")
        
        print(f"\nDependents ({len(deps_in)}):")
        for dep in deps_in[:args.limit]:
            print(f"  ← {os.path.basename(dep)}")


def cmd_impact(args):
    """Analyze impact"""
    update_system = DiveUpdateSearchEnhanced()
    
    file_path = args.file
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n📊 Impact Analysis: {os.path.basename(file_path)}\n")
    
    impact = update_system.analyze_impact(file_path, args.description or "")
    
    print(f"Is Core: {'Yes' if impact['is_core'] else 'No'}")
    print(f"Complexity: {impact['complexity']}")
    print(f"Impact Score: {impact['impact_score']}")
    print(f"\nDirect Dependents: {len(impact['dependents'])}")
    print(f"Transitive Dependents: {len(impact['transitive_dependents'])}")
    print(f"\nSafe Updates: {len(impact['safe_updates'])}")
    print(f"Complex Updates: {len(impact['complex_updates'])}")
    
    if impact['safe_updates']:
        print("\n✅ Safe to auto-update:")
        for update in impact['safe_updates'][:5]:
            print(f"  - {os.path.basename(update['file'])}")
    
    if impact['complex_updates']:
        print("\n⚠️  Requires manual review:")
        for update in impact['complex_updates'][:5]:
            print(f"  - {os.path.basename(update['file'])}: {update['reason']}")


def cmd_breaking(args):
    """Show breaking changes"""
    engine = init_search_engine()
    
    breaking = engine.get_breaking_changes(args.version)
    
    print(f"\n⚠️  Breaking Changes")
    if args.version:
        print(f"Version: {args.version}")
    print(f"Found: {len(breaking)}\n")
    
    for change in breaking[:args.limit]:
        print(f"• {change['description']}")
        print(f"  File: {os.path.basename(change['file_path'])}")
        print(f"  Type: {change['change_type']} | Category: {change['category']}")
        print(f"  Time: {change['timestamp']}")
        if change['affected_components']:
            print(f"  Affects: {', '.join(change['affected_components'])}")
        print()


def cmd_context(args):
    """Get relevant context"""
    memory = DiveMemorySearchEnhanced()
    
    # Load project
    if args.project:
        memory.load_project(args.project)
    else:
        memory.load_project("dive-ai")
    
    print(f"\n📖 Relevant Context for: '{args.query}'\n")
    
    context = memory.get_relevant_context(args.query, max_sections=args.sections)
    
    print(f"Context ({len(context)} chars):\n")
    print(context)


def cmd_stats(args):
    """Show statistics"""
    engine = init_search_engine()
    
    stats = engine.get_statistics()
    
    print("\n📊 Dive Search Engine Statistics\n")
    
    print("File Index:")
    for key, value in stats['file_index'].items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    print("\nMemory Index:")
    for key, value in stats['memory_index'].items():
        if isinstance(value, (list, dict)):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    
    print("\nUpdate Index:")
    for key, value in stats['update_index'].items():
        if isinstance(value, (list, dict)):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    
    print("\nDependency Graph:")
    for key, value in stats['dependency_graph'].items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Dive Search Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dive-search "orchestrator routing"
  dive-search --source memory "knowledge graph"
  dive-search --breaking --version 21.0
  dive-search --deps core/dive_memory.py
  dive-search --impact core/dive_memory.py
  dive-search --context "orchestrator routing"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command (default)
    search_parser = subparsers.add_parser('search', help='Search across all sources')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--source', choices=['file', 'memory', 'update'], help='Specific source')
    search_parser.add_argument('--breaking', action='store_true', help='Only breaking changes')
    search_parser.add_argument('--version', help='Filter by version')
    search_parser.add_argument('--file-type', help='Filter by file type')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # Dependencies command
    deps_parser = subparsers.add_parser('deps', help='Show dependencies')
    deps_parser.add_argument('file', help='File path')
    deps_parser.add_argument('--direction', choices=['deps', 'dependencies', 'dependents', 'rdeps', 'both'], 
                            default='both', help='Direction')
    deps_parser.add_argument('--transitive', action='store_true', help='Include transitive')
    deps_parser.add_argument('--limit', type=int, default=20, help='Max results')
    
    # Impact command
    impact_parser = subparsers.add_parser('impact', help='Analyze impact')
    impact_parser.add_argument('file', help='File path')
    impact_parser.add_argument('--description', help='Change description')
    
    # Breaking changes command
    breaking_parser = subparsers.add_parser('breaking', help='Show breaking changes')
    breaking_parser.add_argument('--version', help='Filter by version')
    breaking_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # Context command
    context_parser = subparsers.add_parser('context', help='Get relevant context')
    context_parser.add_argument('query', help='Query for context')
    context_parser.add_argument('--project', help='Project name')
    context_parser.add_argument('--sections', type=int, default=5, help='Max sections')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Parse args
    args = parser.parse_args()
    
    # If no command, treat first arg as search query
    if not args.command:
        if len(sys.argv) > 1:
            args.command = 'search'
            args.query = ' '.join(sys.argv[1:])
            args.source = None
            args.breaking = False
            args.version = None
            args.file_type = None
            args.limit = 10
        else:
            parser.print_help()
            return
    
    # Execute command
    try:
        if args.command == 'search':
            cmd_search(args)
        elif args.command == 'deps':
            cmd_dependencies(args)
        elif args.command == 'impact':
            cmd_impact(args)
        elif args.command == 'breaking':
            cmd_breaking(args)
        elif args.command == 'context':
            cmd_context(args)
        elif args.command == 'stats':
            cmd_stats(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
