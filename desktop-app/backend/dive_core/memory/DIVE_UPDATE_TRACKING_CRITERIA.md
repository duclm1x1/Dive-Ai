# Dive Update System - Execution Criteria

## When to Run Update Analysis

### Trigger Conditions

1. **Version Breakthrough**
   - Major version change (e.g., 20.x → 21.x)
   - Minor version change with breaking changes
   - Action: Run full impact analysis

2. **Core File Modification**
   - Changes to files in core/ directory
   - Changes to memory system
   - Changes to orchestrator/coder
   - Action: Analyze transitive dependencies

3. **API Changes**
   - Function signature changes
   - New required parameters
   - Removed functions
   - Action: Critical impact analysis

4. **Setup Script Changes**
   - Changes to install.sh
   - Changes to first_run scripts
   - Changes to startup scripts
   - Action: Test installation flow

### Impact Levels

#### CRITICAL
- Breaking API changes
- Version mismatches in setup scripts
- Core system incompatibilities
- **Action:** Must fix before release

#### HIGH
- Function signature changes
- Direct dependency issues
- Test failures
- **Action:** Should fix before release

#### MEDIUM
- New features requiring updates
- Documentation updates
- Refactoring impacts
- **Action:** Fix in next iteration

#### LOW
- Comment changes
- Minor documentation updates
- Non-breaking enhancements
- **Action:** Optional, can defer

## Update Application Rules

### Auto-Apply Criteria

Safe to auto-apply if:
1. Simple version string replacement
2. Documentation updates
3. Comment updates
4. No logic changes

### Manual Review Required

Requires human review if:
1. Code logic changes
2. Function signature changes
3. Complex refactoring
4. Test modifications

## Decision Tree

```
File Changed
    ↓
Is it a core file?
    ↓ Yes
    Run full dependency scan
    Analyze all dependents
    Generate update plan
    Apply auto-updates
    Flag manual reviews
    ↓ No
    Is it a setup script?
        ↓ Yes
        Check version references
        Update related scripts
        Test installation
        ↓ No
        Is it documentation?
            ↓ Yes
            Update version refs
            Check examples
            ↓ No
            Standard update flow
```

## Known Issues

### Issue 1: Version Mismatch Detection
**Problem:** Sometimes version strings in comments are not detected
**Workaround:** Use strict VERSION constant pattern
**Status:** Monitoring

### Issue 2: Circular Dependencies
**Problem:** Circular imports can cause analysis loops
**Workaround:** Track visited files to prevent infinite loops
**Status:** Handled in code

## Examples

### Example 1: Core File Update

```python
# Changed file: core/dive_memory_3file_complete.py
# New version: 21.0.0

# Run analysis
system = DiveUpdateMemoryIntegration()
system.track_change_and_update(
    changed_files=["core/dive_memory_3file_complete.py"],
    new_version="21.0.0",
    breaking=True,
    description="Updated to 3-file memory structure"
)

# Result:
# - 15 files analyzed
# - 5 critical impacts found
# - 3 auto-updates applied
# - 2 manual reviews flagged
```

### Example 2: Version Breakthrough

```python
# Breakthrough from 20.4.1 to 21.0.0

system = DiveUpdateMemoryIntegration()
system.version_breakthrough(
    from_version="20.4.1",
    to_version="21.0.0",
    major_changes=[
        "Memory system restructured",
        "New knowledge graph feature",
        "Enhanced workflow"
    ]
)

# Result:
# - Full project scan
# - Impact analysis on all files
# - Update plan generated
# - Critical updates applied
# - Report saved to memory
```

## Metadata

- **Last Updated:** 2026-02-05T04:22:10.060026
- **Version:** 1.0
- **Status:** Active
