import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import type { Conversation } from '../types';

export function useConversations(workspaceId: string | undefined) {
  return useQuery({
    queryKey: ['conversations', workspaceId],
    queryFn: async () => {
      if (!workspaceId) return [];
      const { data, error } = await supabase
        .from('conversations')
        .select('*')
        .eq('workspace_id', workspaceId)
        .order('updated_at', { ascending: false });
      if (error) throw error;
      return data as Conversation[];
    },
    enabled: !!workspaceId,
  });
}

export function useCreateConversation() {
  const qc = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: async ({ workspaceId, title, model }: { workspaceId: string; title?: string; model?: string }) => {
      const { data, error } = await supabase
        .from('conversations')
        .insert({
          workspace_id: workspaceId,
          user_id: user!.id,
          title: title || 'New Conversation',
          model: model || 'gpt-4',
        })
        .select()
        .single();
      if (error) throw error;
      return data as Conversation;
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['conversations', data.workspace_id] });
    },
  });
}

export function useDeleteConversation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, workspaceId }: { id: string; workspaceId: string }) => {
      const { error } = await supabase.from('conversations').delete().eq('id', id);
      if (error) throw error;
      return workspaceId;
    },
    onSuccess: (workspaceId) => {
      qc.invalidateQueries({ queryKey: ['conversations', workspaceId] });
    },
  });
}

export function useUpdateConversation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, title }: { id: string; title: string; workspaceId: string }) => {
      const { data, error } = await supabase
        .from('conversations')
        .update({ title })
        .eq('id', id)
        .select()
        .single();
      if (error) throw error;
      return data as Conversation;
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['conversations', data.workspace_id] });
    },
  });
}
