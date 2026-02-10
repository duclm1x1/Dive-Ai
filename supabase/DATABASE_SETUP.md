# Dive AI - Supabase Database Setup

## Overview
Complete Supabase database configuration for Dive AI V29 with full support for:
- Algorithm Portfolio & Performance Tracking
- GPA Scoring (Goal-Plan-Action)
- Knowledge Graph for RAG
- Workflow & Task Decomposition
- Memory Sync (Local ↔ Cloud)
- API Usage Tracking

---

## Quick Setup

### 1. Create Supabase Project
```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF
```

### 2. Run Migrations
```bash
cd D:\Antigravity\Dive AI
supabase db push
```

### 3. Configure Environment
Create `.env` file:
```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

---

## Database Schema

### Core Tables (Migration 1)
| Table | Purpose |
|-------|---------|
| `profiles` | User profiles linked to auth.users |
| `workspaces` | Team workspaces |
| `workspace_members` | Workspace membership (owner/admin/member) |
| `conversations` | AI chat conversations |
| `messages` | Conversation messages |
| `agents` | AI agents configuration |
| `agent_logs` | Agent execution logs |

### V29 Tables (Migration 3)
| Table | Purpose |
|-------|---------|
| `algorithms` | Algorithm portfolio & performance metrics |
| `execution_history` | Detailed logs with GPA scoring |
| `theses` | V4 multi-perspective theses |
| `knowledge_entities` | Knowledge graph nodes |
| `knowledge_relations` | Knowledge graph edges |
| `workflow_executions` | Meta-algorithm workflows |
| `tasks` | Hierarchical task decomposition |
| `memory_snapshots` | Local ↔ Cloud memory sync |
| `file_history` | File modification tracking |
| `api_usage` | LLM API usage & costs |

---

## Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│  profiles   │────<│ workspace_members│>────│ workspaces  │
└─────────────┘     └─────────────────┘     └─────────────┘
      │                                            │
      │                                            │
      ▼                                            ▼
┌─────────────┐                            ┌─────────────┐
│conversations│                            │   agents    │
└─────────────┘                            └─────────────┘
      │                                            │
      ▼                                            ▼
┌─────────────┐                            ┌─────────────┐
│  messages   │                            │ agent_logs  │
└─────────────┘                            └─────────────┘

V29 Extension:

┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│ algorithms  │────>│ execution_history│<────│   tasks     │
└─────────────┘     └─────────────────┘     └─────────────┘
                            │                      │
                            ▼                      ▼
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   theses    │     │ workflow_executions│   │file_history │
└─────────────┘     └─────────────────┘     └─────────────┘

┌─────────────────┐     ┌─────────────────┐
│knowledge_entities│────<│knowledge_relations│
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────┐
│memory_snapshots │     │  api_usage  │
└─────────────────┘     └─────────────┘
```

---

## Key Features

### Row Level Security (RLS)
All tables have RLS enabled with policies:
- Users can only access data in their workspaces
- Owners and admins have full CRUD access
- Members have read access + limited write

### Realtime Subscriptions
Enabled on:
- `messages` - Live chat updates
- `conversations` - New chat notifications
- `agents` - Agent status changes
- `workflow_executions` - Workflow progress
- `tasks` - Task status updates
- `execution_history` - Algorithm completions

### Automatic Triggers
- `handle_new_user()` - Create profile on signup
- `handle_new_workspace()` - Add owner as member
- `update_updated_at()` - Auto-update timestamps

---

## Usage Examples

### Python Client
```python
from supabase import create_client

supabase = create_client(
    "https://YOUR_PROJECT.supabase.co",
    "your-anon-key"
)

# Insert algorithm execution
supabase.table("execution_history").insert({
    "workspace_id": workspace_id,
    "algorithm_id": algorithm_uuid,
    "execution_id": "exec_123",
    "gpa_score": 0.85,
    "goal_alignment": 0.9,
    "plan_alignment": 0.8,
    "action_quality": 0.85,
    "status": "success"
}).execute()

# Query top algorithms
result = supabase.table("algorithms") \
    .select("*") \
    .eq("workspace_id", workspace_id) \
    .order("success_rate", desc=True) \
    .limit(10) \
    .execute()
```

### JavaScript Client
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://YOUR_PROJECT.supabase.co',
  'your-anon-key'
)

// Subscribe to workflow updates
const channel = supabase
  .channel('workflow-updates')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'workflow_executions' },
    (payload) => console.log('Workflow update:', payload)
  )
  .subscribe()

// Insert knowledge entity
const { data, error } = await supabase
  .from('knowledge_entities')
  .insert({
    workspace_id: workspaceId,
    entity_type: 'function',
    name: 'calculate_gpa_score',
    description: 'Calculates GPA score for algorithm execution',
    source_file: 'core/evaluation/gpa_scorer.py'
  })
```

---

## Migration Files

| File | Description |
|------|-------------|
| `20260207033202_create_core_tables_and_functions.sql` | Core tables, triggers, indexes |
| `20260207033247_add_rls_policies_and_realtime.sql` | RLS policies, realtime setup |
| `20260209165500_add_v29_algorithm_intelligence.sql` | V29 algorithm/knowledge tables |

---

## Performance Indexes

```sql
-- Core tables
idx_workspace_members_user, idx_workspace_members_workspace
idx_conversations_workspace, idx_conversations_user
idx_messages_conversation, idx_messages_created
idx_agents_workspace, idx_agent_logs_agent

-- V29 tables
idx_algorithms_workspace, idx_algorithms_tier, idx_algorithms_category
idx_execution_workspace, idx_execution_algorithm, idx_execution_status
idx_theses_workspace, idx_theses_status
idx_knowledge_workspace, idx_knowledge_type, idx_knowledge_name
idx_relations_workspace, idx_relations_source, idx_relations_target
idx_workflow_workspace, idx_workflow_conversation, idx_workflow_status
idx_tasks_workspace, idx_tasks_workflow, idx_tasks_parent, idx_tasks_status
idx_memory_workspace, idx_memory_type, idx_memory_project
idx_file_history_workspace, idx_file_history_path, idx_file_history_created
idx_api_usage_workspace, idx_api_usage_provider, idx_api_usage_created
```

---

## Admin Commands

```bash
# Reset database (DANGER: deletes all data)
supabase db reset

# Generate TypeScript types
supabase gen types typescript --local > src/types/database.ts

# View logs
supabase db logs

# Dump schema
supabase db dump -f schema.sql
```

---

## Support
For issues with Supabase setup, see:
- [Supabase Docs](https://supabase.com/docs)
- [Dive AI GitHub](https://github.com/duclm1x1/Dive-AI)
