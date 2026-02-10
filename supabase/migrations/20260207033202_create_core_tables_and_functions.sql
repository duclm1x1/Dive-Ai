/*
  # Dive AI - Core Database Schema

  1. New Tables
    - `profiles` - User profiles linked to auth.users
      - `id` (uuid, PK, references auth.users)
      - `email` (text, not null)
      - `full_name` (text, default '')
      - `avatar_url` (text, nullable)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)
    - `workspaces` - Team workspaces
      - `id` (uuid, PK)
      - `owner_id` (uuid, references profiles)
      - `name` (text, not null)
      - `slug` (text, unique)
      - `description` (text)
      - `created_at` / `updated_at`
    - `workspace_members` - Workspace membership join table
      - `id` (uuid, PK)
      - `workspace_id` (uuid, references workspaces)
      - `user_id` (uuid, references profiles)
      - `role` (text: owner/admin/member)
      - `joined_at` (timestamptz)
    - `conversations` - AI chat conversations
      - `id` (uuid, PK)
      - `workspace_id` (uuid, references workspaces)
      - `user_id` (uuid, references profiles)
      - `title` (text)
      - `model` (text)
      - `created_at` / `updated_at`
    - `messages` - Conversation messages
      - `id` (uuid, PK)
      - `conversation_id` (uuid, references conversations)
      - `user_id` (uuid, nullable)
      - `sender` (text: user/assistant/system)
      - `content` (text)
      - `metadata` (jsonb)
      - `created_at` (timestamptz)
    - `agents` - AI agents configuration
      - `id` (uuid, PK)
      - `workspace_id` (uuid, references workspaces)
      - `name` (text)
      - `description` (text)
      - `system_prompt` (text)
      - `model` (text)
      - `status` (text: active/inactive/error)
      - `config` (jsonb)
      - `created_at` / `updated_at`
    - `agent_logs` - Agent execution logs
      - `id` (uuid, PK)
      - `agent_id` (uuid, references agents)
      - `execution_id` (text)
      - `log_level` (text: debug/info/warn/error)
      - `message` (text)
      - `metadata` (jsonb)
      - `created_at` (timestamptz)

  2. Functions
    - `handle_new_user()` - Auto-creates profile on signup
    - `handle_new_workspace()` - Auto-adds owner as member
    - `update_updated_at()` - Auto-updates updated_at columns

  3. Triggers
    - `on_auth_user_created` - Fires handle_new_user
    - `on_workspace_created` - Fires handle_new_workspace
    - Updated_at triggers on profiles, workspaces, conversations, agents

  4. Security
    - RLS enabled on ALL tables
*/

-- Utility function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email text NOT NULL,
  full_name text NOT NULL DEFAULT '',
  avatar_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Workspaces table
CREATE TABLE IF NOT EXISTS workspaces (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name text NOT NULL,
  slug text UNIQUE NOT NULL,
  description text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER workspaces_updated_at
  BEFORE UPDATE ON workspaces
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Workspace members join table
CREATE TABLE IF NOT EXISTS workspace_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  role text NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
  joined_at timestamptz DEFAULT now(),
  UNIQUE(workspace_id, user_id)
);

ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;

-- Auto-add owner as workspace member
CREATE OR REPLACE FUNCTION handle_new_workspace()
RETURNS trigger AS $$
BEGIN
  INSERT INTO workspace_members (workspace_id, user_id, role)
  VALUES (NEW.id, NEW.owner_id, 'owner');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_workspace_created
  AFTER INSERT ON workspaces
  FOR EACH ROW EXECUTE FUNCTION handle_new_workspace();

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title text NOT NULL DEFAULT 'New Conversation',
  model text DEFAULT 'gpt-4',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id uuid NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  user_id uuid REFERENCES profiles(id) ON DELETE SET NULL,
  sender text NOT NULL CHECK (sender IN ('user', 'assistant', 'system')),
  content text NOT NULL,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text DEFAULT '',
  system_prompt text DEFAULT '',
  model text DEFAULT 'gpt-4',
  status text NOT NULL DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error')),
  config jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE agents ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER agents_updated_at
  BEFORE UPDATE ON agents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Agent logs table
CREATE TABLE IF NOT EXISTS agent_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  execution_id text,
  log_level text NOT NULL DEFAULT 'info' CHECK (log_level IN ('debug', 'info', 'warn', 'error')),
  message text NOT NULL,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_conversations_workspace ON conversations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_agents_workspace ON agents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON agent_logs(agent_id);