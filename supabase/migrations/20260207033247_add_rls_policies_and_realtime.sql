/*
  # Dive AI - Row Level Security Policies & Realtime

  1. Security Policies
    - `profiles`: Users can view profiles in shared workspaces, manage own profile
    - `workspaces`: Members can view, owners can create/update/delete
    - `workspace_members`: Members can view, owners/admins can manage
    - `conversations`: Workspace members can view/create, owners can manage own
    - `messages`: Workspace members can view/send messages
    - `agents`: Members can view, owners/admins can manage
    - `agent_logs`: Members can view logs

  2. Realtime
    - Enable realtime on messages, conversations, and agents tables
*/

-- =====================
-- PROFILES POLICIES
-- =====================

CREATE POLICY "Users can view profiles in shared workspaces"
  ON profiles FOR SELECT TO authenticated
  USING (
    id = auth.uid()
    OR EXISTS (
      SELECT 1 FROM workspace_members wm1
      JOIN workspace_members wm2 ON wm1.workspace_id = wm2.workspace_id
      WHERE wm1.user_id = auth.uid() AND wm2.user_id = profiles.id
    )
  );

CREATE POLICY "Users can create own profile"
  ON profiles FOR INSERT TO authenticated
  WITH CHECK (id = auth.uid());

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE TO authenticated
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid());

-- =====================
-- WORKSPACES POLICIES
-- =====================

CREATE POLICY "Members can view workspace"
  ON workspaces FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = workspaces.id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create workspaces"
  ON workspaces FOR INSERT TO authenticated
  WITH CHECK (owner_id = auth.uid());

CREATE POLICY "Owners can update workspace"
  ON workspaces FOR UPDATE TO authenticated
  USING (owner_id = auth.uid())
  WITH CHECK (owner_id = auth.uid());

CREATE POLICY "Owners can delete workspace"
  ON workspaces FOR DELETE TO authenticated
  USING (owner_id = auth.uid());

-- =====================
-- WORKSPACE MEMBERS POLICIES
-- =====================

CREATE POLICY "Members can view workspace members"
  ON workspace_members FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members wm
      WHERE wm.workspace_id = workspace_members.workspace_id
      AND wm.user_id = auth.uid()
    )
  );

CREATE POLICY "Owners and admins can add members"
  ON workspace_members FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workspace_members wm
      WHERE wm.workspace_id = workspace_members.workspace_id
      AND wm.user_id = auth.uid()
      AND wm.role IN ('owner', 'admin')
    )
    OR EXISTS (
      SELECT 1 FROM workspaces w
      WHERE w.id = workspace_members.workspace_id
      AND w.owner_id = auth.uid()
    )
  );

CREATE POLICY "Owners can update member roles"
  ON workspace_members FOR UPDATE TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspaces w
      WHERE w.id = workspace_members.workspace_id
      AND w.owner_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workspaces w
      WHERE w.id = workspace_members.workspace_id
      AND w.owner_id = auth.uid()
    )
  );

CREATE POLICY "Owners admins and self can remove members"
  ON workspace_members FOR DELETE TO authenticated
  USING (
    user_id = auth.uid()
    OR EXISTS (
      SELECT 1 FROM workspace_members wm
      WHERE wm.workspace_id = workspace_members.workspace_id
      AND wm.user_id = auth.uid()
      AND wm.role IN ('owner', 'admin')
    )
  );

-- =====================
-- CONVERSATIONS POLICIES
-- =====================

CREATE POLICY "Members can view conversations"
  ON conversations FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = conversations.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can create conversations"
  ON conversations FOR INSERT TO authenticated
  WITH CHECK (
    user_id = auth.uid()
    AND EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = conversations.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update own conversations"
  ON conversations FOR UPDATE TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own conversations"
  ON conversations FOR DELETE TO authenticated
  USING (user_id = auth.uid());

-- =====================
-- MESSAGES POLICIES
-- =====================

CREATE POLICY "Members can view messages"
  ON messages FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM conversations c
      JOIN workspace_members wm ON wm.workspace_id = c.workspace_id
      WHERE c.id = messages.conversation_id
      AND wm.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can send messages"
  ON messages FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM conversations c
      JOIN workspace_members wm ON wm.workspace_id = c.workspace_id
      WHERE c.id = messages.conversation_id
      AND wm.user_id = auth.uid()
    )
  );

-- =====================
-- AGENTS POLICIES
-- =====================

CREATE POLICY "Members can view agents"
  ON agents FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = agents.workspace_id
      AND workspace_members.user_id = auth.uid()
    )
  );

CREATE POLICY "Owners and admins can create agents"
  ON agents FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = agents.workspace_id
      AND workspace_members.user_id = auth.uid()
      AND workspace_members.role IN ('owner', 'admin')
    )
  );

CREATE POLICY "Owners and admins can update agents"
  ON agents FOR UPDATE TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = agents.workspace_id
      AND workspace_members.user_id = auth.uid()
      AND workspace_members.role IN ('owner', 'admin')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = agents.workspace_id
      AND workspace_members.user_id = auth.uid()
      AND workspace_members.role IN ('owner', 'admin')
    )
  );

CREATE POLICY "Owners and admins can delete agents"
  ON agents FOR DELETE TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM workspace_members
      WHERE workspace_members.workspace_id = agents.workspace_id
      AND workspace_members.user_id = auth.uid()
      AND workspace_members.role IN ('owner', 'admin')
    )
  );

-- =====================
-- AGENT LOGS POLICIES
-- =====================

CREATE POLICY "Members can view agent logs"
  ON agent_logs FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM agents a
      JOIN workspace_members wm ON wm.workspace_id = a.workspace_id
      WHERE a.id = agent_logs.agent_id
      AND wm.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can insert agent logs"
  ON agent_logs FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM agents a
      JOIN workspace_members wm ON wm.workspace_id = a.workspace_id
      WHERE a.id = agent_logs.agent_id
      AND wm.user_id = auth.uid()
    )
  );

-- =====================
-- REALTIME
-- =====================

ALTER PUBLICATION supabase_realtime ADD TABLE messages;
ALTER PUBLICATION supabase_realtime ADD TABLE conversations;
ALTER PUBLICATION supabase_realtime ADD TABLE agents;