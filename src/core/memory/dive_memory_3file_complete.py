#!/usr/bin/env python3
"""
Dive Memory - Complete 3-File System

Each project has exactly 3 files:
1. {PROJECT}_FULL.md - All knowledge (with metadata)
2. {PROJECT}_CRITERIA.md - Execution guidelines (with examples, decision tree, known issues)
3. {PROJECT}_CHANGELOG.md - Change history

This is the complete, production-ready memory system.
"""

import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import re
import json


class DiveMemory3FileComplete:
    """
    Complete 3-File Memory System
    
    Each project gets exactly 3 files:
    - {PROJECT}_FULL.md: Complete knowledge with metadata
    - {PROJECT}_CRITERIA.md: Enhanced execution guidelines
    - {PROJECT}_CHANGELOG.md: Change tracking
    """
    
    def __init__(self, memory_root: Optional[Path] = None):
        """Initialize 3-file system"""
        if memory_root is None:
            memory_root = Path(__file__).parent.parent / "memory"
        
        self.memory_root = Path(memory_root)
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
        self.current_project = None
        self.loaded_projects = {}
    
    def detect_project(self, context: str) -> str:
        """Auto-detect project from context"""
        patterns = [
            r"(?:working on|project|building|developing)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:project|app|system)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                project_name = match.group(1).strip()
                return self._normalize_project_name(project_name)
        
        cwd = Path.cwd().name
        if cwd and cwd != "Dive-Ai":
            return self._normalize_project_name(cwd)
        
        return "dive-ai"
    
    def _normalize_project_name(self, name: str) -> str:
        """Normalize project name to kebab-case"""
        normalized = name.lower().strip()
        normalized = re.sub(r'\s+', '-', normalized)
        normalized = re.sub(r'[^a-z0-9-]', '', normalized)
        return normalized
    
    def get_project_files(self, project: str) -> Dict[str, Path]:
        """Get the 3 files for a project"""
        project_upper = project.upper().replace('-', '_')
        
        return {
            'full': self.memory_root / f"{project_upper}_FULL.md",
            'criteria': self.memory_root / f"{project_upper}_CRITERIA.md",
            'changelog': self.memory_root / f"{project_upper}_CHANGELOG.md"
        }
    
    def load_project(self, project: str) -> Dict[str, str]:
        """Load all 3 files for a project"""
        files = self.get_project_files(project)
        
        content = {
            'full': '',
            'criteria': '',
            'changelog': ''
        }
        
        for key, file_path in files.items():
            if file_path.exists():
                content[key] = file_path.read_text()
                print(f"   📄 Loaded {file_path.name} ({len(content[key])} chars)")
            else:
                print(f"   ⚠️  {file_path.name} not found (will be created)")
        
        self.loaded_projects[project] = content
        self.current_project = project
        
        return content
    
    def create_full_template(self, project: str, description: str = "", 
                            version: str = "1.0", status: str = "Development",
                            dependencies: List[str] = None) -> str:
        """Create enhanced FULL template with metadata"""
        project_title = project.replace('-', ' ').title()
        deps = dependencies or []
        
        template = f"""---
project: {project_title}
version: {version}
status: {status}
created: {datetime.now().strftime("%Y-%m-%d")}
last_updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
dependencies: {json.dumps(deps)}
---

# {project_title} - Complete Knowledge

**Project**: {project_title}  
**Version**: {version}  
**Status**: {status}  
**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Overview

{description if description else f"Complete knowledge base for {project_title} project."}

---

## What It Is

### Purpose
[What problem does this project solve?]

### Target Users
[Who will use this?]

### Key Value Proposition
[Why is this valuable?]

---

## How It Works

### High-Level Flow
1. Step 1
2. Step 2
3. Step 3

### Architecture

#### System Architecture
```
[ASCII diagram or description]
```

#### Components
- **Component 1**: Purpose and responsibility
- **Component 2**: Purpose and responsibility
- **Component 3**: Purpose and responsibility

#### Data Flow
1. Data enters at [point A]
2. Processed by [component B]
3. Stored in [location C]
4. Retrieved by [component D]

---

## Features

### Core Features
1. **Feature 1**: Description
2. **Feature 2**: Description
3. **Feature 3**: Description

### Additional Features
1. **Feature A**: Description
2. **Feature B**: Description

---

## Technical Details

### Technology Stack
- **Frontend**: [Technologies]
- **Backend**: [Technologies]
- **Database**: [Technologies]
- **Infrastructure**: [Technologies]

### Dependencies
{chr(10).join(f"- {dep}" for dep in deps) if deps else "- [List dependencies]"}

### Configuration
- **Environment Variables**: [List]
- **Config Files**: [List]
- **Secrets**: [List]

### API Endpoints
- `GET /endpoint1`: Description
- `POST /endpoint2`: Description

---

## Code Structure

### Directory Layout
```
project/
├── src/
├── tests/
├── docs/
└── config/
```

### Key Files
- `file1.py`: Purpose
- `file2.py`: Purpose

---

## History & Decisions

### Major Decisions

#### Decision 1: [Title]
- **Date**: YYYY-MM-DD
- **Decision**: [What was decided]
- **Rationale**: [Why]
- **Alternatives Considered**: [What else was considered]

#### Decision 2: [Title]
- **Date**: YYYY-MM-DD
- **Decision**: [What was decided]
- **Rationale**: [Why]

### Evolution
- **Phase 1**: [Description]
- **Phase 2**: [Description]

---

## Research & Context

### Research Findings
- Finding 1
- Finding 2

### References
- [Link 1]
- [Link 2]

### Related Work
- Project A: [How it relates]
- Project B: [How it relates]

---

## Performance & Metrics

### Performance Targets
- Metric 1: Target value
- Metric 2: Target value

### Current Performance
- Metric 1: Current value
- Metric 2: Current value

---

## Security & Compliance

### Security Measures
- Measure 1
- Measure 2

### Compliance Requirements
- Requirement 1
- Requirement 2

---

## Notes & Observations

[Additional notes, insights, and observations]

---

*Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Version: {version}*
*Status: {status}*
"""
        return template
    
    def create_criteria_template(self, project: str) -> str:
        """Create enhanced CRITERIA template with new sections"""
        project_title = project.replace('-', ' ').title()
        
        template = f"""---
project: {project_title}
type: criteria
created: {datetime.now().strftime("%Y-%m-%d")}
last_updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# {project_title} - Execution Guidelines

**Project**: {project_title}  
**Type**: Criteria & Best Practices  
**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Acceptance Criteria

### Must Have (P0)
- [ ] Criterion 1: [Specific, measurable criterion]
- [ ] Criterion 2: [Specific, measurable criterion]
- [ ] Criterion 3: [Specific, measurable criterion]

### Should Have (P1)
- [ ] Criterion 4: [Specific, measurable criterion]
- [ ] Criterion 5: [Specific, measurable criterion]

### Nice to Have (P2)
- [ ] Criterion 6: [Specific, measurable criterion]

---

## Tools & Technologies

### Required Tools
1. **Tool 1**: 
   - Purpose: [What it's for]
   - When to use: [Specific scenarios]
   - Installation: `command to install`

2. **Tool 2**:
   - Purpose: [What it's for]
   - When to use: [Specific scenarios]
   - Installation: `command to install`

### Recommended Tools
1. **Tool A**: Use when [scenario]
2. **Tool B**: Use when [scenario]

---

## Tool Usage Examples

### Tool 1: Concrete Examples

#### Use Case 1: [Scenario]
```bash
# Example command
tool1 --option value

# Expected output
[What you should see]
```

#### Use Case 2: [Scenario]
```python
# Example code
from tool1 import feature
result = feature.do_something()
```

### Tool 2: Concrete Examples

#### Use Case 1: [Scenario]
```bash
tool2 command
```

---

## Decision Tree

### When Starting a New Feature
```
Is it a UI feature?
├─ YES → Use [Frontend Framework]
│         └─ Is it complex?
│             ├─ YES → Create separate component
│             └─ NO → Add to existing component
└─ NO → Is it API-related?
          ├─ YES → Use [Backend Framework]
          └─ NO → Use [Other approach]
```

### When Fixing a Bug
```
Is it a known issue?
├─ YES → Check "Known Issues & Solutions" section
└─ NO → Is it reproducible?
          ├─ YES → Debug with [Tool X]
          └─ NO → Add logging and monitor
```

### When Deploying
```
Is it production?
├─ YES → Run full test suite
│         └─ All tests pass?
│             ├─ YES → Deploy with [Method A]
│             └─ NO → Fix and retest
└─ NO → Deploy to staging with [Method B]
```

---

## Known Issues & Solutions

### Issue 1: [Problem Description]
- **Symptom**: [What you see]
- **Root Cause**: [Why it happens]
- **Solution**: [How we fixed it]
- **Prevention**: [How to avoid it]
- **Date Resolved**: YYYY-MM-DD

### Issue 2: [Problem Description]
- **Symptom**: [What you see]
- **Root Cause**: [Why it happens]
- **Solution**: [How we fixed it]
- **Prevention**: [How to avoid it]
- **Date Resolved**: YYYY-MM-DD

### Issue 3: [Problem Description]
- **Status**: 🔴 Unresolved
- **Symptom**: [What you see]
- **Workaround**: [Temporary solution]
- **Investigating**: [Current status]

---

## Best Practices

### Code Quality
1. **Practice 1**: [Description and why]
2. **Practice 2**: [Description and why]
3. **Practice 3**: [Description and why]

### Testing
1. **Unit Tests**: [When and how]
2. **Integration Tests**: [When and how]
3. **E2E Tests**: [When and how]

### Documentation
1. **Code Comments**: [When to add]
2. **API Docs**: [How to maintain]
3. **README**: [What to include]

### Performance
1. **Optimization 1**: [What and when]
2. **Optimization 2**: [What and when]

---

## Workflows

### Development Workflow
1. **Create branch**: `git checkout -b feature/name`
2. **Implement feature**: Follow best practices
3. **Write tests**: Ensure coverage
4. **Run tests**: `npm test` or `pytest`
5. **Commit**: `git commit -m "feat: description"`
6. **Push**: `git push origin feature/name`
7. **Create PR**: Use PR template

### Deployment Workflow
1. **Merge to main**: After PR approval
2. **Run CI/CD**: Automated tests
3. **Deploy to staging**: Automatic
4. **Manual QA**: Test on staging
5. **Deploy to production**: `npm run deploy:prod`
6. **Monitor**: Check logs and metrics

### Bug Fix Workflow
1. **Reproduce**: Create test case
2. **Identify**: Debug with tools
3. **Fix**: Implement solution
4. **Test**: Verify fix works
5. **Document**: Add to Known Issues
6. **Deploy**: Follow deployment workflow

---

## Right Actions

### When Starting
- [ ] Read FULL.md completely
- [ ] Review CRITERIA.md
- [ ] Check CHANGELOG.md for recent changes
- [ ] Set up development environment
- [ ] Run `make setup` or equivalent
- [ ] Verify all tests pass

### When Implementing
- [ ] Check Decision Tree for guidance
- [ ] Review Known Issues for similar problems
- [ ] Follow Best Practices
- [ ] Use recommended tools
- [ ] Write tests alongside code
- [ ] Document as you go

### When Testing
- [ ] Run unit tests: `make test-unit`
- [ ] Run integration tests: `make test-integration`
- [ ] Test edge cases
- [ ] Test error handling
- [ ] Verify performance
- [ ] Check security

### When Deploying
- [ ] Review Pre-Deployment Checklist
- [ ] Ensure all tests pass
- [ ] Update CHANGELOG.md
- [ ] Create deployment tag
- [ ] Deploy to staging first
- [ ] Monitor metrics
- [ ] Rollback plan ready

---

## Common Pitfalls

### Pitfall 1: [Description]
- **Why it's bad**: [Explanation]
- **How to avoid**: [Prevention]
- **If it happens**: [Recovery]

### Pitfall 2: [Description]
- **Why it's bad**: [Explanation]
- **How to avoid**: [Prevention]
- **If it happens**: [Recovery]

### Pitfall 3: [Description]
- **Why it's bad**: [Explanation]
- **How to avoid**: [Prevention]
- **If it happens**: [Recovery]

---

## Checklists

### Pre-Development Checklist
- [ ] Environment set up
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] Database initialized
- [ ] Tests passing
- [ ] Documentation read

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Code reviewed
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Documentation updated
- [ ] Backup created
- [ ] Rollback plan ready
- [ ] Monitoring configured

### Post-Deployment Checklist
- [ ] Deployment successful
- [ ] Health checks passing
- [ ] Metrics normal
- [ ] No errors in logs
- [ ] Users notified (if needed)
- [ ] Documentation updated

---

## References

### Documentation
- [Official Docs](https://example.com)
- [API Reference](https://example.com/api)
- [Tutorial](https://example.com/tutorial)

### Examples
- [Example 1](https://github.com/example/1)
- [Example 2](https://github.com/example/2)

### Related Projects
- [Project A](https://github.com/project-a)
- [Project B](https://github.com/project-b)

---

*Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Keep this document updated as the project evolves*
"""
        return template
    
    def create_changelog_template(self, project: str) -> str:
        """Create CHANGELOG template"""
        project_title = project.replace('-', ' ').title()
        today = datetime.now().strftime("%Y-%m-%d")
        
        template = f"""---
project: {project_title}
type: changelog
created: {today}
last_updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# {project_title} - Change Log

**Project**: {project_title}  
**Type**: Change History  
**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Format

Each entry follows this format:
```
## YYYY-MM-DD HH:MM

### Added
- New feature or capability

### Changed
- Modification to existing feature

### Fixed
- Bug fix

### Removed
- Deprecated or removed feature

### Notes
- Additional context or observations
```

---

## {today}

### Added
- Initial project setup
- Created memory system (FULL, CRITERIA, CHANGELOG files)

### Notes
- Project initialized with 3-file memory system
- Ready for development

---

## Version History

### Version 1.0 - {today}
- Initial release
- Core features implemented
- Documentation complete

---

*Keep this log updated with every significant change*
*Use this to track project evolution and learn from history*
"""
        return template
    
    def initialize_project(self, project: str, description: str = "",
                          version: str = "1.0", status: str = "Development",
                          dependencies: List[str] = None):
        """Initialize a new project with 3 template files"""
        print(f"\n🆕 Initializing project: {project}")
        
        files = self.get_project_files(project)
        
        # Create FULL file
        if not files['full'].exists():
            template = self.create_full_template(project, description, version, status, dependencies)
            files['full'].write_text(template)
            print(f"   ✅ Created {files['full'].name}")
        else:
            print(f"   ℹ️  {files['full'].name} already exists")
        
        # Create CRITERIA file
        if not files['criteria'].exists():
            template = self.create_criteria_template(project)
            files['criteria'].write_text(template)
            print(f"   ✅ Created {files['criteria'].name}")
        else:
            print(f"   ℹ️  {files['criteria'].name} already exists")
        
        # Create CHANGELOG file
        if not files['changelog'].exists():
            template = self.create_changelog_template(project)
            files['changelog'].write_text(template)
            print(f"   ✅ Created {files['changelog'].name}")
        else:
            print(f"   ℹ️  {files['changelog'].name} already exists")
        
        # Load the project
        self.load_project(project)
    
    def save_full_knowledge(self, project: str, content: str, append: bool = False):
        """
        Save to FULL file
        
        Args:
            project: Project name
            content: Content to save
            append: Whether to append or overwrite
        """
        files = self.get_project_files(project)
        full_file = files['full']
        
        if append and full_file.exists():
            existing = full_file.read_text()
            content = f"{existing}\n\n{content}"
        
        full_file.write_text(content)
        print(f"   💾 Saved to {full_file.name}")
        
        # Update cache
        if project in self.loaded_projects:
            self.loaded_projects[project]['full'] = content
    
    def save_criteria(self, project: str, content: str, append: bool = False):
        """
        Save to CRITERIA file
        
        Args:
            project: Project name
            content: Content to save
            append: Whether to append or overwrite
        """
        files = self.get_project_files(project)
        criteria_file = files['criteria']
        
        if append and criteria_file.exists():
            existing = criteria_file.read_text()
            content = f"{existing}\n\n{content}"
        
        criteria_file.write_text(content)
        print(f"   💾 Saved to {criteria_file.name}")
        
        # Update cache
        if project in self.loaded_projects:
            self.loaded_projects[project]['criteria'] = content
    
    def log_change(self, project: str, change_type: str, description: str):
        """
        Log a change to CHANGELOG
        
        Args:
            project: Project name
            change_type: One of: Added, Changed, Fixed, Removed, Notes
            description: Description of the change
        """
        files = self.get_project_files(project)
        changelog_file = files['changelog']
        
        if not changelog_file.exists():
            print(f"   ⚠️  CHANGELOG not found, creating...")
            self.initialize_project(project)
        
        content = changelog_file.read_text()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Find if today's section exists
        today = datetime.now().strftime("%Y-%m-%d")
        today_section = f"## {today}"
        
        if today_section not in content:
            # Create new section for today
            new_section = f"""
## {timestamp}

### {change_type}
- {description}

---

"""
            # Insert after the format section
            insert_pos = content.find("---\n\n## ")
            if insert_pos != -1:
                content = content[:insert_pos + 5] + new_section + content[insert_pos + 5:]
        else:
            # Add to existing section
            # Find the section
            section_start = content.find(today_section)
            next_section = content.find("\n## ", section_start + 1)
            
            if next_section == -1:
                next_section = content.find("\n---\n\n## Version History")
            
            section_content = content[section_start:next_section]
            
            # Check if change_type subsection exists
            if f"### {change_type}" in section_content:
                # Add to existing subsection
                subsection_start = section_content.find(f"### {change_type}")
                next_subsection = section_content.find("\n###", subsection_start + 1)
                
                if next_subsection == -1:
                    next_subsection = len(section_content)
                
                # Insert before next subsection
                insertion = f"- {description}\n"
                section_content = section_content[:next_subsection] + insertion + section_content[next_subsection:]
            else:
                # Create new subsection
                insertion = f"\n### {change_type}\n- {description}\n"
                section_content += insertion
            
            # Replace in content
            content = content[:section_start] + section_content + content[next_section:]
        
        # Update last_updated in metadata
        content = re.sub(
            r'last_updated: .*',
            f'last_updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            content
        )
        
        changelog_file.write_text(content)
        print(f"   📝 Logged to CHANGELOG: [{change_type}] {description}")
    
    def get_context_for_task(self, task: str, project: Optional[str] = None) -> str:
        """Get complete context for a task"""
        if project is None:
            project = self.detect_project(task)
        
        print(f"\n🔍 Getting context for task in project: {project}")
        
        if project not in self.loaded_projects:
            self.load_project(project)
        
        content = self.loaded_projects.get(project, {
            'full': '',
            'criteria': '',
            'changelog': ''
        })
        
        context = f"""# Context for: {task}

## Project: {project.replace('-', ' ').title()}

---

## FULL KNOWLEDGE

{content['full']}

---

## EXECUTION GUIDELINES

{content['criteria']}

---

## CHANGE HISTORY

{content['changelog']}

---

*Context compiled: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        return context
    
    def list_projects(self) -> List[str]:
        """List all projects"""
        projects = set()
        
        for file in self.memory_root.glob("*_FULL.md"):
            project = file.stem.replace('_FULL', '').lower().replace('_', '-')
            projects.add(project)
        
        return sorted(list(projects))


def main():
    """Demo: Complete 3-File System"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              📁 Dive Memory - Complete 3-File System Demo                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    memory = DiveMemory3FileComplete()
    
    # Initialize Dive AI
    print("\n" + "="*80)
    memory.initialize_project(
        "dive-ai",
        description="AI development platform with unified brain architecture",
        version="V21.0",
        status="Production",
        dependencies=["python>=3.11", "openai", "anthropic"]
    )
    
    # Log some changes
    memory.log_change("dive-ai", "Added", "Complete 3-file memory system")
    memory.log_change("dive-ai", "Added", "Auto-loading orchestrator")
    memory.log_change("dive-ai", "Fixed", "Memory integration issues")
    
    # Initialize Calo Track
    print("\n" + "="*80)
    memory.initialize_project(
        "calo-track",
        description="Calorie tracking application with ML-powered food recognition",
        version="1.0",
        status="Development",
        dependencies=["react", "nodejs", "tensorflow"]
    )
    
    # Log changes for Calo Track
    memory.log_change("calo-track", "Added", "Food logging feature")
    memory.log_change("calo-track", "Added", "ML model for food recognition")
    
    # List projects
    print("\n" + "="*80)
    print("📂 All Projects:")
    projects = memory.list_projects()
    for i, proj in enumerate(projects, 1):
        print(f"   {i}. {proj}")
    
    # Get context
    print("\n" + "="*80)
    task = "Working on Calo Track: Implement meal logging feature"
    context = memory.get_context_for_task(task)
    print(f"📊 Context length: {len(context)} characters")
    
    print("\n" + "="*80)
    print("✅ Complete 3-File System Demo Done!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
