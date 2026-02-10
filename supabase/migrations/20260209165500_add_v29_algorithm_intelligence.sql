/*
  # Dive AI V29 - Extended Schema for Algorithm Intelligence

  This migration adds V29-specific tables for:
  1. Algorithm Portfolio - Track all algorithms and their performance
  2. Execution History - Detailed logs of algorithm executions with GPA scores
  3. Theses - V4 multi-perspective theses and outcomes
  4. Knowledge Entities - Knowledge graph nodes
  5. Knowledge Relations - Knowledge graph edges
  6. Workflow Executions - Meta-algorithm workflow tracking
  7. Tasks - Task decomposition and tracking
  8. Memory Snapshots - Conversation/project memory sync

  Date: 2026-02-09
*/

-- =====================
-- ALGORITHM PORTFOLIO
-- =====================
-- Track all available algorithms and their historical performance

CREATE TABLE IF NOT EXISTS algorithms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid REFERENCES workspaces(id) ON DELETE CASCADE,
  
  -- Algorithm Identity
  algorithm_id text NOT NULL,
  name text NOT NULL,
  tier text NOT NULL CHECK (tier IN ('strategy', 'tactic', 'operation')),
  category text NOT NULL,
  description text DEFAULT '',
  
  -- Performance Metrics
  base_score real DEFAULT 0.5,
  success_rate real DEFAULT 0.5,
  avg_execution_time_ms real DEFAULT 1000,
  total_executions integer DEFAULT 0,
  last_execution_at timestamptz,
  
  -- Configuration
  parameters jsonb DEFAULT '{}',
  dependencies jsonb DEFAULT '[]',
  is_enabled boolean DEFAULT true,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  
  UNIQUE(workspace_id, algorithm_id)
);

ALTER TABLE algorithms ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER algorithms_updated_at
  BEFORE UPDATE ON algorithms
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_algorithms_workspace ON algorithms(workspace_id);
CREATE INDEX idx_algorithms_tier ON algorithms(tier);
CREATE INDEX idx_algorithms_category ON algorithms(category);

-- =====================
-- EXECUTION HISTORY
-- =====================
-- Detailed logs of each algorithm execution with GPA scoring

CREATE TABLE IF NOT EXISTS execution_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  algorithm_id uuid REFERENCES algorithms(id) ON DELETE SET NULL,
  
  -- Execution Context
  execution_id text NOT NULL,
  parent_execution_id text,
  task_context text,
  
  -- Input/Output
  input_data jsonb DEFAULT '{}',
  output_data jsonb DEFAULT '{}',
  
  -- GPA Scoring (Goal-Plan-Action)
  gpa_score real,
  goal_alignment real,
  plan_alignment real,
  action_quality real,
  
  -- Execution Status
  status text NOT NULL DEFAULT 'pending' 
    CHECK (status IN ('pending', 'running', 'success', 'failed', 'cancelled')),
  error_message text,
  
  -- Timing
  started_at timestamptz DEFAULT now(),
  completed_at timestamptz,
  duration_ms integer,
  
  -- Feedback
  tactical_feedback text,
  strategic_feedback text,
  
  created_at timestamptz DEFAULT now()
);

ALTER TABLE execution_history ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_execution_workspace ON execution_history(workspace_id);
CREATE INDEX idx_execution_algorithm ON execution_history(algorithm_id);
CREATE INDEX idx_execution_status ON execution_history(status);
CREATE INDEX idx_execution_created ON execution_history(created_at DESC);

-- =====================
-- THESES (V4 Multi-Perspective)
-- =====================
-- Store strategic theses formed from multi-perspective analysis

CREATE TABLE IF NOT EXISTS theses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  
  -- Thesis Identity
  thesis_id text NOT NULL,
  title text NOT NULL,
  statement text NOT NULL,
  
  -- Evidence
  supporting_evidence jsonb DEFAULT '[]',
  counter_evidence jsonb DEFAULT '[]',
  
  -- Analysis
  perspectives_analyzed jsonb DEFAULT '[]',
  recommended_approach text,
  confidence_score real DEFAULT 0.5,
  
  -- Outcome Tracking
  status text DEFAULT 'active' CHECK (status IN ('active', 'validated', 'invalidated', 'archived')),
  outcome text,
  validated_at timestamptz,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  
  UNIQUE(workspace_id, thesis_id)
);

ALTER TABLE theses ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER theses_updated_at
  BEFORE UPDATE ON theses
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_theses_workspace ON theses(workspace_id);
CREATE INDEX idx_theses_status ON theses(status);

-- =====================
-- KNOWLEDGE ENTITIES
-- =====================
-- Knowledge graph nodes for RAG and memory retrieval

CREATE TABLE IF NOT EXISTS knowledge_entities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  
  -- Entity Identity
  entity_type text NOT NULL 
    CHECK (entity_type IN ('concept', 'file', 'function', 'class', 'pattern', 'decision', 'requirement')),
  name text NOT NULL,
  description text,
  
  -- Content
  content text,
  embedding vector(1536), -- OpenAI embedding dimension
  keywords jsonb DEFAULT '[]',
  
  -- Metadata
  source_file text,
  source_line_start integer,
  source_line_end integer,
  metadata jsonb DEFAULT '{}',
  
  -- Importance
  importance_score real DEFAULT 0.5,
  access_count integer DEFAULT 0,
  last_accessed_at timestamptz,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE knowledge_entities ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER knowledge_entities_updated_at
  BEFORE UPDATE ON knowledge_entities
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_knowledge_workspace ON knowledge_entities(workspace_id);
CREATE INDEX idx_knowledge_type ON knowledge_entities(entity_type);
CREATE INDEX idx_knowledge_name ON knowledge_entities(name);

-- =====================
-- KNOWLEDGE RELATIONS
-- =====================
-- Knowledge graph edges connecting entities

CREATE TABLE IF NOT EXISTS knowledge_relations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  
  source_id uuid NOT NULL REFERENCES knowledge_entities(id) ON DELETE CASCADE,
  target_id uuid NOT NULL REFERENCES knowledge_entities(id) ON DELETE CASCADE,
  
  -- Relation Type
  relation_type text NOT NULL 
    CHECK (relation_type IN ('imports', 'extends', 'implements', 'uses', 'references', 'depends_on', 'related_to', 'contradicts', 'supports')),
  
  -- Strength
  weight real DEFAULT 1.0,
  confidence real DEFAULT 1.0,
  
  -- Metadata
  metadata jsonb DEFAULT '{}',
  
  created_at timestamptz DEFAULT now(),
  
  UNIQUE(source_id, target_id, relation_type)
);

ALTER TABLE knowledge_relations ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_relations_workspace ON knowledge_relations(workspace_id);
CREATE INDEX idx_relations_source ON knowledge_relations(source_id);
CREATE INDEX idx_relations_target ON knowledge_relations(target_id);

-- =====================
-- WORKFLOW EXECUTIONS
-- =====================
-- Track meta-algorithm workflow executions

CREATE TABLE IF NOT EXISTS workflow_executions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  conversation_id uuid REFERENCES conversations(id) ON DELETE SET NULL,
  
  -- Workflow Identity
  workflow_id text NOT NULL,
  meta_algorithm text NOT NULL,
  goal text NOT NULL,
  
  -- State
  current_state text DEFAULT 'initializing',
  state_history jsonb DEFAULT '[]',
  context jsonb DEFAULT '{}',
  
  -- Progress
  total_steps integer DEFAULT 0,
  completed_steps integer DEFAULT 0,
  failed_steps integer DEFAULT 0,
  
  -- KPIs (Workflow Scorer)
  lead_time_seconds real,
  wasted_action_ratio real,
  path_complexity real,
  final_success_rate real,
  kpi_score real,
  
  -- Status
  status text DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled', 'paused')),
  error_message text,
  
  started_at timestamptz DEFAULT now(),
  completed_at timestamptz,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE workflow_executions ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER workflow_executions_updated_at
  BEFORE UPDATE ON workflow_executions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_workflow_workspace ON workflow_executions(workspace_id);
CREATE INDEX idx_workflow_conversation ON workflow_executions(conversation_id);
CREATE INDEX idx_workflow_status ON workflow_executions(status);

-- =====================
-- TASKS
-- =====================
-- Hierarchical task decomposition tracking

CREATE TABLE IF NOT EXISTS tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  workflow_id uuid REFERENCES workflow_executions(id) ON DELETE CASCADE,
  parent_task_id uuid REFERENCES tasks(id) ON DELETE CASCADE,
  
  -- Task Identity
  task_id text NOT NULL,
  title text NOT NULL,
  description text,
  
  -- Hierarchy
  tier text NOT NULL CHECK (tier IN ('strategy', 'tactic', 'operation')),
  depth integer DEFAULT 0,
  sequence_order integer DEFAULT 0,
  
  -- Execution
  assigned_algorithm text,
  input_data jsonb DEFAULT '{}',
  output_data jsonb DEFAULT '{}',
  
  -- Cost Function (A*)
  g_cost real, -- Historical cost
  h_cost real, -- Heuristic (estimated remaining)
  f_cost real, -- Total = g + h
  
  -- Status
  status text DEFAULT 'pending' 
    CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped', 'blocked')),
  gpa_score real,
  
  started_at timestamptz,
  completed_at timestamptz,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER tasks_updated_at
  BEFORE UPDATE ON tasks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_tasks_workspace ON tasks(workspace_id);
CREATE INDEX idx_tasks_workflow ON tasks(workflow_id);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_status ON tasks(status);

-- =====================
-- MEMORY SNAPSHOTS
-- =====================
-- Sync local SQLite memory to cloud

CREATE TABLE IF NOT EXISTS memory_snapshots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  
  -- Snapshot Identity
  snapshot_type text NOT NULL CHECK (snapshot_type IN ('project', 'session', 'algorithm', 'knowledge')),
  project_name text,
  
  -- Content
  full_content text, -- For PROJECT_FULL.md
  criteria_content text, -- For PROJECT_CRITERIA.md
  changelog_content text, -- For PROJECT_CHANGELOG.md
  
  -- Metadata
  file_count integer DEFAULT 0,
  total_size_bytes integer DEFAULT 0,
  checksum text,
  
  -- Sync Status
  sync_status text DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'conflict', 'error')),
  last_synced_at timestamptz,
  local_updated_at timestamptz,
  
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE memory_snapshots ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER memory_snapshots_updated_at
  BEFORE UPDATE ON memory_snapshots
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX idx_memory_workspace ON memory_snapshots(workspace_id);
CREATE INDEX idx_memory_type ON memory_snapshots(snapshot_type);
CREATE INDEX idx_memory_project ON memory_snapshots(project_name);

-- =====================
-- FILE HISTORY
-- =====================
-- Track file modifications (Brain Layer)

CREATE TABLE IF NOT EXISTS file_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  execution_id uuid REFERENCES execution_history(id) ON DELETE SET NULL,
  
  -- File Identity
  file_path text NOT NULL,
  file_name text NOT NULL,
  
  -- Action
  action text NOT NULL CHECK (action IN ('create', 'read', 'update', 'delete', 'move', 'copy')),
  description text,
  
  -- Content
  content_before text,
  content_after text,
  diff_summary text,
  
  -- Result
  result text CHECK (result IN ('success', 'failed', 'skipped')),
  error_message text,
  
  created_at timestamptz DEFAULT now()
);

ALTER TABLE file_history ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_file_history_workspace ON file_history(workspace_id);
CREATE INDEX idx_file_history_path ON file_history(file_path);
CREATE INDEX idx_file_history_created ON file_history(created_at DESC);

-- =====================
-- API USAGE TRACKING
-- =====================
-- Track LLM API usage and costs

CREATE TABLE IF NOT EXISTS api_usage (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid REFERENCES profiles(id) ON DELETE SET NULL,
  
  -- Request Info
  provider text NOT NULL, -- 'v98', 'aicoding', 'openai'
  model text NOT NULL,
  request_type text DEFAULT 'chat', -- 'chat', 'embedding', 'vision'
  
  -- Tokens
  prompt_tokens integer DEFAULT 0,
  completion_tokens integer DEFAULT 0,
  total_tokens integer DEFAULT 0,
  
  -- Cost (in USD cents)
  cost_cents real DEFAULT 0,
  
  -- Response
  latency_ms integer,
  status text CHECK (status IN ('success', 'error', 'timeout', 'rate_limited')),
  
  created_at timestamptz DEFAULT now()
);

ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_api_usage_workspace ON api_usage(workspace_id);
CREATE INDEX idx_api_usage_provider ON api_usage(provider);
CREATE INDEX idx_api_usage_created ON api_usage(created_at DESC);

-- =====================
-- RLS POLICIES FOR NEW TABLES
-- =====================

-- Algorithms
CREATE POLICY "Members can view algorithms"
  ON algorithms FOR SELECT TO authenticated
  USING (
    workspace_id IS NULL 
    OR EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = algorithms.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Admins can manage algorithms"
  ON algorithms FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = algorithms.workspace_id
      AND workspace_members.user_id = auth.uid()
      AND workspace_members.role IN ('owner', 'admin')
    )
  );

-- Execution History
CREATE POLICY "Members can view execution history"
  ON execution_history FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = execution_history.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can insert execution history"
  ON execution_history FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = execution_history.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- Theses
CREATE POLICY "Members can view theses"
  ON theses FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = theses.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can manage theses"
  ON theses FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = theses.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- Knowledge Entities
CREATE POLICY "Members can view knowledge"
  ON knowledge_entities FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = knowledge_entities.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can manage knowledge"
  ON knowledge_entities FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = knowledge_entities.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- Knowledge Relations
CREATE POLICY "Members can view relations"
  ON knowledge_relations FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = knowledge_relations.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can manage relations"
  ON knowledge_relations FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = knowledge_relations.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- Workflow Executions
CREATE POLICY "Members can view workflows"
  ON workflow_executions FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = workflow_executions.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can manage workflows"
  ON workflow_executions FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = workflow_executions.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- Tasks
CREATE POLICY "Members can view tasks"
  ON tasks FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = tasks.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can manage tasks"
  ON tasks FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = tasks.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- Memory Snapshots
CREATE POLICY "Members can view memory"
  ON memory_snapshots FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = memory_snapshots.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can manage memory"
  ON memory_snapshots FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = memory_snapshots.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- File History
CREATE POLICY "Members can view file history"
  ON file_history FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = file_history.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can insert file history"
  ON file_history FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = file_history.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- API Usage
CREATE POLICY "Members can view api usage"
  ON api_usage FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = api_usage.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can insert api usage"
  ON api_usage FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = api_usage.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

-- =====================
-- REALTIME FOR NEW TABLES
-- =====================
ALTER PUBLICATION supabase_realtime ADD TABLE workflow_executions;
ALTER PUBLICATION supabase_realtime ADD TABLE tasks;
ALTER PUBLICATION supabase_realtime ADD TABLE execution_history;
