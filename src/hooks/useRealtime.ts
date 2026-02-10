import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { supabase } from '../lib/supabase';

export function useRealtimeMessages(conversationId: string | undefined) {
  const qc = useQueryClient();

  useEffect(() => {
    if (!conversationId) return;

    const channel = supabase
      .channel(`messages:${conversationId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'messages',
          filter: `conversation_id=eq.${conversationId}`,
        },
        () => {
          qc.invalidateQueries({ queryKey: ['messages', conversationId] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [conversationId, qc]);
}

export function useRealtimeConversations(workspaceId: string | undefined) {
  const qc = useQueryClient();

  useEffect(() => {
    if (!workspaceId) return;

    const channel = supabase
      .channel(`conversations:${workspaceId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'conversations',
          filter: `workspace_id=eq.${workspaceId}`,
        },
        () => {
          qc.invalidateQueries({ queryKey: ['conversations', workspaceId] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [workspaceId, qc]);
}

export function useRealtimeAgents(workspaceId: string | undefined) {
  const qc = useQueryClient();

  useEffect(() => {
    if (!workspaceId) return;

    const channel = supabase
      .channel(`agents:${workspaceId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'agents',
          filter: `workspace_id=eq.${workspaceId}`,
        },
        () => {
          qc.invalidateQueries({ queryKey: ['agents', workspaceId] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [workspaceId, qc]);
}
