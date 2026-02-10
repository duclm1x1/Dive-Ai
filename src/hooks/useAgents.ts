import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '../lib/supabase';
import type { Agent } from '../types';

export function useAgents(workspaceId: string | undefined) {
  return useQuery({
    queryKey: ['agents', workspaceId],
    queryFn: async () => {
      if (!workspaceId) return [];
      const { data, error } = await supabase
        .from('agents')
        .select('*')
        .eq('workspace_id', workspaceId)
        .order('created_at', { ascending: false });
      if (error) throw error;
      return data as Agent[];
    },
    enabled: !!workspaceId,
  });
}

export function useCreateAgent() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async (input: {
      workspaceId: string;
      name: string;
      description?: string;
      systemPrompt?: string;
      model?: string;
    }) => {
      const { data, error } = await supabase
        .from('agents')
        .insert({
          workspace_id: input.workspaceId,
          name: input.name,
          description: input.description || '',
          system_prompt: input.systemPrompt || '',
          model: input.model || 'gpt-4',
        })
        .select()
        .single();
      if (error) throw error;
      return data as Agent;
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['agents', data.workspace_id] });
    },
  });
}

export function useUpdateAgent() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...updates }: {
      id: string;
      name?: string;
      description?: string;
      system_prompt?: string;
      model?: string;
      status?: 'active' | 'inactive' | 'error';
      workspaceId: string;
    }) => {
      const { workspaceId, ...fields } = updates;
      const { data, error } = await supabase
        .from('agents')
        .update(fields)
        .eq('id', id)
        .select()
        .single();
      if (error) throw error;
      return { agent: data as Agent, workspaceId };
    },
    onSuccess: ({ workspaceId }) => {
      qc.invalidateQueries({ queryKey: ['agents', workspaceId] });
    },
  });
}

export function useDeleteAgent() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, workspaceId }: { id: string; workspaceId: string }) => {
      const { error } = await supabase.from('agents').delete().eq('id', id);
      if (error) throw error;
      return workspaceId;
    },
    onSuccess: (workspaceId) => {
      qc.invalidateQueries({ queryKey: ['agents', workspaceId] });
    },
  });
}
