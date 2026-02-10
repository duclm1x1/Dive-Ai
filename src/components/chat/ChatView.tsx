import { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MessageSquarePlus, Sparkles, Brain } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { useMessages, useSendMessage, useInsertAssistantMessage } from '../../hooks/useMessages';
import { useConversations, useCreateConversation, useUpdateConversation } from '../../hooks/useConversations';
import { useRealtimeMessages, useRealtimeConversations } from '../../hooks/useRealtime';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { EmptyState } from '../ui/EmptyState';
import { getLlmConfig, setLlmConfig, type LlmConfig } from '../../lib/llmConfig';
import type { Message } from '../../types';

let localIdCounter = 0;

async function callAi(
  messages: { role: string; content: string }[],
  config: LlmConfig,
  onStream?: (chunk: string) => void
): Promise<string> {
  const apiUrl = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/chat`;
  const useStream = !!config.apiKey && !!onStream;

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages,
      model: config.model,
      provider: config.provider,
      apiKey: config.apiKey || undefined,
      baseUrl: config.baseUrl || undefined,
      stream: useStream,
    }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    return data.reply || 'The AI provider returned an error. Check your settings.';
  }

  if (useStream && response.headers.get('content-type')?.includes('text/event-stream')) {
    const reader = response.body?.getReader();
    if (!reader) return 'Stream unavailable.';

    const decoder = new TextDecoder();
    let full = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = line.slice(6).trim();
        if (payload === '[DONE]') break;
        try {
          const parsed = JSON.parse(payload);
          const delta = parsed.choices?.[0]?.delta?.content || '';
          if (delta) {
            full += delta;
            onStream(full);
          }
        } catch { /* skip malformed chunks */ }
      }
    }
    return full || 'No response from model.';
  }

  const data = await response.json();
  return data.reply || data.message || 'I received your message.';
}

function WelcomeScreen({ onSend, model, onModelChange }: {
  onSend: (content: string) => void;
  model: string;
  onModelChange: (m: string) => void;
}) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <div className="h-14 w-14 rounded-xl bg-brand-600/15 border border-brand-600/25 flex items-center justify-center mb-5">
          <Brain size={26} className="text-brand-400" />
        </div>
        <h2 className="text-lg font-semibold text-white mb-1.5">Dive AI</h2>
        <p className="text-surface-500 text-sm text-center max-w-sm mb-1">
          Your intelligent coding assistant. Ask anything about code, architecture, debugging, or technical concepts.
        </p>
        <p className="text-[11px] text-surface-600 font-mono mb-6">
          Configure your API key in Settings for full LLM access
        </p>
        <div className="grid grid-cols-2 gap-2 max-w-md w-full">
          {[
            'Write a React hook for debouncing',
            'Explain async/await in TypeScript',
            'Review my API architecture',
            'Debug a memory leak in Node.js',
          ].map((prompt) => (
            <button
              key={prompt}
              onClick={() => onSend(prompt)}
              className="text-left px-3 py-2.5 rounded-lg bg-surface-900 border border-surface-800 hover:border-surface-700 text-xs text-surface-400 hover:text-surface-200 transition-all"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
      <ChatInput onSend={onSend} loading={false} model={model} onModelChange={onModelChange} />
    </div>
  );
}

function GuestChatView() {
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [config, setConfig] = useState<LlmConfig>(getLlmConfig);

  useEffect(() => {
    const handleConfigChange = (e: Event) => {
      const customEvent = e as CustomEvent<LlmConfig>;
      if (customEvent.detail) {
        setConfig(customEvent.detail);
      }
    };
    window.addEventListener('llm-config-changed', handleConfigChange);
    return () => window.removeEventListener('llm-config-changed', handleConfigChange);
  }, []);

  const handleModelChange = (model: string) => {
    const newConfig = { ...config, model };
    setConfig(newConfig);
    setLlmConfig(newConfig);
  };

  const handleSend = useCallback(async (content: string) => {
    const userMsg: Message = {
      id: `local-${++localIdCounter}`,
      conversation_id: 'guest',
      user_id: 'guest',
      sender: 'user',
      content,
      metadata: {},
      created_at: new Date().toISOString(),
    };

    const updated = [...localMessages, userMsg];
    setLocalMessages(updated);
    setAiLoading(true);
    setStreamingContent('');

    const history = updated.map((m) => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.content,
    }));

    const reply = await callAi(history, config, (chunk) => {
      setStreamingContent(chunk);
    });

    setStreamingContent('');
    setAiLoading(false);

    const assistantMsg: Message = {
      id: `local-${++localIdCounter}`,
      conversation_id: 'guest',
      user_id: null,
      sender: 'assistant',
      content: reply,
      metadata: {},
      created_at: new Date().toISOString(),
    };
    setLocalMessages((prev) => [...prev, assistantMsg]);
  }, [localMessages, config]);

  if (localMessages.length === 0 && !aiLoading) {
    return <WelcomeScreen onSend={handleSend} model={config.model} onModelChange={handleModelChange} />;
  }

  return (
    <div className="h-full flex flex-col">
      <MessageList messages={localMessages} loading={aiLoading} streamingContent={streamingContent} />
      <ChatInput onSend={handleSend} loading={aiLoading} model={config.model} onModelChange={handleModelChange} />
    </div>
  );
}

function AuthenticatedChatView() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const { currentWorkspace } = useWorkspace();
  const { data: messages } = useMessages(conversationId);
  const { data: conversations } = useConversations(currentWorkspace?.id);
  const sendMessage = useSendMessage();
  const insertAssistant = useInsertAssistantMessage();
  const createConversation = useCreateConversation();
  const updateConversation = useUpdateConversation();
  const [aiLoading, setAiLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [config, setConfig] = useState<LlmConfig>(getLlmConfig);

  useRealtimeMessages(conversationId);
  useRealtimeConversations(currentWorkspace?.id);

  useEffect(() => {
    const handleConfigChange = (e: Event) => {
      const customEvent = e as CustomEvent<LlmConfig>;
      if (customEvent.detail) {
        setConfig(customEvent.detail);
      }
    };
    window.addEventListener('llm-config-changed', handleConfigChange);
    return () => window.removeEventListener('llm-config-changed', handleConfigChange);
  }, []);

  const currentConversation = conversations?.find((c) => c.id === conversationId);

  const handleModelChange = (model: string) => {
    const newConfig = { ...config, model };
    setConfig(newConfig);
    setLlmConfig(newConfig);
  };

  const handleSend = useCallback(async (content: string) => {
    if (!conversationId || !currentWorkspace) return;

    await sendMessage.mutateAsync({ conversationId, content });

    if (currentConversation?.title === 'New Conversation') {
      const title = content.length > 50 ? content.slice(0, 50) + '...' : content;
      updateConversation.mutate({ id: conversationId, title, workspaceId: currentWorkspace.id });
    }

    setAiLoading(true);
    setStreamingContent('');

    const history = [...(messages ?? []), { sender: 'user' as const, content }].map((m) => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.content,
    }));

    const reply = await callAi(history, config, (chunk) => {
      setStreamingContent(chunk);
    });

    setStreamingContent('');
    await insertAssistant.mutateAsync({ conversationId, content: reply });
    setAiLoading(false);
  }, [conversationId, currentWorkspace, messages, currentConversation, sendMessage, insertAssistant, updateConversation, config]);

  const handleNewChat = async () => {
    if (!currentWorkspace) return;
    const conv = await createConversation.mutateAsync({ workspaceId: currentWorkspace.id });
    navigate(`/chat/${conv.id}`);
  };

  if (!conversationId) {
    return (
      <div className="h-full flex flex-col items-center justify-center">
        <EmptyState
          icon={MessageSquarePlus}
          title="Start a conversation"
          description="Select a conversation from the sidebar or create a new one."
          action={
            <button onClick={handleNewChat} className="btn-primary flex items-center gap-2 text-sm">
              <Sparkles size={14} />
              New Conversation
            </button>
          }
        />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-2.5 border-b border-surface-800 bg-surface-950/80 backdrop-blur-sm flex items-center gap-2">
        <h2 className="text-sm font-medium text-white truncate">
          {currentConversation?.title ?? 'Conversation'}
        </h2>
        <span className="text-[10px] text-surface-600 font-mono">
          {currentConversation?.model ?? config.model}
        </span>
      </div>
      <MessageList messages={messages ?? []} loading={aiLoading} streamingContent={streamingContent} />
      <ChatInput onSend={handleSend} loading={aiLoading} model={config.model} onModelChange={handleModelChange} />
    </div>
  );
}

export function ChatView() {
  const { isGuest } = useAuth();
  return isGuest ? <GuestChatView /> : <AuthenticatedChatView />;
}
