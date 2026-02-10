"""
Dive AI Self-Aware Memory System
Tracks Dive AI's own development, changes, and evolution

This system makes Dive AI self-documenting by storing:
- All code changes and modifications
- Feature additions and removals
- Version history
- Development decisions
- Performance metrics
- Integration results
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

# Add skills path
skills_path = Path(__file__).parent.parent / "skills" / "dive-memory-v3" / "scripts"
sys.path.insert(0, str(skills_path))

from dive_memory import DiveMemory


class DiveAISelfMemory:
    """Self-aware memory system for Dive AI project tracking"""
    
    def __init__(self, project_root: Optional[str] = None, memory_db_path: Optional[str] = None):
        """Initialize self-aware memory system"""
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        
        # Use dedicated database for self-tracking
        if memory_db_path is None:
            memory_db_path = str(self.project_root / "data" / "dive_ai_self_memory.db")
        
        self.memory = DiveMemory(memory_db_path)
        self.memory.enable_context_injection()
        
        # Initialize project tracking
        self._init_project_tracking()
    
    def _init_project_tracking(self):
        """Initialize project tracking in memory"""
        # Check if project is already tracked
        results = self.memory.search("Dive AI project initialization", section="project", top_k=1)
        
        if not results:
            # First time - initialize project memory
            self.memory.add(
                content="Dive AI project initialization - Self-aware memory system activated",
                section="project",
                tags=["initialization", "project", "dive-ai"],
                importance=10,
                metadata={
                    "project_name": "Dive AI",
                    "version": "20.2.1",
                    "initialized_at": datetime.now().isoformat(),
                    "project_root": str(self.project_root)
                }
            )
    
    def track_code_change(self, file_path: str, change_type: str, 
                         description: str, details: Optional[Dict[str, Any]] = None):
        """Track code changes to Dive AI"""
        content = f"""Code Change: {change_type}
File: {file_path}
Description: {description}
Timestamp: {datetime.now().isoformat()}
"""
        
        if details:
            content += f"\nDetails:\n{json.dumps(details, indent=2)}"
        
        # Calculate file hash for tracking
        full_path = self.project_root / file_path
        file_hash = None
        if full_path.exists():
            with open(full_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
        
        metadata = {
            "file_path": file_path,
            "change_type": change_type,
            "file_hash": file_hash,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            metadata.update(details)
        
        tags = ["code-change", change_type, file_path.split('/')[-1].split('.')[0]]
        
        memory_id = self.memory.add(
            content=content,
            section="code-changes",
            tags=tags,
            importance=7,
            metadata=metadata
        )
        
        return memory_id
    
    def track_feature_addition(self, feature_name: str, description: str,
                              source: str, files_affected: List[str],
                              importance: int = 8):
        """Track new feature additions to Dive AI"""
        content = f"""Feature Addition: {feature_name}
Source: {source}
Description: {description}
Files Affected: {len(files_affected)}
Timestamp: {datetime.now().isoformat()}

Files:
{chr(10).join(f'  - {f}' for f in files_affected)}
"""
        
        metadata = {
            "feature_name": feature_name,
            "source": source,
            "files_affected": files_affected,
            "timestamp": datetime.now().isoformat(),
            "status": "added"
        }
        
        tags = ["feature", "addition", source, feature_name.lower().replace(' ', '-')]
        
        memory_id = self.memory.add(
            content=content,
            section="features",
            tags=tags,
            importance=importance,
            metadata=metadata
        )
        
        return memory_id
    
    def track_version_change(self, old_version: str, new_version: str,
                            changes: List[str], breaking_changes: Optional[List[str]] = None):
        """Track version changes"""
        content = f"""Version Change: {old_version} → {new_version}
Timestamp: {datetime.now().isoformat()}

Changes:
{chr(10).join(f'  - {c}' for c in changes)}
"""
        
        if breaking_changes:
            content += f"\n\nBreaking Changes:\n{chr(10).join(f'  - {c}' for c in breaking_changes)}"
        
        metadata = {
            "old_version": old_version,
            "new_version": new_version,
            "changes": changes,
            "breaking_changes": breaking_changes or [],
            "timestamp": datetime.now().isoformat()
        }
        
        tags = ["version", f"v{new_version}", "release"]
        
        memory_id = self.memory.add(
            content=content,
            section="versions",
            tags=tags,
            importance=10,
            metadata=metadata
        )
        
        return memory_id
    
    def track_integration(self, integration_name: str, source: str,
                         status: str, details: Dict[str, Any]):
        """Track integrations from other versions"""
        content = f"""Integration: {integration_name}
Source: {source}
Status: {status}
Timestamp: {datetime.now().isoformat()}

Details:
{json.dumps(details, indent=2)}
"""
        
        metadata = {
            "integration_name": integration_name,
            "source": source,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **details
        }
        
        tags = ["integration", source, status, integration_name.lower().replace(' ', '-')]
        
        importance = 9 if status == "success" else 7
        
        memory_id = self.memory.add(
            content=content,
            section="integrations",
            tags=tags,
            importance=importance,
            metadata=metadata
        )
        
        return memory_id
    
    def track_decision(self, decision: str, rationale: str,
                      alternatives: Optional[List[str]] = None,
                      impact: Optional[str] = None):
        """Track architectural and design decisions"""
        content = f"""Decision: {decision}
Timestamp: {datetime.now().isoformat()}

Rationale:
{rationale}
"""
        
        if alternatives:
            content += f"\n\nAlternatives Considered:\n{chr(10).join(f'  - {a}' for a in alternatives)}"
        
        if impact:
            content += f"\n\nExpected Impact:\n{impact}"
        
        metadata = {
            "decision": decision,
            "rationale": rationale,
            "alternatives": alternatives or [],
            "impact": impact,
            "timestamp": datetime.now().isoformat()
        }
        
        tags = ["decision", "architecture", "design"]
        
        memory_id = self.memory.add(
            content=content,
            section="decisions",
            tags=tags,
            importance=9,
            metadata=metadata
        )
        
        return memory_id
    
    def track_performance_metric(self, metric_name: str, value: float,
                                unit: str, context: Optional[str] = None):
        """Track performance metrics"""
        content = f"""Performance Metric: {metric_name}
Value: {value} {unit}
Timestamp: {datetime.now().isoformat()}
"""
        
        if context:
            content += f"\nContext: {context}"
        
        metadata = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        tags = ["performance", "metric", metric_name.lower().replace(' ', '-')]
        
        memory_id = self.memory.add(
            content=content,
            section="performance",
            tags=tags,
            importance=7,
            metadata=metadata
        )
        
        return memory_id
    
    def track_test_result(self, test_name: str, status: str,
                         duration: float, details: Optional[Dict[str, Any]] = None):
        """Track test results"""
        content = f"""Test: {test_name}
Status: {status}
Duration: {duration}s
Timestamp: {datetime.now().isoformat()}
"""
        
        if details:
            content += f"\nDetails:\n{json.dumps(details, indent=2)}"
        
        metadata = {
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            metadata.update(details)
        
        tags = ["test", status, test_name.lower().replace(' ', '-')]
        
        importance = 6 if status == "passed" else 8
        
        memory_id = self.memory.add(
            content=content,
            section="tests",
            tags=tags,
            importance=importance,
            metadata=metadata
        )
        
        return memory_id
    
    def query_history(self, query: str, section: Optional[str] = None,
                     top_k: int = 10) -> List[Dict[str, Any]]:
        """Query Dive AI's own history"""
        results = self.memory.search(
            query=query,
            section=section,
            top_k=top_k
        )
        
        return [
            {
                "content": r.content,
                "section": r.section,
                "tags": r.tags,
                "importance": r.importance,
                "metadata": r.metadata,
                "score": r.score,
                "created_at": r.created_at
            }
            for r in results
        ]
    
    def get_recent_changes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent changes to Dive AI"""
        results = self.memory.search(
            query="recent changes",
            section="code-changes",
            top_k=limit
        )
        
        return [
            {
                "file_path": r.metadata.get("file_path"),
                "change_type": r.metadata.get("change_type"),
                "timestamp": r.metadata.get("timestamp"),
                "description": r.content.split('\n')[2].replace('Description: ', '')
            }
            for r in results
        ]
    
    def get_feature_history(self) -> List[Dict[str, Any]]:
        """Get all features added to Dive AI"""
        results = self.memory.search(
            query="features",
            section="features",
            top_k=100
        )
        
        return [
            {
                "feature_name": r.metadata.get("feature_name"),
                "source": r.metadata.get("source"),
                "timestamp": r.metadata.get("timestamp"),
                "status": r.metadata.get("status"),
                "files_affected": r.metadata.get("files_affected", [])
            }
            for r in results
        ]
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get version history"""
        results = self.memory.search(
            query="version",
            section="versions",
            top_k=50
        )
        
        return [
            {
                "old_version": r.metadata.get("old_version"),
                "new_version": r.metadata.get("new_version"),
                "timestamp": r.metadata.get("timestamp"),
                "changes": r.metadata.get("changes", []),
                "breaking_changes": r.metadata.get("breaking_changes", [])
            }
            for r in results
        ]
    
    def check_before_modify(self, file_path: str) -> Dict[str, Any]:
        """Check what was done before modifying a file"""
        query = f"file:{file_path}"
        results = self.memory.search(
            query=query,
            section="code-changes",
            top_k=10
        )
        
        if not results:
            return {
                "has_history": False,
                "message": f"No previous modifications found for {file_path}",
                "history": []
            }
        
        history = [
            {
                "change_type": r.metadata.get("change_type"),
                "description": r.content.split('\n')[2].replace('Description: ', ''),
                "timestamp": r.metadata.get("timestamp"),
                "file_hash": r.metadata.get("file_hash")
            }
            for r in results
        ]
        
        return {
            "has_history": True,
            "message": f"Found {len(history)} previous modifications for {file_path}",
            "history": history,
            "latest": history[0] if history else None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Dive AI self-memory statistics"""
        stats = self.memory.get_stats()
        
        # Add section-specific stats
        sections = ["code-changes", "features", "versions", "integrations", 
                   "decisions", "performance", "tests"]
        
        section_stats = {}
        for section in sections:
            results = self.memory.search("", section=section, top_k=1000)
            section_stats[section] = len(results)
        
        return {
            **stats,
            "section_stats": section_stats,
            "project_root": str(self.project_root),
            "database_path": self.memory.db_path
        }
    
    def generate_changelog(self, since_version: Optional[str] = None) -> str:
        """Generate changelog from memory"""
        if since_version:
            query = f"version after {since_version}"
        else:
            query = "recent changes"
        
        changes = self.get_recent_changes(limit=50)
        features = self.get_feature_history()
        
        changelog = f"# Dive AI Changelog\n\n"
        changelog += f"Generated: {datetime.now().isoformat()}\n\n"
        
        if since_version:
            changelog += f"## Changes since v{since_version}\n\n"
        else:
            changelog += f"## Recent Changes\n\n"
        
        if features:
            changelog += "### Features Added\n\n"
            for feature in features[:10]:
                changelog += f"- **{feature['feature_name']}** (from {feature['source']})\n"
                changelog += f"  - {len(feature.get('files_affected', []))} files affected\n"
                changelog += f"  - Added: {feature['timestamp']}\n\n"
        
        if changes:
            changelog += "### Code Changes\n\n"
            for change in changes[:20]:
                changelog += f"- {change['change_type']}: `{change['file_path']}`\n"
                changelog += f"  - {change['description']}\n"
                changelog += f"  - {change['timestamp']}\n\n"
        
        return changelog


# Example usage
if __name__ == "__main__":
    # Initialize self-aware memory
    self_memory = DiveAISelfMemory()
    
    # Example: Track a code change
    self_memory.track_code_change(
        file_path="integration/dive_ai_self_memory.py",
        change_type="created",
        description="Created self-aware memory system for Dive AI",
        details={
            "purpose": "Track Dive AI's own development",
            "features": ["code tracking", "feature tracking", "version control"]
        }
    )
    
    # Example: Track a feature addition
    self_memory.track_feature_addition(
        feature_name="Self-Aware Memory System",
        description="Dive AI now tracks its own development and changes",
        source="V20.2.1",
        files_affected=["integration/dive_ai_self_memory.py"],
        importance=10
    )
    
    # Example: Check before modifying a file
    check_result = self_memory.check_before_modify("integration/dive_memory_integration.py")
    print(f"Check result: {json.dumps(check_result, indent=2)}")
    
    # Example: Get stats
    stats = self_memory.get_stats()
    print(f"\nSelf-memory stats: {json.dumps(stats, indent=2)}")
    
    # Example: Generate changelog
    changelog = self_memory.generate_changelog()
    print(f"\n{changelog}")
