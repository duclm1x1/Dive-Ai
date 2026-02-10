import { z } from 'zod';

export interface Profile {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface Workspace {
  id: string;
  owner_id: string;
  name: string;
  slug: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: 'owner' | 'admin' | 'member';
  joined_at: string;
  profiles?: Profile;
}

export interface Conversation {
  id: string;
  workspace_id: string;
  user_id: string;
  title: string;
  model: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  user_id: string | null;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Agent {
  id: string;
  workspace_id: string;
  name: string;
  description: string;
  system_prompt: string;
  model: string;
  status: 'active' | 'inactive' | 'error';
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AgentLog {
  id: string;
  agent_id: string;
  execution_id: string | null;
  log_level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export const signupSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  fullName: z.string().min(1, 'Full name is required'),
});

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

export const createWorkspaceSchema = z.object({
  name: z.string().min(1, 'Name is required').max(50, 'Name too long'),
  description: z.string().max(200, 'Description too long').optional(),
});

export const createConversationSchema = z.object({
  title: z.string().min(1).max(100).optional(),
  model: z.string().optional(),
});

export const createAgentSchema = z.object({
  name: z.string().min(1, 'Name is required').max(50, 'Name too long'),
  description: z.string().max(500).optional(),
  systemPrompt: z.string().max(4000).optional(),
  model: z.string().optional(),
});

export const sendMessageSchema = z.object({
  content: z.string().min(1, 'Message cannot be empty'),
});

export type SignupInput = z.infer<typeof signupSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type CreateWorkspaceInput = z.infer<typeof createWorkspaceSchema>;
export type CreateAgentInput = z.infer<typeof createAgentSchema>;
