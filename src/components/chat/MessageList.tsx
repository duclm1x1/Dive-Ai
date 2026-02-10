import { useEffect, useRef, useState } from 'react';
import { Bot, User, Brain, Copy, Edit3, Trash2, RefreshCw, Check, MoreVertical, FileVideo, FileAudio, Image as ImageIcon } from 'lucide-react';
import type { Message, FileAttachment } from '../../types';
import { MarkdownRenderer } from './MarkdownRenderer';

interface MessageListProps {
  messages: Message[];
  loading?: boolean;
  streamingContent?: string;
}

function AttachmentPreview({ attachment }: { attachment: FileAttachment }) {
  const Icon = attachment.type === 'video' ? FileVideo
    : attachment.type === 'audio' ? FileAudio
    : ImageIcon;

  return (
    <div className="inline-block mr-2 mb-2">
      {attachment.preview && (attachment.type === 'image' || attachment.type === 'video') ? (
        <div className="relative w-40 h-40 rounded-lg overflow-hidden border border-surface-700 bg-surface-800">
          {attachment.type === 'image' ? (
            <img src={attachment.preview} alt={attachment.name} className="w-full h-full object-cover" />
          ) : (
            <video src={attachment.preview} className="w-full h-full object-cover" controls />
          )}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-surface-950/90 to-transparent px-2 py-1">
            <p className="text-[9px] text-surface-300 truncate">{attachment.name}</p>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-surface-700 bg-surface-800/50">
          <Icon size={16} className="text-surface-500" />
          <div>
            <p className="text-xs text-surface-300 truncate max-w-[200px]">{attachment.name}</p>
            {attachment.size && (
              <p className="text-[9px] text-surface-600">
                {(attachment.size / 1024 / 1024).toFixed(2)} MB
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.sender === 'user';
  const [showActions, setShowActions] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleEdit = () => {
    console.log('Edit message', message.id);
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this message?')) {
      console.log('Delete message', message.id);
    }
  };

  const handleRegenerate = () => {
    console.log('Regenerate response', message.id);
  };

  return (
    <div className="group animate-fade-in relative">
      <div className="flex items-start gap-3">
        <div className={`h-7 w-7 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5 ${
          isUser
            ? 'bg-surface-800 border border-surface-700'
            : 'bg-brand-600/20 border border-brand-600/30'
        }`}>
          {isUser
            ? <User size={14} className="text-surface-300" />
            : <Bot size={14} className="text-brand-400" />
          }
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-surface-300">
              {isUser ? 'You' : 'Dive AI'}
            </span>
            <span className="text-[10px] text-surface-600">
              {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
          <div className={`rounded-lg px-3.5 py-2.5 relative ${
            isUser
              ? 'bg-surface-900 border border-surface-800'
              : 'bg-surface-900/50 border border-surface-800/50'
          }`}>
            {message.attachments && message.attachments.length > 0 && (
              <div className="mb-2">
                {message.attachments.map((attachment, idx) => (
                  <AttachmentPreview key={idx} attachment={attachment} />
                ))}
              </div>
            )}
            {isUser ? (
              <p className="text-sm leading-relaxed text-surface-200 whitespace-pre-wrap">{message.content}</p>
            ) : (
              <MarkdownRenderer content={message.content} />
            )}

            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => setShowActions(!showActions)}
                className="p-1.5 rounded-lg bg-surface-800 hover:bg-surface-700 border border-surface-700 text-surface-400 hover:text-white transition-all"
                title="Message actions"
              >
                <MoreVertical size={12} />
              </button>

              {showActions && (
                <div className="absolute top-full right-0 mt-1 bg-surface-800 border border-surface-700 rounded-lg shadow-xl z-10 py-1 min-w-[140px] animate-scale-in">
                  <button
                    onClick={handleCopy}
                    className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-surface-300 hover:bg-surface-700 hover:text-white transition-colors"
                  >
                    {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                    <span>{copied ? 'Copied!' : 'Copy'}</span>
                  </button>
                  {isUser && (
                    <button
                      onClick={handleEdit}
                      className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-surface-300 hover:bg-surface-700 hover:text-white transition-colors"
                    >
                      <Edit3 size={12} />
                      <span>Edit</span>
                    </button>
                  )}
                  {!isUser && (
                    <button
                      onClick={handleRegenerate}
                      className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-surface-300 hover:bg-surface-700 hover:text-white transition-colors"
                    >
                      <RefreshCw size={12} />
                      <span>Regenerate</span>
                    </button>
                  )}
                  <button
                    onClick={handleDelete}
                    className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-rose-400 hover:bg-rose-500/10 transition-colors"
                  >
                    <Trash2 size={12} />
                    <span>Delete</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StreamingBubble({ content }: { content: string }) {
  return (
    <div className="animate-fade-in">
      <div className="flex items-start gap-3">
        <div className="h-7 w-7 rounded-md bg-brand-600/20 border border-brand-600/30 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Bot size={14} className="text-brand-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-surface-300">Dive AI</span>
            <span className="text-[10px] text-brand-500">typing...</span>
          </div>
          <div className="rounded-lg px-3.5 py-2.5 bg-surface-900/50 border border-surface-800/50">
            <MarkdownRenderer content={content} />
            <span className="inline-block w-1.5 h-4 bg-brand-400 animate-pulse ml-0.5 align-middle" />
          </div>
        </div>
      </div>
    </div>
  );
}

const THINKING_MESSAGES = [
  'Reading your message...',
  'Understanding the context...',
  'Thinking through the problem...',
  'Considering different approaches...',
  'Formulating a response...',
  'Organizing my thoughts...',
  'Almost ready...',
];

function ThinkingIndicator() {
  const [messageIndex, setMessageIndex] = useState(0);
  const [dots, setDots] = useState('');

  useEffect(() => {
    const dotsInterval = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return '';
        return prev + '.';
      });
    }, 400);

    const messageInterval = setInterval(() => {
      setMessageIndex(prev => (prev + 1) % THINKING_MESSAGES.length);
    }, 3000);

    return () => {
      clearInterval(dotsInterval);
      clearInterval(messageInterval);
    };
  }, []);

  return (
    <div className="animate-fade-in">
      <div className="flex items-start gap-3">
        <div className="h-7 w-7 rounded-md bg-brand-600/20 border border-brand-600/30 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Bot size={14} className="text-brand-400 animate-pulse" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-surface-300">Dive AI</span>
          </div>
          <div className="inline-flex items-center gap-2 rounded-lg px-4 py-2.5 bg-surface-900/50 border border-surface-800/50">
            <Brain size={14} className="text-brand-400 animate-pulse" />
            <span className="text-sm text-surface-400">
              {THINKING_MESSAGES[messageIndex]}{dots}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function MessageList({ messages, loading, streamingContent }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, streamingContent]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
      <div className="max-w-3xl mx-auto space-y-4">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {streamingContent && <StreamingBubble content={streamingContent} />}
        {loading && !streamingContent && <ThinkingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
