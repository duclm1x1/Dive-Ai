#!/usr/bin/env python3
"""
Dive Coder - Final Version

Uses complete 3-file memory system:
- Checks memory before coding
- Executes with full context
- Saves results to memory
- Auto-logs all changes to CHANGELOG
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dive_memory_3file_complete import DiveMemory3FileComplete
from datetime import datetime
from typing import Dict, List, Optional


class DiveCoderFinal:
    """
    Dive Coder with Complete 3-File Memory System
    
    Responsibilities:
    - Check memory before coding
    - Execute with full context
    - Save results to memory
    - Auto-log changes to CHANGELOG
    """
    
    def __init__(self, project: Optional[str] = None):
        """
        Initialize coder
        
        Args:
            project: Project name
        """
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                     👨‍💻 Dive Coder - Final Version                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        self.memory = DiveMemory3FileComplete()
        self.project = project or "dive-ai"
        self.context = {}
        
        # Load memory
        self._load_memory()
    
    def _load_memory(self):
        """Load memory for context"""
        print(f"\n📚 Loading memory for project: {self.project}")
        print("="*80)
        
        self.context = self.memory.load_project(self.project)
        
        print("="*80)
        print(f"✅ Memory loaded!")
        print("="*80 + "\n")
    
    def check_previous_implementations(self, task: str) -> Dict:
        """
        Check memory for previous implementations
        
        Args:
            task: Task description
            
        Returns:
            Dict with previous implementations
        """
        print(f"\n🔍 Checking previous implementations: {task}")
        
        # Search in FULL and CRITERIA
        task_lower = task.lower()
        
        full_matches = []
        for line in self.context.get('full', '').split('\n'):
            if any(word in line.lower() for word in task_lower.split()):
                full_matches.append(line.strip())
        
        criteria_matches = []
        for line in self.context.get('criteria', '').split('\n'):
            if any(word in line.lower() for word in task_lower.split()):
                criteria_matches.append(line.strip())
        
        # Check CHANGELOG for similar work
        changelog_matches = []
        for line in self.context.get('changelog', '').split('\n'):
            if any(word in line.lower() for word in task_lower.split()):
                changelog_matches.append(line.strip())
        
        results = {
            'full_matches': full_matches[:5],
            'criteria_matches': criteria_matches[:5],
            'changelog_matches': changelog_matches[:5]
        }
        
        print(f"   Found {len(full_matches)} matches in FULL")
        print(f"   Found {len(criteria_matches)} matches in CRITERIA")
        print(f"   Found {len(changelog_matches)} matches in CHANGELOG")
        
        return results
    
    def execute(self, task: str, code: Optional[str] = None) -> Dict:
        """
        Execute task with full context
        
        Args:
            task: Task description
            code: Code to execute (optional, for demo)
            
        Returns:
            Execution result
        """
        print(f"\n⚙️  Executing task: {task}")
        
        # Check previous implementations
        previous = self.check_previous_implementations(task)
        
        # Execute (simulated for demo)
        print("\n   💻 Coding with full context...")
        
        result = {
            'task': task,
            'code': code or f"# Code for: {task}\\npass",
            'status': 'success',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'context_used': {
                'full_matches': len(previous['full_matches']),
                'criteria_matches': len(previous['criteria_matches']),
                'changelog_matches': len(previous['changelog_matches'])
            }
        }
        
        print(f"\n   ✅ Execution complete!")
        print(f"   📊 Used {result['context_used']['full_matches']} FULL matches")
        print(f"   📊 Used {result['context_used']['criteria_matches']} CRITERIA matches")
        print(f"   📊 Used {result['context_used']['changelog_matches']} CHANGELOG matches")
        
        # Save result to memory
        self._save_result(result)
        
        # Auto-log to CHANGELOG
        self._auto_log_change(result)
        
        return result
    
    def _save_result(self, result: Dict):
        """Save execution result to memory"""
        result_text = f"""
## Execution: {result['task']}

**Timestamp**: {result['timestamp']}  
**Status**: {result['status']}

**Code**:
```python
{result['code']}
```

**Context Used**:
- FULL matches: {result['context_used']['full_matches']}
- CRITERIA matches: {result['context_used']['criteria_matches']}
- CHANGELOG matches: {result['context_used']['changelog_matches']}

---
"""
        
        # Append to FULL file
        self.memory.save_full_knowledge(self.project, result_text, append=True)
        print(f"   💾 Result saved to memory")
    
    def _auto_log_change(self, result: Dict):
        """Auto-log change to CHANGELOG"""
        # Determine change type based on task
        task_lower = result['task'].lower()
        
        if any(word in task_lower for word in ['add', 'create', 'implement', 'new']):
            change_type = "Added"
        elif any(word in task_lower for word in ['fix', 'bug', 'error', 'issue']):
            change_type = "Fixed"
        elif any(word in task_lower for word in ['update', 'modify', 'change', 'improve']):
            change_type = "Changed"
        elif any(word in task_lower for word in ['remove', 'delete', 'deprecate']):
            change_type = "Removed"
        else:
            change_type = "Changed"
        
        self.memory.log_change(
            self.project,
            change_type,
            f"{result['task']} (Status: {result['status']})"
        )
        
        print(f"   📝 Auto-logged to CHANGELOG: [{change_type}] {result['task']}")


def main():
    """Demo: Coder with 3-file system"""
    
    # Initialize coder
    coder = DiveCoderFinal("dive-ai")
    
    # Execute tasks
    print("\n" + "="*80)
    result1 = coder.execute(
        task="Implement user authentication",
        code="""
def authenticate(username, password):
    # Check credentials
    if verify_credentials(username, password):
        return create_session(username)
    return None
"""
    )
    
    print("\n" + "="*80)
    result2 = coder.execute(
        task="Fix memory leak in data processor",
        code="""
def process_data(data):
    # Fixed: Clear cache after processing
    result = transform(data)
    cache.clear()
    return result
"""
    )
    
    print("\n" + "="*80)
    result3 = coder.execute(
        task="Add logging to API endpoints",
        code="""
@app.route('/api/endpoint')
def endpoint():
    logger.info('Endpoint called')
    result = process_request()
    logger.info('Endpoint completed')
    return result
"""
    )
    
    print("\n" + "="*80)
    print("✅ Coder Demo Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
