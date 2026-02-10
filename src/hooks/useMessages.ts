import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import type { Message } from '../types';

export function useMessages(conversationId: string | undefined) {
  return useQuery({
    queryKey: ['messages', conversationId],
    queryFn: async () => {
      if (!conversationId) return [];
      const { data, error } = await supabase
        .from('messages')
        .select('*')
        .eq('conversation_id', conversationId)
        .order('created_at', { ascending: true });
      if (error) throw error;
      return data as Message[];
    },
    enabled: !!conversationId,
  });
}

export function useSendMessage() {
  const qc = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: async ({ conversationId, content }: { conversationId: string; content: string }) => {
      const { data, error } = await supabase
        .from('messages')
        .insert({
          conversation_id: conversationId,
          user_id: user!.id,
          sender: 'user',
          content,
        })
        .select()
        .single();
      if (error) throw error;
      return data as Message;
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['messages', data.conversation_id] });
    },
  });
}

export function useInsertAssistantMessage() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async ({ conversationId, content, metadata }: {
      conversationId: string;
      content: string;
      metadata?: Record<string, unknown>;
    }) => {
      const { data, error } = await supabase
        .from('messages')
        .insert({
          conversation_id: conversationId,
          sender: 'assistant',
          content,
          metadata: metadata ?? {},
        })
        .select()
        .single();
      if (error) throw error;
      return data as Message;
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['messages', data.conversation_id] });
    },
  });
}
