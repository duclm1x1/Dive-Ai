"""
Dive Doc-First Workflow System
"Document before code, knowledge before action"

Workflow:
    1. Research & Document → Store in Dive Memory as @doc/...
    2. Create Task → Reference @doc/... with acceptance criteria
    3. AI reads task → Auto-loads docs from memory
    4. AI understands "done" → From acceptance criteria
    5. AI codes → With full context from docs
    6. Knowledge accumulates → Reusable across sessions

Benefits:
    ✅ Knowledge is preserved (not lost after session)
    ✅ AI has clear context (no guessing)
    ✅ No redundant code (AI knows what's done)
    ✅ Save tokens (reuse docs instead of re-research)
    ✅ Save time (no starting from zero)
    ✅ Knowledge compounds (builds over time)
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add core path
sys.path.insert(0, str(Path(__file__).parent))

from dive_memory_brain import get_brain


class DiveDocFirstWorkflow:
    """
    Doc-First Workflow System
    Document → Task → Code
    """
    
    def __init__(self):
        self.brain = get_brain()
    
    # ============================================================================
    # STEP 1: CREATE DOCUMENT (Research & Decisions)
    # ============================================================================
    
    def create_doc(self, doc_id: str, title: str, content: str,
                   doc_type: str = "research", tags: Optional[List[str]] = None) -> str:
        """
        Create a document in memory
        Can be referenced later with @doc/{doc_id}
        
        Args:
            doc_id: Unique document ID (e.g., "auth-jwt-research")
            title: Document title
            content: Full document content (research, decisions, rationale)
            doc_type: Type of document (research, decision, architecture, etc.)
            tags: Optional tags for categorization
        
        Returns:
            memory_id: ID of stored document
        """
        print(f"\n📝 Creating document: @doc/{doc_id}")
        print(f"   Title: {title}")
        print(f"   Type: {doc_type}")
        
        # Format document content
        doc_content = f"""# {title}

**Document ID**: @doc/{doc_id}
**Type**: {doc_type}
**Created**: {datetime.now().isoformat()}

---

{content}

---

**Reference**: Use @doc/{doc_id} to reference this document
"""
        
        # Prepare metadata
        metadata = {
            "doc_id": doc_id,
            "title": title,
            "doc_type": doc_type,
            "created_at": datetime.now().isoformat(),
            "reference": f"@doc/{doc_id}"
        }
        
        # Prepare tags
        if tags is None:
            tags = []
        tags.extend(["document", doc_type, doc_id])
        
        # Store in memory
        memory_id = self.brain.memory.add(
            content=doc_content,
            section="documents",
            subsection=doc_type,
            tags=tags,
            importance=9,  # High importance for documents
            metadata=metadata
        )
        
        print(f"   ✅ Stored: {memory_id}")
        print(f"   📎 Reference: @doc/{doc_id}")
        
        return memory_id
    
    def get_doc(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by its ID
        
        Args:
            doc_id: Document ID (with or without @doc/ prefix)
        
        Returns:
            Document data or None if not found
        """
        # Remove @doc/ prefix if present
        doc_id = doc_id.replace("@doc/", "")
        
        # Search for document
        results = self.brain.memory.search(
            query=f"@doc/{doc_id}",
            section="documents",
            top_k=1
        )
        
        if not results:
            return None
        
        doc = results[0]
        return {
            "memory_id": doc.id,
            "doc_id": doc_id,
            "title": doc.metadata.get("title", ""),
            "content": doc.content,
            "doc_type": doc.metadata.get("doc_type", ""),
            "created_at": doc.metadata.get("created_at", ""),
            "tags": doc.tags,
            "metadata": doc.metadata
        }
    
    # ============================================================================
    # STEP 2: CREATE TASK (With Acceptance Criteria & Doc References)
    # ============================================================================
    
    def create_task(self, task_id: str, title: str, description: str,
                   acceptance_criteria: List[str], doc_references: List[str],
                   assigned_to: Optional[str] = None) -> str:
        """
        Create a task with acceptance criteria and document references
        
        Args:
            task_id: Unique task ID
            title: Task title
            description: Task description
            acceptance_criteria: List of criteria to consider task "done"
            doc_references: List of @doc/... references
            assigned_to: Optional agent ID
        
        Returns:
            memory_id: ID of stored task
        """
        print(f"\n📋 Creating task: {task_id}")
        print(f"   Title: {title}")
        print(f"   References: {len(doc_references)} docs")
        print(f"   Acceptance Criteria: {len(acceptance_criteria)}")
        
        # Format task content
        task_content = f"""# Task: {title}

**Task ID**: {task_id}
**Status**: pending
**Created**: {datetime.now().isoformat()}
{f'**Assigned To**: {assigned_to}' if assigned_to else ''}

## Description

{description}

## Document References

{chr(10).join(f'- {ref}' for ref in doc_references)}

## Acceptance Criteria

{chr(10).join(f'{i+1}. {criterion}' for i, criterion in enumerate(acceptance_criteria))}

---

**AI Instructions**:
1. Read all referenced documents using @doc/... IDs
2. Understand what "done" means from acceptance criteria
3. Implement solution based on document context
4. Verify all acceptance criteria are met
5. Store results back to memory
"""
        
        # Prepare metadata
        metadata = {
            "task_id": task_id,
            "title": title,
            "status": "pending",
            "acceptance_criteria": acceptance_criteria,
            "doc_references": doc_references,
            "assigned_to": assigned_to,
            "created_at": datetime.now().isoformat()
        }
        
        # Prepare tags
        tags = ["task", "pending", task_id]
        if assigned_to:
            tags.append(assigned_to)
        
        # Store in memory
        memory_id = self.brain.memory.add(
            content=task_content,
            section="tasks",
            tags=tags,
            importance=8,
            metadata=metadata
        )
        
        print(f"   ✅ Task created: {memory_id}")
        
        return memory_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a task by its ID
        
        Args:
            task_id: Task ID
        
        Returns:
            Task data or None if not found
        """
        # Search for task
        results = self.brain.memory.search(
            query=task_id,
            section="tasks",
            top_k=1
        )
        
        if not results:
            return None
        
        task = results[0]
        return {
            "memory_id": task.id,
            "task_id": task_id,
            "title": task.metadata.get("title", ""),
            "content": task.content,
            "status": task.metadata.get("status", "pending"),
            "acceptance_criteria": task.metadata.get("acceptance_criteria", []),
            "doc_references": task.metadata.get("doc_references", []),
            "assigned_to": task.metadata.get("assigned_to", ""),
            "created_at": task.metadata.get("created_at", ""),
            "metadata": task.metadata
        }
    
    # ============================================================================
    # STEP 3: AI AUTO-READ SYSTEM
    # ============================================================================
    
    def load_task_context(self, task_id: str) -> Dict[str, Any]:
        """
        Load complete context for a task
        Automatically reads all referenced documents
        
        Args:
            task_id: Task ID
        
        Returns:
            Complete context including task and all referenced docs
        """
        print(f"\n🤖 AI: Loading task context for {task_id}...")
        
        # Load task
        task = self.get_task(task_id)
        if not task:
            return {
                "error": f"Task {task_id} not found",
                "task": None,
                "documents": []
            }
        
        print(f"   ✅ Task loaded: {task['title']}")
        
        # Load all referenced documents
        documents = []
        doc_refs = task.get("doc_references", [])
        
        print(f"   📚 Loading {len(doc_refs)} referenced documents...")
        
        for doc_ref in doc_refs:
            doc = self.get_doc(doc_ref)
            if doc:
                documents.append(doc)
                print(f"      ✅ {doc_ref}: {doc['title']}")
            else:
                print(f"      ⚠️  {doc_ref}: Not found")
        
        print(f"   ✅ Context loaded: {len(documents)} documents")
        
        return {
            "task": task,
            "documents": documents,
            "acceptance_criteria": task.get("acceptance_criteria", []),
            "full_context": self._build_full_context(task, documents)
        }
    
    def _build_full_context(self, task: Dict[str, Any], documents: List[Dict[str, Any]]) -> str:
        """Build complete context string for AI"""
        context = f"""# Task Context

## Task: {task['title']}

{task['content']}

## Referenced Documents

"""
        
        for doc in documents:
            context += f"\n### {doc['title']}\n\n"
            context += f"{doc['content']}\n\n"
            context += "---\n\n"
        
        return context
    
    # ============================================================================
    # STEP 4: UNDERSTAND "DONE"
    # ============================================================================
    
    def check_task_completion(self, task_id: str, completed_items: List[str]) -> Dict[str, Any]:
        """
        Check if task is complete based on acceptance criteria
        
        Args:
            task_id: Task ID
            completed_items: List of completed acceptance criteria
        
        Returns:
            Completion status and remaining items
        """
        task = self.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        criteria = task.get("acceptance_criteria", [])
        
        # Check completion
        completed_count = len(completed_items)
        total_count = len(criteria)
        is_complete = completed_count >= total_count
        
        remaining = [c for c in criteria if c not in completed_items]
        
        return {
            "task_id": task_id,
            "is_complete": is_complete,
            "completed": completed_count,
            "total": total_count,
            "percentage": (completed_count / total_count * 100) if total_count > 0 else 0,
            "remaining": remaining,
            "completed_items": completed_items
        }
    
    # ============================================================================
    # STEP 5: COMPLETE TASK & STORE RESULTS
    # ============================================================================
    
    def complete_task(self, task_id: str, result: str, 
                     completed_criteria: List[str], 
                     code_files: Optional[List[str]] = None) -> str:
        """
        Mark task as complete and store results
        
        Args:
            task_id: Task ID
            result: Task result description
            completed_criteria: List of completed acceptance criteria
            code_files: Optional list of files created/modified
        
        Returns:
            memory_id: ID of completion record
        """
        print(f"\n✅ Completing task: {task_id}")
        
        # Check completion
        completion_check = self.check_task_completion(task_id, completed_criteria)
        
        if not completion_check.get("is_complete"):
            print(f"   ⚠️  Task not fully complete!")
            print(f"   Completed: {completion_check['completed']}/{completion_check['total']}")
            print(f"   Remaining: {completion_check['remaining']}")
        
        # Format completion content
        completion_content = f"""# Task Completion: {task_id}

**Status**: {'complete' if completion_check.get('is_complete') else 'partial'}
**Completed**: {datetime.now().isoformat()}
**Completion Rate**: {completion_check.get('percentage', 0):.1f}%

## Result

{result}

## Completed Acceptance Criteria

{chr(10).join(f'✅ {criterion}' for criterion in completed_criteria)}

{f"## Remaining Criteria{chr(10)}{chr(10).join(f'⏳ {criterion}' for criterion in completion_check.get('remaining', []))}" if completion_check.get('remaining') else ''}

{f"## Files Created/Modified{chr(10)}{chr(10).join(f'- {file}' for file in code_files)}" if code_files else ''}
"""
        
        # Prepare metadata
        metadata = {
            "task_id": task_id,
            "status": "complete" if completion_check.get("is_complete") else "partial",
            "result": result,
            "completed_criteria": completed_criteria,
            "completion_rate": completion_check.get("percentage", 0),
            "code_files": code_files or [],
            "completed_at": datetime.now().isoformat()
        }
        
        # Store completion
        memory_id = self.brain.memory.add(
            content=completion_content,
            section="task-completions",
            tags=["completion", task_id, metadata["status"]],
            importance=8,
            metadata=metadata
        )
        
        print(f"   ✅ Completion stored: {memory_id}")
        print(f"   📊 Completion rate: {completion_check.get('percentage', 0):.1f}%")
        
        return memory_id
    
    # ============================================================================
    # WORKFLOW STATISTICS
    # ============================================================================
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        # Count documents
        docs = self.brain.memory.search("", section="documents", top_k=1000)
        
        # Count tasks
        tasks = self.brain.memory.search("", section="tasks", top_k=1000)
        
        # Count completions
        completions = self.brain.memory.search("", section="task-completions", top_k=1000)
        
        # Calculate completion rate
        completed_tasks = len([c for c in completions if c.metadata.get("status") == "complete"])
        total_tasks = len(tasks)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "documents": len(docs),
            "tasks": len(tasks),
            "completions": len(completions),
            "completed_tasks": completed_tasks,
            "pending_tasks": total_tasks - completed_tasks,
            "completion_rate": completion_rate
        }


# Example usage
if __name__ == "__main__":
    print("📚 Dive Doc-First Workflow System")
    print("="*80)
    
    workflow = DiveDocFirstWorkflow()
    
    # STEP 1: Create research document
    print("\n" + "="*80)
    print("STEP 1: Create Research Document")
    print("="*80)
    
    doc_id = workflow.create_doc(
        doc_id="auth-jwt-research",
        title="JWT Authentication Research",
        content="""## Research Findings

### Why JWT?
- Stateless authentication
- Scalable across microservices
- Industry standard

### Implementation Approach
1. Use RS256 algorithm (more secure than HS256)
2. Short-lived access tokens (15 min)
3. Long-lived refresh tokens (7 days)
4. Store refresh tokens in httpOnly cookies

### Libraries
- `jsonwebtoken` for token generation
- `bcrypt` for password hashing

### Security Considerations
- Never store sensitive data in JWT payload
- Always validate token signature
- Implement token rotation
""",
        doc_type="research",
        tags=["authentication", "jwt", "security"]
    )
    
    # STEP 2: Create task with doc reference
    print("\n" + "="*80)
    print("STEP 2: Create Task with Document Reference")
    print("="*80)
    
    task_id = workflow.create_task(
        task_id="implement-jwt-auth",
        title="Implement JWT Authentication System",
        description="Build a complete JWT authentication system based on research findings",
        acceptance_criteria=[
            "User can register with email and password",
            "User can login and receive JWT access token",
            "User can refresh token using refresh token",
            "Passwords are hashed with bcrypt",
            "Tokens use RS256 algorithm",
            "Access tokens expire in 15 minutes",
            "Refresh tokens expire in 7 days"
        ],
        doc_references=["@doc/auth-jwt-research"],
        assigned_to="agent-042"
    )
    
    # STEP 3: AI loads task context
    print("\n" + "="*80)
    print("STEP 3: AI Auto-Loads Task Context")
    print("="*80)
    
    context = workflow.load_task_context("implement-jwt-auth")
    
    print(f"\n📊 Context Summary:")
    print(f"   Task: {context['task']['title']}")
    print(f"   Documents: {len(context['documents'])}")
    print(f"   Acceptance Criteria: {len(context['acceptance_criteria'])}")
    
    # STEP 4: Complete task
    print("\n" + "="*80)
    print("STEP 4: Complete Task")
    print("="*80)
    
    completion_id = workflow.complete_task(
        task_id="implement-jwt-auth",
        result="Successfully implemented JWT authentication system with all security features",
        completed_criteria=[
            "User can register with email and password",
            "User can login and receive JWT access token",
            "User can refresh token using refresh token",
            "Passwords are hashed with bcrypt",
            "Tokens use RS256 algorithm",
            "Access tokens expire in 15 minutes",
            "Refresh tokens expire in 7 days"
        ],
        code_files=[
            "src/auth/jwt.service.ts",
            "src/auth/auth.controller.ts",
            "src/auth/auth.module.ts"
        ]
    )
    
    # STEP 5: Get workflow stats
    print("\n" + "="*80)
    print("STEP 5: Workflow Statistics")
    print("="*80)
    
    stats = workflow.get_workflow_stats()
    print(f"\n📊 Workflow Stats:")
    print(f"   Documents: {stats['documents']}")
    print(f"   Tasks: {stats['tasks']}")
    print(f"   Completed: {stats['completed_tasks']}")
    print(f"   Pending: {stats['pending_tasks']}")
    print(f"   Completion Rate: {stats['completion_rate']:.1f}%")
    
    print("\n" + "="*80)
    print("✅ Doc-First Workflow is working!")
    print("="*80)
