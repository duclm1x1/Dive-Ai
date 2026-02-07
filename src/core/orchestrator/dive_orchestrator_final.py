#!/usr/bin/env python3
"""
Dive Orchestrator - Final Version

Uses complete 3-file memory system:
- Auto-loads all 3 files on startup
- Checks memory before every decision
- Saves decisions to memory
- Logs changes to CHANGELOG
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dive_memory_3file_complete import DiveMemory3FileComplete
from datetime import datetime
from typing import Dict, List, Optional


class DiveOrchestratorFinal:
    """
    Dive Orchestrator with Complete 3-File Memory System
    
    Responsibilities:
    - Auto-load memory on startup
    - Check memory before decisions
    - Make informed decisions
    - Save decisions to memory
    - Log changes to CHANGELOG
    """
    
    def __init__(self, project: Optional[str] = None):
        """
        Initialize orchestrator
        
        Args:
            project: Project name (auto-detected if not provided)
        """
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                   🧠 Dive Orchestrator - Final Version                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        self.memory = DiveMemory3FileComplete()
        self.project = project or "dive-ai"
        self.context = {}
        
        # Auto-load memory on startup
        self._auto_load_memory()
    
    def _auto_load_memory(self):
        """Auto-load all memory files on startup"""
        print(f"\n🔄 Auto-loading memory for project: {self.project}")
        print("="*80)
        
        # Load all 3 files
        self.context = self.memory.load_project(self.project)
        
        # Parse metadata from FULL file
        self._parse_metadata()
        
        print("="*80)
        print(f"✅ Memory loaded successfully!")
        print(f"   - FULL: {len(self.context.get('full', ''))} chars")
        print(f"   - CRITERIA: {len(self.context.get('criteria', ''))} chars")
        print(f"   - CHANGELOG: {len(self.context.get('changelog', ''))} chars")
        print("="*80 + "\n")
    
    def _parse_metadata(self):
        """Parse metadata from FULL file"""
        full_content = self.context.get('full', '')
        
        # Extract metadata
        import re
        
        version_match = re.search(r'version:\s*(.+)', full_content, re.IGNORECASE)
        status_match = re.search(r'status:\s*(.+)', full_content, re.IGNORECASE)
        
        self.metadata = {
            'version': version_match.group(1).strip() if version_match else 'Unknown',
            'status': status_match.group(1).strip() if status_match else 'Unknown'
        }
        
        print(f"   📊 Metadata: Version {self.metadata['version']}, Status: {self.metadata['status']}")
    
    def check_memory(self, query: str) -> Dict:
        """
        Check memory for relevant information
        
        Args:
            query: What to search for
            
        Returns:
            Dict with relevant information
        """
        print(f"\n🔍 Checking memory: {query}")
        
        results = {
            'full_knowledge': self.context.get('full', ''),
            'criteria': self.context.get('criteria', ''),
            'changelog': self.context.get('changelog', ''),
            'metadata': self.metadata
        }
        
        # Simple keyword search
        query_lower = query.lower()
        
        # Search in FULL
        full_matches = []
        for line in results['full_knowledge'].split('\n'):
            if query_lower in line.lower():
                full_matches.append(line.strip())
        
        # Search in CRITERIA
        criteria_matches = []
        for line in results['criteria'].split('\n'):
            if query_lower in line.lower():
                criteria_matches.append(line.strip())
        
        results['matches'] = {
            'full': full_matches[:5],  # Top 5
            'criteria': criteria_matches[:5]
        }
        
        print(f"   Found {len(full_matches)} matches in FULL")
        print(f"   Found {len(criteria_matches)} matches in CRITERIA")
        
        return results
    
    def make_decision(self, task: str, options: List[str]) -> Dict:
        """
        Make an informed decision
        
        Args:
            task: Task description
            options: List of options to choose from
            
        Returns:
            Decision dict with choice and rationale
        """
        print(f"\n🎯 Making decision for task: {task}")
        print(f"   Options: {options}")
        
        # Check memory for context
        memory_check = self.check_memory(task)
        
        # Simple decision logic (in real implementation, use LLM)
        print("\n   💭 Analyzing with memory context...")
        
        # For demo, choose first option
        decision = {
            'task': task,
            'options': options,
            'chosen': options[0] if options else None,
            'rationale': f"Based on memory context (Version {self.metadata['version']}), choosing {options[0] if options else 'None'}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'memory_used': {
                'full_matches': len(memory_check['matches']['full']),
                'criteria_matches': len(memory_check['matches']['criteria'])
            }
        }
        
        print(f"\n   ✅ Decision: {decision['chosen']}")
        print(f"   📝 Rationale: {decision['rationale']}")
        
        # Save decision to memory
        self._save_decision(decision)
        
        # Log to CHANGELOG
        self.memory.log_change(
            self.project,
            "Changed",
            f"Decision made: {task} → {decision['chosen']}"
        )
        
        return decision
    
    def _save_decision(self, decision: Dict):
        """Save decision to memory"""
        decision_text = f"""
## Decision: {decision['task']}

**Timestamp**: {decision['timestamp']}  
**Options Considered**: {', '.join(decision['options'])}  
**Chosen**: {decision['chosen']}  
**Rationale**: {decision['rationale']}

**Memory Context Used**:
- FULL matches: {decision['memory_used']['full_matches']}
- CRITERIA matches: {decision['memory_used']['criteria_matches']}

---
"""
        
        # Append to FULL file (History section)
        self.memory.save_full_knowledge(self.project, decision_text, append=True)
        print(f"   💾 Decision saved to memory")
    
    def get_context_summary(self) -> str:
        """Get summary of current context"""
        return f"""
Current Context for {self.project}:
- Version: {self.metadata['version']}
- Status: {self.metadata['status']}
- FULL knowledge: {len(self.context.get('full', ''))} chars
- CRITERIA: {len(self.context.get('criteria', ''))} chars
- CHANGELOG: {len(self.context.get('changelog', ''))} chars
"""


def main():
    """Demo: Orchestrator with 3-file system"""
    
    # Initialize orchestrator (auto-loads memory)
    orchestrator = DiveOrchestratorFinal("dive-ai")
    
    # Make a decision
    print("\n" + "="*80)
    decision = orchestrator.make_decision(
        task="Choose architecture for new feature",
        options=["Microservices", "Monolith", "Serverless"]
    )
    
    # Another decision
    print("\n" + "="*80)
    decision2 = orchestrator.make_decision(
        task="Select database for project",
        options=["PostgreSQL", "MongoDB", "SQLite"]
    )
    
    # Show context summary
    print("\n" + "="*80)
    print(orchestrator.get_context_summary())
    
    print("\n" + "="*80)
    print("✅ Orchestrator Demo Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
