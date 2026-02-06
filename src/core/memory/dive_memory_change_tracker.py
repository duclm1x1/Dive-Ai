#!/usr/bin/env python3
"""
Dive Memory - Change Tracker & Notification System
Prevents memory chaos by tracking all changes (add/modify/delete)
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum


class ChangeType(Enum):
    """Types of changes"""
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    RENAMED = "RENAMED"


class ChangeCategory(Enum):
    """Categories of changes"""
    FEATURE = "FEATURE"
    BUGFIX = "BUGFIX"
    REFACTOR = "REFACTOR"
    DOCUMENTATION = "DOCUMENTATION"
    CONFIGURATION = "CONFIGURATION"
    DEPENDENCY = "DEPENDENCY"


class MemoryChangeTracker:
    """
    Tracks all changes in Dive Memory to prevent chaos
    
    Features:
    - Track add/modify/delete operations
    - Maintain change history
    - Generate notifications for AI
    - Prevent inconsistencies
    - Enable rollback
    """
    
    def __init__(self, memory_root: Path = None):
        """Initialize change tracker"""
        if memory_root is None:
            memory_root = Path(__file__).parent.parent / "memory"
        
        self.memory_root = Path(memory_root)
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
        # Change tracking directory
        self.tracking_dir = self.memory_root / "change_tracking"
        self.tracking_dir.mkdir(exist_ok=True)
        
        # Change log file
        self.change_log_file = self.tracking_dir / "CHANGE_LOG.json"
        self.change_log = self._load_change_log()
        
        # Notification queue
        self.notification_file = self.tracking_dir / "NOTIFICATIONS.json"
        self.notifications = self._load_notifications()
    
    def _load_change_log(self) -> List[Dict]:
        """Load change log from file"""
        if self.change_log_file.exists():
            with open(self.change_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_change_log(self):
        """Save change log to file"""
        with open(self.change_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.change_log, f, indent=2)
    
    def _load_notifications(self) -> List[Dict]:
        """Load notifications from file"""
        if self.notification_file.exists():
            with open(self.notification_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_notifications(self):
        """Save notifications to file"""
        with open(self.notification_file, 'w', encoding='utf-8') as f:
            json.dump(self.notifications, f, indent=2)
    
    def track_change(
        self,
        change_type: ChangeType,
        category: ChangeCategory,
        file_path: str,
        description: str,
        details: Dict = None,
        related_files: List[str] = None,
        breaking: bool = False
    ) -> Dict:
        """
        Track a change in memory
        
        Args:
            change_type: Type of change (ADDED/MODIFIED/DELETED)
            category: Category of change (FEATURE/BUGFIX/etc)
            file_path: Path to the changed file
            description: Human-readable description
            details: Additional details about the change
            related_files: List of related files affected
            breaking: Whether this is a breaking change
            
        Returns:
            Change record
        """
        timestamp = datetime.now().isoformat()
        
        change_record = {
            'id': len(self.change_log) + 1,
            'timestamp': timestamp,
            'change_type': change_type.value,
            'category': category.value,
            'file_path': file_path,
            'description': description,
            'details': details or {},
            'related_files': related_files or [],
            'breaking': breaking,
            'status': 'active'
        }
        
        # Add to change log
        self.change_log.append(change_record)
        self._save_change_log()
        
        # Create notification for AI
        self._create_notification(change_record)
        
        print(f"   📝 Change tracked: {change_type.value} - {file_path}")
        
        return change_record
    
    def _create_notification(self, change_record: Dict):
        """Create notification for AI to read"""
        notification = {
            'id': len(self.notifications) + 1,
            'timestamp': change_record['timestamp'],
            'priority': 'HIGH' if change_record['breaking'] else 'NORMAL',
            'message': self._generate_notification_message(change_record),
            'change_id': change_record['id'],
            'read': False,
            'acknowledged': False
        }
        
        self.notifications.append(notification)
        self._save_notifications()
    
    def _generate_notification_message(self, change_record: Dict) -> str:
        """Generate human-readable notification message"""
        change_type = change_record['change_type']
        category = change_record['category']
        file_path = change_record['file_path']
        description = change_record['description']
        
        message = f"[{change_type}] {category}: {file_path}\n"
        message += f"Description: {description}\n"
        
        if change_record['related_files']:
            message += f"Related Files: {', '.join(change_record['related_files'])}\n"
        
        if change_record['breaking']:
            message += "⚠️  BREAKING CHANGE - Review required!\n"
        
        return message
    
    def get_unread_notifications(self) -> List[Dict]:
        """Get all unread notifications for AI"""
        return [n for n in self.notifications if not n['read']]
    
    def mark_notification_read(self, notification_id: int):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                notification['read_at'] = datetime.now().isoformat()
                break
        self._save_notifications()
    
    def mark_notification_acknowledged(self, notification_id: int):
        """Mark notification as acknowledged (AI has processed it)"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['acknowledged'] = True
                notification['acknowledged_at'] = datetime.now().isoformat()
                break
        self._save_notifications()
    
    def get_changes_for_file(self, file_path: str) -> List[Dict]:
        """Get all changes for a specific file"""
        return [
            change for change in self.change_log
            if change['file_path'] == file_path and change['status'] == 'active'
        ]
    
    def get_changes_by_category(self, category: ChangeCategory) -> List[Dict]:
        """Get all changes in a category"""
        return [
            change for change in self.change_log
            if change['category'] == category.value and change['status'] == 'active'
        ]
    
    def get_breaking_changes(self) -> List[Dict]:
        """Get all breaking changes"""
        return [
            change for change in self.change_log
            if change['breaking'] and change['status'] == 'active'
        ]
    
    def get_recent_changes(self, limit: int = 10) -> List[Dict]:
        """Get recent changes"""
        return sorted(
            [c for c in self.change_log if c['status'] == 'active'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
    
    def find_related_changes(self, file_path: str) -> List[Dict]:
        """Find all changes related to a file"""
        related = []
        
        for change in self.change_log:
            if change['status'] != 'active':
                continue
            
            # Direct match
            if change['file_path'] == file_path:
                related.append(change)
            # In related files
            elif file_path in change.get('related_files', []):
                related.append(change)
        
        return related
    
    def generate_memory_status_report(self) -> str:
        """Generate comprehensive memory status report for AI"""
        lines = []
        lines.append("="*80)
        lines.append("📊 DIVE MEMORY STATUS REPORT")
        lines.append("="*80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary
        total_changes = len([c for c in self.change_log if c['status'] == 'active'])
        unread_notifications = len(self.get_unread_notifications())
        breaking_changes = len(self.get_breaking_changes())
        
        lines.append("📈 SUMMARY")
        lines.append(f"   Total Active Changes: {total_changes}")
        lines.append(f"   Unread Notifications: {unread_notifications}")
        lines.append(f"   Breaking Changes: {breaking_changes}")
        lines.append("")
        
        # Recent changes by category
        lines.append("📂 RECENT CHANGES BY CATEGORY")
        for category in ChangeCategory:
            changes = self.get_changes_by_category(category)
            if changes:
                lines.append(f"   {category.value}: {len(changes)} changes")
                for change in changes[:3]:
                    lines.append(f"      - {change['file_path']}: {change['description']}")
        lines.append("")
        
        # Breaking changes
        if breaking_changes > 0:
            lines.append("⚠️  BREAKING CHANGES")
            for change in self.get_breaking_changes()[:5]:
                lines.append(f"   - {change['file_path']}")
                lines.append(f"     {change['description']}")
                if change['related_files']:
                    lines.append(f"     Related: {', '.join(change['related_files'])}")
            lines.append("")
        
        # Unread notifications
        if unread_notifications > 0:
            lines.append("🔔 UNREAD NOTIFICATIONS")
            for notification in self.get_unread_notifications()[:5]:
                priority = notification['priority']
                icon = "🔴" if priority == "HIGH" else "🟡"
                lines.append(f"   {icon} [{priority}] Notification #{notification['id']}")
                lines.append(f"      {notification['message'].split(chr(10))[0]}")
            lines.append("")
        
        # File statistics
        lines.append("📊 FILE STATISTICS")
        file_changes = {}
        for change in self.change_log:
            if change['status'] == 'active':
                file_path = change['file_path']
                file_changes[file_path] = file_changes.get(file_path, 0) + 1
        
        most_changed = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:5]
        lines.append("   Most Changed Files:")
        for file_path, count in most_changed:
            lines.append(f"      - {file_path}: {count} changes")
        lines.append("")
        
        lines.append("="*80)
        lines.append("💡 RECOMMENDATIONS FOR AI")
        lines.append("="*80)
        
        # Generate recommendations
        if unread_notifications > 0:
            lines.append("   1. Read and acknowledge all unread notifications")
        
        if breaking_changes > 0:
            lines.append("   2. Review breaking changes and update dependent code")
        
        if total_changes > 50:
            lines.append("   3. Consider consolidating memory - too many active changes")
        
        lines.append("")
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def generate_ai_context_summary(self) -> str:
        """
        Generate concise summary for AI to understand current memory state
        This should be read at the start of every task
        """
        lines = []
        lines.append("🧠 DIVE MEMORY CONTEXT")
        lines.append("")
        
        # Recent changes
        recent = self.get_recent_changes(limit=5)
        if recent:
            lines.append("📝 Recent Changes (Last 5):")
            for change in recent:
                icon = {"ADDED": "➕", "MODIFIED": "✏️", "DELETED": "❌", "RENAMED": "🔄"}
                change_icon = icon.get(change['change_type'], "•")
                lines.append(f"   {change_icon} {change['file_path']}: {change['description']}")
        
        lines.append("")
        
        # Unread notifications
        unread = self.get_unread_notifications()
        if unread:
            lines.append(f"🔔 {len(unread)} Unread Notifications:")
            for notification in unread[:3]:
                priority_icon = "🔴" if notification['priority'] == "HIGH" else "🟡"
                lines.append(f"   {priority_icon} {notification['message'].split(chr(10))[0]}")
        
        lines.append("")
        
        # Breaking changes
        breaking = self.get_breaking_changes()
        if breaking:
            lines.append(f"⚠️  {len(breaking)} Breaking Changes Require Attention:")
            for change in breaking[:3]:
                lines.append(f"   - {change['file_path']}")
        
        return "\n".join(lines)
    
    def export_for_orchestrator(self) -> Dict:
        """
        Export memory state in format optimized for Dive Orchestrator
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_changes': len([c for c in self.change_log if c['status'] == 'active']),
                'unread_notifications': len(self.get_unread_notifications()),
                'breaking_changes': len(self.get_breaking_changes())
            },
            'recent_changes': self.get_recent_changes(limit=10),
            'unread_notifications': self.get_unread_notifications(),
            'breaking_changes': self.get_breaking_changes(),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations for AI"""
        recommendations = []
        
        unread = len(self.get_unread_notifications())
        if unread > 0:
            recommendations.append(f"Read {unread} unread notifications")
        
        breaking = len(self.get_breaking_changes())
        if breaking > 0:
            recommendations.append(f"Review {breaking} breaking changes")
        
        total = len([c for c in self.change_log if c['status'] == 'active'])
        if total > 50:
            recommendations.append("Consider memory consolidation")
        
        return recommendations


def main():
    """Test change tracker"""
    tracker = MemoryChangeTracker()
    
    # Test 1: Track a feature addition
    print("\n📊 TEST 1: Track Feature Addition")
    tracker.track_change(
        change_type=ChangeType.ADDED,
        category=ChangeCategory.FEATURE,
        file_path="core/dive_update_system.py",
        description="Added Dive Update System for intelligent code updates",
        details={
            'lines_added': 500,
            'functions_added': ['analyze_impact', 'apply_updates']
        },
        related_files=[
            'core/dive_dependency_tracker.py',
            'core/dive_impact_analyzer.py'
        ],
        breaking=False
    )
    
    # Test 2: Track a breaking change
    print("\n📊 TEST 2: Track Breaking Change")
    tracker.track_change(
        change_type=ChangeType.MODIFIED,
        category=ChangeCategory.REFACTOR,
        file_path="core/dive_memory_3file_complete.py",
        description="Changed memory API - now uses 3-file structure",
        details={
            'old_api': 'load_memory(project)',
            'new_api': 'load_project(project)'
        },
        related_files=[
            'core/dive_smart_orchestrator.py',
            'core/dive_smart_coder.py',
            'first_run_complete.py'
        ],
        breaking=True
    )
    
    # Test 3: Generate reports
    print("\n📊 TEST 3: Generate Reports")
    print(tracker.generate_ai_context_summary())
    print()
    print(tracker.generate_memory_status_report())
    
    # Test 4: Export for orchestrator
    print("\n📊 TEST 4: Export for Orchestrator")
    export = tracker.export_for_orchestrator()
    print(json.dumps(export, indent=2))


if __name__ == "__main__":
    main()
