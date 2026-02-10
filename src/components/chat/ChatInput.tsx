import { useState, useRef, useEffect } from 'react';
import { ArrowUp, Loader2, ChevronDown, RefreshCw, Mic, MicOff, Paperclip, X, FileVideo, FileAudio, Image as ImageIcon } from 'lucide-react';
import {
  getStoredModels,
  getLlmConfig,
  setStoredModels,
  fetchModelsFromApi,
  groupModelsByCategory,
  getLatencyInfo,
  setLatencyInfo,
  getProviderLabel,
  type ModelInfo,
  type LatencyInfo,
} from '../../lib/llmConfig';
import type { FileAttachment } from '../../types';

interface ChatInputProps {
  onSend: (content: string, attachments?: FileAttachment[]) => void;
  disabled?: boolean;
  loading?: boolean;
  model?: string;
  onModelChange?: (model: string) => void;
}

const DEFAULT_MODELS: ModelInfo[] = [
  { id: 'gpt-4o', label: 'GPT-4o', provider: 'openai', category: 'OpenAI', tier: 90 },
  { id: 'gpt-4o-mini', label: 'GPT-4o Mini', provider: 'openai', category: 'OpenAI', tier: 80 },
];

const ACCEPTED_FILE_TYPES = {
  'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
  'video/*': ['.mp4', '.webm', '.mov'],
  'audio/*': ['.mp3', '.wav', '.m4a', '.ogg'],
};

export function ChatInput({ onSend, disabled, loading, model = 'gpt-4o-mini', onModelChange }: ChatInputProps) {
  const [value, setValue] = useState('');
  const [showModels, setShowModels] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>(() => {
    const stored = getStoredModels();
    return stored.length > 0 ? stored : DEFAULT_MODELS;
  });
  const [latency, setLatency] = useState<LatencyInfo | null>(getLatencyInfo);
  const [fetchingModels, setFetchingModels] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px';
    }
  }, [value]);

  useEffect(() => {
    const handleModelsChange = (e: Event) => {
      const customEvent = e as CustomEvent<ModelInfo[]>;
      if (customEvent.detail && customEvent.detail.length > 0) {
        setModels(customEvent.detail);
      }
    };

    const handleLatencyChange = (e: Event) => {
      const customEvent = e as CustomEvent<LatencyInfo>;
      if (customEvent.detail) {
        setLatency(customEvent.detail);
      }
    };

    window.addEventListener('llm-models-changed', handleModelsChange);
    window.addEventListener('llm-latency-changed', handleLatencyChange);
    return () => {
      window.removeEventListener('llm-models-changed', handleModelsChange);
      window.removeEventListener('llm-latency-changed', handleLatencyChange);
    };
  }, []);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          }
        }

        if (finalTranscript) {
          setValue(prev => prev + finalTranscript);
        }
      };

      recognitionRef.current.onerror = () => {
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if ((!trimmed && attachments.length === 0) || disabled || loading) return;
    onSend(trimmed, attachments.length > 0 ? attachments : undefined);
    setValue('');
    setAttachments([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFetchModels = async () => {
    const config = getLlmConfig();
    if (!config.apiKey || !config.baseUrl) return;

    setFetchingModels(true);
    try {
      const { models: fetchedModels, latency: responseLatency } = await fetchModelsFromApi(config.baseUrl, config.apiKey);
      if (fetchedModels.length > 0) {
        const modelsWithProvider = fetchedModels.map(m => ({ ...m, provider: config.provider }));
        setModels(modelsWithProvider);
        setStoredModels(modelsWithProvider);

        const latencyInfo: LatencyInfo = {
          latency: responseLatency,
          timestamp: Date.now(),
          provider: config.provider,
        };
        setLatency(latencyInfo);
        setLatencyInfo(latencyInfo);
      }
    } catch {
      // Silent fail
    }
    setFetchingModels(false);
  };

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newAttachments: FileAttachment[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const type = file.type.startsWith('image/') ? 'image'
        : file.type.startsWith('video/') ? 'video'
        : file.type.startsWith('audio/') ? 'audio'
        : null;

      if (type) {
        const attachment: FileAttachment = {
          file,
          type,
          name: file.name,
          size: file.size,
        };

        if (type === 'image' || type === 'video') {
          const reader = new FileReader();
          reader.onload = (e) => {
            attachment.preview = e.target?.result as string;
            setAttachments(prev => [...prev.filter(a => a.name !== file.name), attachment]);
          };
          reader.readAsDataURL(file);
        }

        newAttachments.push(attachment);
      }
    }

    if (newAttachments.length > 0) {
      setAttachments(prev => [...prev, ...newAttachments]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'video': return FileVideo;
      case 'audio': return FileAudio;
      case 'image': return ImageIcon;
      default: return Paperclip;
    }
  };

  const currentModel = models.find((m) => m.id === model) || models[0] || { id: model, label: model, provider: 'custom', category: 'Other', tier: 50 };
  const groupedModels = groupModelsByCategory(models);
  const config = getLlmConfig();
  const canFetch = config.apiKey && config.baseUrl;
  const providerLabel = getProviderLabel(config.provider);

  return (
    <div className="border-t border-surface-800 bg-surface-950 p-3">
      <div className="max-w-3xl mx-auto">
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`relative rounded-xl transition-all ${
            isDragging ? 'ring-2 ring-brand-500 bg-brand-500/5' : ''
          }`}
        >
          {isDragging && (
            <div className="absolute inset-0 flex items-center justify-center bg-surface-900/95 rounded-xl z-10 border-2 border-dashed border-brand-500">
              <div className="text-center">
                <Paperclip size={32} className="text-brand-400 mx-auto mb-2" />
                <p className="text-sm text-brand-400 font-medium">Drop files here</p>
                <p className="text-xs text-surface-500 mt-1">Images, videos, or audio files</p>
              </div>
            </div>
          )}

          {attachments.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-2">
              {attachments.map((attachment, index) => {
                const Icon = getFileIcon(attachment.type);
                return (
                  <div key={index} className="relative group">
                    {attachment.preview ? (
                      <div className="relative w-20 h-20 rounded-lg overflow-hidden border border-surface-700 bg-surface-800">
                        {attachment.type === 'image' ? (
                          <img src={attachment.preview} alt="" className="w-full h-full object-cover" />
                        ) : (
                          <video src={attachment.preview} className="w-full h-full object-cover" />
                        )}
                        <button
                          onClick={() => removeAttachment(index)}
                          className="absolute top-1 right-1 w-5 h-5 rounded-full bg-surface-950/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Remove file"
                        >
                          <X size={12} className="text-surface-300" />
                        </button>
                      </div>
                    ) : (
                      <div className="relative w-20 h-20 rounded-lg border border-surface-700 bg-surface-800 flex flex-col items-center justify-center">
                        <Icon size={20} className="text-surface-500 mb-1" />
                        <span className="text-[9px] text-surface-600 truncate max-w-full px-1">
                          {attachment.name}
                        </span>
                        <button
                          onClick={() => removeAttachment(index)}
                          className="absolute top-1 right-1 w-5 h-5 rounded-full bg-surface-950/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Remove file"
                        >
                          <X size={12} className="text-surface-300" />
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          <div className="flex items-end gap-2 bg-surface-900 border border-surface-800 rounded-xl px-3 py-2.5 focus-within:border-surface-700 transition-all">
            <div className="flex items-center gap-1 pb-0.5">
              <span className="text-brand-500 font-mono text-sm font-semibold select-none">&gt;_</span>
            </div>
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Dive AI anything... (Shift+Enter for new line)"
              disabled={disabled}
              rows={1}
              className="flex-1 bg-transparent text-surface-100 placeholder-surface-600 resize-none focus:outline-none text-sm leading-relaxed max-h-40 font-mono"
            />
            <div className="flex items-center gap-1">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept={Object.values(ACCEPTED_FILE_TYPES).flat().join(',')}
                onChange={(e) => handleFileSelect(e.target.files)}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled}
                className="flex-shrink-0 h-7 w-7 rounded-lg bg-surface-800 hover:bg-surface-700 disabled:bg-surface-800 disabled:text-surface-600 text-surface-300 hover:text-white flex items-center justify-center transition-all duration-200 disabled:cursor-not-allowed"
                title="Attach files (images, videos, audio)"
              >
                <Paperclip size={14} />
              </button>
              <button
                onClick={toggleVoiceInput}
                disabled={disabled}
                className={`flex-shrink-0 h-7 w-7 rounded-lg flex items-center justify-center transition-all duration-200 disabled:cursor-not-allowed ${
                  isRecording
                    ? 'bg-rose-600 hover:bg-rose-500 text-white animate-pulse'
                    : 'bg-surface-800 hover:bg-surface-700 text-surface-300 hover:text-white'
                }`}
                title={isRecording ? 'Stop recording' : 'Start voice input'}
              >
                {isRecording ? <MicOff size={14} /> : <Mic size={14} />}
              </button>
              <button
                onClick={handleSubmit}
                disabled={(!value.trim() && attachments.length === 0) || disabled || loading}
                className="flex-shrink-0 h-7 w-7 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:bg-surface-800 disabled:text-surface-600 text-white flex items-center justify-center transition-all duration-200 disabled:cursor-not-allowed"
                title="Send message (Enter)"
              >
                {loading ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <ArrowUp size={14} />
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between mt-2 px-1">
          <div className="relative">
            <button
              onClick={() => setShowModels(!showModels)}
              className="flex items-center gap-1.5 text-[11px] text-surface-500 hover:text-surface-300 transition-colors"
              title="Change AI model"
            >
              <span className="font-medium text-surface-400">{currentModel.label}</span>
              <span className="text-surface-600">-</span>
              <span>{providerLabel}</span>
              {latency && (
                <>
                  <span className="text-surface-600">-</span>
                  <span className={`font-mono ${latency.latency < 200 ? 'text-emerald-400' : latency.latency < 500 ? 'text-amber-400' : 'text-rose-400'}`}>
                    {latency.latency}ms
                  </span>
                </>
              )}
              <ChevronDown size={10} className={showModels ? 'rotate-180 transition-transform' : 'transition-transform'} />
            </button>
            {showModels && (
              <div className="absolute bottom-full left-0 mb-1 bg-surface-900 border border-surface-800 rounded-lg shadow-xl z-50 min-w-[300px] max-h-80 overflow-hidden animate-scale-in">
                <div className="flex items-center justify-between px-3 py-2 border-b border-surface-800">
                  <span className="text-[10px] text-surface-500 uppercase tracking-wider">Select Model</span>
                  {canFetch && (
                    <button
                      onClick={handleFetchModels}
                      disabled={fetchingModels}
                      className="flex items-center gap-1 text-[10px] text-surface-500 hover:text-brand-400 transition-colors disabled:opacity-50"
                      title="Refresh model list"
                    >
                      <RefreshCw size={10} className={fetchingModels ? 'animate-spin' : ''} />
                      Refresh
                    </button>
                  )}
                </div>
                <div className="overflow-y-auto max-h-64 py-1">
                  {groupedModels.map((group) => (
                    <div key={group.category}>
                      <div className="px-3 py-1.5 text-[10px] text-surface-600 font-semibold uppercase tracking-wider bg-surface-800/50 sticky top-0">
                        {group.category}
                      </div>
                      {group.models.map((m) => (
                        <button
                          key={m.id}
                          onClick={() => {
                            onModelChange?.(m.id);
                            setShowModels(false);
                          }}
                          className={`w-full text-left px-3 py-2 text-xs hover:bg-surface-800 transition-colors ${
                            m.id === model ? 'text-brand-400 bg-brand-500/5' : 'text-surface-400'
                          }`}
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-medium truncate">{m.label}</span>
                            <span className="text-[10px] text-surface-600 flex-shrink-0">{providerLabel}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  ))}
                  {models.length === 0 && (
                    <div className="px-3 py-3 text-xs text-surface-500 text-center">
                      No models loaded.<br />
                      <span className="text-surface-600">Configure API in Settings.</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          <span className="text-[10px] text-surface-600">
            {isRecording ? 'Recording...' : 'Press Enter to send • Shift+Enter for new line'}
          </span>
        </div>
      </div>
    </div>
  );
}
