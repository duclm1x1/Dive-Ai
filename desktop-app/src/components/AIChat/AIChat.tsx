import React, { useState, useRef, useEffect, useCallback } from 'react';
import './AIChat.css';

// ── Types ────────────────────────────────────────────
interface AIChatProps {
    conversationId?: string | null;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    model?: string;
    latency_ms?: number;
    actions?: ActionResult[];
    attachments?: FileAttachment[];
    thinking?: string;
    selfHealRounds?: number;
}

interface ActionResult {
    action: string;
    success: boolean;
    output: string;
    error: string;
}

interface FileAttachment {
    name: string;
    size: number;
    content: string;
}

interface ModelInfo {
    id: string;
    name: string;
    model: string;
    vendor: string;
    provider_id: string;
    provider_name: string;
    thinking: boolean;
    priority: number;
    latency_ms: number;
    status: string;
}

// ── Component ────────────────────────────────────────
function AIChat({ conversationId: externalConvId }: AIChatProps) {
    // State
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [models, setModels] = useState<Record<string, ModelInfo[]>>({});
    const [selectedModel, setSelectedModel] = useState<string>(
        localStorage.getItem('dive_selected_model') || ''
    );
    const [showModelSelector, setShowModelSelector] = useState(false);
    const [defaultModel, setDefaultModel] = useState<string>('');
    const [isDragging, setIsDragging] = useState(false);
    const [attachedFiles, setAttachedFiles] = useState<FileAttachment[]>([]);
    const [conversationId, setConversationId] = useState<string | null>(
        externalConvId || localStorage.getItem('dive_conversation_id')
    );
    const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

    // Refs
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const selectorRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // ── Effects ──────────────────────────────────────

    // Scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => { scrollToBottom(); }, [messages]);

    // Load models + history on mount
    useEffect(() => {
        loadModels();
        loadConversationHistory();
    }, []);

    // React to external convId changes
    useEffect(() => {
        if (externalConvId && externalConvId !== conversationId) {
            setConversationId(externalConvId);
            loadConversationById(externalConvId);
        }
    }, [externalConvId]);

    // Close model selector on outside click
    useEffect(() => {
        const handleClick = (e: MouseEvent) => {
            if (selectorRef.current && !selectorRef.current.contains(e.target as Node)) {
                setShowModelSelector(false);
            }
        };
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px';
        }
    }, [input]);

    // ── Data Loading ─────────────────────────────────

    const loadConversationHistory = async () => {
        try {
            const convId = conversationId;
            if (!convId) return;
            await loadConversationById(convId);
        } catch (e) {
            console.error('Failed to load conversation history:', e);
        }
    };

    const loadConversationById = async (convId: string) => {
        try {
            const result = await window.diveAPI.gateway.request(
                `/conversations/${convId}/messages`
            );
            if (result.messages && result.messages.length > 0) {
                const loaded: Message[] = result.messages.map((m: any) => ({
                    role: m.role,
                    content: m.content,
                    timestamp: new Date(m.timestamp || m.created_at),
                    model: m.model,
                    latency_ms: m.latency_ms,
                    thinking: m.thinking,
                    actions: m.actions,
                }));
                setMessages(loaded);
            } else {
                setMessages([]);
            }
        } catch (e) {
            console.error('Failed to load conversation:', e);
            setMessages([]);
        }
    };

    const loadModels = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/models/list');
            if (result.groups) {
                setModels(result.groups);
                setDefaultModel(result.default_model || '');
                if (!selectedModel && result.default_model) {
                    setSelectedModel(result.default_model);
                }
            }
        } catch (e) {
            console.error('Failed to load models:', e);
        }
    };

    // ── Model Selector ───────────────────────────────

    const getStatusColor = (model: ModelInfo) => {
        if (model.status === 'no_key' || model.status === 'failed') return 'status-red';
        if (model.latency_ms > 0 && model.latency_ms < 500) return 'status-green';
        if (model.latency_ms >= 500 && model.latency_ms < 1500) return 'status-blue';
        if (model.latency_ms >= 1500) return 'status-red';
        return 'status-unknown';
    };

    const getSelectedModelName = () => {
        for (const group of Object.values(models)) {
            for (const m of group) {
                if (m.id === selectedModel) return m.name;
            }
        }
        return 'Select Model';
    };

    const selectModel = (modelId: string) => {
        setSelectedModel(modelId);
        localStorage.setItem('dive_selected_model', modelId);
        setShowModelSelector(false);
    };

    // ── File Handling ────────────────────────────────

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback(async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        const files = Array.from(e.dataTransfer.files);
        for (const file of files) {
            await addFileAttachment(file);
        }
    }, []);

    const addFileAttachment = async (file: File) => {
        try {
            const text = await file.text();
            setAttachedFiles(prev => [...prev, {
                name: file.name,
                size: file.size,
                content: text.substring(0, 10000)
            }]);
        } catch {
            setAttachedFiles(prev => [...prev, {
                name: file.name,
                size: file.size,
                content: `[Binary file: ${file.name}, ${file.size} bytes]`
            }]);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            Array.from(e.target.files).forEach(addFileAttachment);
        }
    };

    const removeFile = (index: number) => {
        setAttachedFiles(prev => prev.filter((_, i) => i !== index));
    };

    // ── Clipboard ────────────────────────────────────

    const copyToClipboard = (text: string, idx: number) => {
        navigator.clipboard.writeText(text).then(() => {
            setCopiedIdx(idx);
            setTimeout(() => setCopiedIdx(null), 2000);
        });
    };

    // ── Message Sending ──────────────────────────────

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        let messageContent = input.trim();

        // Append file contents
        if (attachedFiles.length > 0) {
            const fileContext = attachedFiles.map(f =>
                `\n\n📎 File: ${f.name} (${f.size} bytes)\n\`\`\`\n${f.content}\n\`\`\``
            ).join('\n');
            messageContent += fileContext;
        }

        const userMessage: Message = {
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
            attachments: attachedFiles.length > 0 ? [...attachedFiles] : undefined
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setAttachedFiles([]);
        setIsLoading(true);

        try {
            const result = await window.diveAPI.gateway.chat(messageContent, {
                model_id: selectedModel || undefined,
                conversation_id: conversationId || undefined
            });

            if (result.conversation_id) {
                setConversationId(result.conversation_id);
                localStorage.setItem('dive_conversation_id', result.conversation_id);
            }

            const assistantMessage: Message = {
                role: 'assistant',
                content: result.response || result.error || 'No response',
                timestamp: new Date(),
                model: result.model,
                latency_ms: result.latency_ms,
                actions: result.actions || [],
                thinking: result.thinking || undefined,
                selfHealRounds: (result as any).self_heal_rounds || 0
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Error: ${error}`,
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // ── Markdown Renderer ────────────────────────────

    const renderContent = (content: string, msgIdx: number) => {
        // Split by code blocks
        const parts = content.split(/(```[\s\S]*?```)/g);
        let codeBlockCount = 0;

        return parts.map((part, i) => {
            // Code block
            if (part.startsWith('```')) {
                const lines = part.slice(3, -3).split('\n');
                const lang = lines[0].trim();
                const code = lang ? lines.slice(1).join('\n') : lines.join('\n');
                const blockIdx = codeBlockCount++;
                const globalIdx = msgIdx * 1000 + blockIdx;
                const isLong = code.split('\n').length > 20;

                return (
                    <CodeBlock
                        key={i}
                        lang={lang}
                        code={code}
                        isLong={isLong}
                        isCopied={copiedIdx === globalIdx}
                        onCopy={() => copyToClipboard(code, globalIdx)}
                    />
                );
            }

            // Regular text with inline formatting
            return (
                <span key={i}>
                    {part.split('\n').map((line, j) => {
                        const formatted = formatLine(line);
                        return (
                            <React.Fragment key={j}>
                                <span dangerouslySetInnerHTML={{ __html: formatted }} />
                                {j < part.split('\n').length - 1 && <br />}
                            </React.Fragment>
                        );
                    })}
                </span>
            );
        });
    };

    const formatLine = (line: string): string => {
        // Headers
        if (line.startsWith('### ')) return `<strong style="font-size:0.95em;color:var(--accent)">${line.slice(4)}</strong>`;
        if (line.startsWith('## ')) return `<strong style="font-size:1.05em;color:var(--text-primary)">${line.slice(3)}</strong>`;
        if (line.startsWith('# ')) return `<strong style="font-size:1.15em;color:var(--text-primary)">${line.slice(2)}</strong>`;

        // Bullet points
        if (line.match(/^[\s]*[-*]\s/)) {
            const content = line.replace(/^[\s]*[-*]\s/, '');
            return `<span style="padding-left:16px;display:inline-block">• ${content}</span>`;
        }

        // Numbered lists
        if (line.match(/^[\s]*\d+\.\s/)) {
            return `<span style="padding-left:16px;display:inline-block">${line}</span>`;
        }

        // Bold
        let formatted = line.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        // Italic
        formatted = formatted.replace(/\*(.*?)\*/g, '<i>$1</i>');
        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
        // Links
        formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color:var(--accent);text-decoration:underline">$1</a>');
        // Action icons
        formatted = formatted.replace(/^(✅|❌|⚠️|🔧|📎|💡|🤿)/, '<span class="action-icon">$1</span>');
        // Horizontal rule
        if (line.match(/^---+$/)) return '<hr style="border:none;border-top:1px solid var(--glass-border);margin:8px 0"/>';

        return formatted;
    };

    // ── Code Block Component ─────────────────────────

    const CodeBlock = ({ lang, code, isLong, isCopied, onCopy }: {
        lang: string;
        code: string;
        isLong: boolean;
        isCopied: boolean;
        onCopy: () => void;
    }) => {
        const [collapsed, setCollapsed] = useState(isLong);

        return (
            <div className="code-block">
                <div className="code-header">
                    {lang && <span className="code-lang">{lang}</span>}
                    <div className="code-actions">
                        {isLong && (
                            <button className="code-action-btn" onClick={() => setCollapsed(!collapsed)}>
                                {collapsed ? '▸ Expand' : '▾ Collapse'}
                            </button>
                        )}
                        <button
                            className={`code-action-btn copy-btn ${isCopied ? 'copied' : ''}`}
                            onClick={onCopy}
                        >
                            {isCopied ? '✓ Copied' : '⎘ Copy'}
                        </button>
                    </div>
                </div>
                <pre className={collapsed ? 'code-collapsed' : ''}>
                    <code>{collapsed ? code.split('\n').slice(0, 5).join('\n') + '\n...' : code}</code>
                </pre>
            </div>
        );
    };

    // ── Thinking Bubble ──────────────────────────────

    const ThinkingBubble = ({ thinking }: { thinking: string }) => {
        const [expanded, setExpanded] = React.useState(false);
        if (!thinking) return null;

        return (
            <div className={`thinking-bubble ${expanded ? 'expanded' : ''}`}>
                <button className="thinking-toggle" onClick={() => setExpanded(!expanded)}>
                    <span className="thinking-icon">🧠</span>
                    <span>AI Thinking</span>
                    <span className="thinking-arrow">{expanded ? '▾' : '▸'}</span>
                </button>
                {expanded && (
                    <div className="thinking-content">
                        {thinking.split('\n').map((line, i) => (
                            <React.Fragment key={i}>
                                {line}
                                {i < thinking.split('\n').length - 1 && <br />}
                            </React.Fragment>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    // ── Action Results ───────────────────────────────

    const renderActions = (actions: ActionResult[]) => {
        if (!actions || actions.length === 0) return null;

        return (
            <div className="action-results">
                <div className="action-results-header">🔧 Actions Executed</div>
                {actions.map((action, i) => (
                    <div key={i} className={`action-result ${action.success ? 'success' : 'failed'}`}>
                        <div className="action-result-header">
                            <span className="action-icon">{action.success ? '✅' : '❌'}</span>
                            <span className="action-name">{action.action}</span>
                        </div>
                        {action.output && (
                            <pre className="action-output">{action.output.substring(0, 500)}</pre>
                        )}
                        {action.error && (
                            <div className="action-error">⚠️ {action.error}</div>
                        )}
                    </div>
                ))}
            </div>
        );
    };

    // ── Render ────────────────────────────────────────

    return (
        <div
            className={`chat-container ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            {/* Drag overlay */}
            {isDragging && (
                <div className="drag-overlay">
                    <div className="drag-icon">📁</div>
                    <div className="drag-text">Drop files here</div>
                </div>
            )}

            {/* Model Selector Bar */}
            <div className="model-bar" ref={selectorRef}>
                <button
                    className="model-selector-btn"
                    onClick={() => setShowModelSelector(!showModelSelector)}
                >
                    <span className="model-icon">🤖</span>
                    <span className="model-name">{getSelectedModelName()}</span>
                    <span className={`model-arrow ${showModelSelector ? 'open' : ''}`}>▾</span>
                </button>

                {showModelSelector && (
                    <div className="model-dropdown">
                        {Object.entries(models).map(([vendor, vendorModels]) => (
                            <div key={vendor} className="vendor-group">
                                <div className="vendor-header">{vendor}</div>
                                {vendorModels.map(m => (
                                    <button
                                        key={`${m.provider_id}-${m.id}`}
                                        className={`model-item ${m.id === selectedModel ? 'selected' : ''}`}
                                        onClick={() => selectModel(m.id)}
                                    >
                                        <span className={`status-dot ${getStatusColor(m)}`}></span>
                                        <span className="model-item-name">
                                            {m.name}
                                            {m.thinking && <span className="thinking-badge">🧠</span>}
                                        </span>
                                        <span className="model-provider">{m.provider_name}</span>
                                        <span className="model-latency">
                                            {m.latency_ms > 0 ? `${Math.round(m.latency_ms)}ms` : '—'}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        ))}
                        <div className="model-dropdown-footer">
                            <button className="refresh-btn" onClick={loadModels}>↻ Refresh</button>
                        </div>
                    </div>
                )}
            </div>

            {/* Messages */}
            <div className="messages">
                {messages.length === 0 && (
                    <div className="welcome">
                        <div className="welcome-logo">🤿</div>
                        <h2>Dive AI</h2>
                        <p>Your autonomous AI assistant — I can control your PC, debug myself, and write code!</p>
                        <div className="suggestions">
                            <button onClick={() => setInput('What can you do?')}>💬 What can you do?</button>
                            <button onClick={() => setInput('Debug yourself — check your gateway server')}>🔧 Self-debug</button>
                            <button onClick={() => setInput('Write a Python script that...')}>⚡ Write code</button>
                            <button onClick={() => setInput('Take a screenshot of my screen')}>📸 Screenshot</button>
                            <button onClick={() => setInput('List the files in your backend directory')}>📁 List files</button>
                            <button onClick={() => setInput('Search the web for...')}>🔍 Search</button>
                        </div>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        {/* Avatar */}
                        <div className="msg-avatar">
                            {msg.role === 'user' ? '👤' : '🤿'}
                        </div>

                        <div className="msg-body">
                            {/* File attachments for user messages */}
                            {msg.attachments && msg.attachments.length > 0 && (
                                <div className="message-attachments">
                                    {msg.attachments.map((f, i) => (
                                        <div key={i} className="attachment-chip">
                                            📎 {f.name} <span className="attachment-size">({Math.round(f.size / 1024)}KB)</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Message content */}
                            <div className="message-content">
                                {msg.role === 'assistant' ? renderContent(msg.content, idx) : msg.content}
                            </div>

                            {/* Thinking bubble */}
                            {msg.thinking && <ThinkingBubble thinking={msg.thinking} />}

                            {/* Action results */}
                            {msg.actions && msg.actions.length > 0 && renderActions(msg.actions)}

                            {/* Metadata */}
                            <div className="message-meta">
                                <span className="message-time">
                                    {msg.timestamp.toLocaleTimeString()}
                                </span>
                                {msg.model && (
                                    <span className="message-model">
                                        {msg.model}{msg.latency_ms ? ` • ${Math.round(msg.latency_ms)}ms` : ''}
                                        {msg.selfHealRounds ? ` • 🔄${msg.selfHealRounds}` : ''}
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                    <div className="message assistant loading">
                        <div className="msg-avatar">🤿</div>
                        <div className="msg-body">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Attached files preview */}
            {attachedFiles.length > 0 && (
                <div className="attached-files-bar">
                    {attachedFiles.map((f, i) => (
                        <div key={i} className="attached-file-chip">
                            <span>📎 {f.name}</span>
                            <button className="remove-file" onClick={() => removeFile(i)}>✕</button>
                        </div>
                    ))}
                </div>
            )}

            {/* Input Area */}
            <div className="input-area">
                <button
                    className="attach-btn"
                    onClick={() => fileInputRef.current?.click()}
                    title="Attach file"
                >
                    📎
                </button>
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    style={{ display: 'none' }}
                    onChange={handleFileSelect}
                />
                <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message... (Shift+Enter for newline)"
                    rows={1}
                />
                <button
                    className="send-btn"
                    onClick={sendMessage}
                    disabled={isLoading || !input.trim()}
                >
                    <span className="send-icon">↑</span>
                </button>
            </div>
        </div>
    );
}

export default AIChat;
