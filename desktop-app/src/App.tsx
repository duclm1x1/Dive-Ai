import React, { useState, useEffect, useCallback, useRef } from 'react';
import AIChat from './components/AIChat/AIChat';
import BrowserView from './components/Browser/BrowserView';
import CodeEditor from './components/CodeEditor/CodeEditor';
import Terminal from './components/Terminal/Terminal';
import DesktopController from './components/Desktop/DesktopController';
import Calculator from './components/Calculator/Calculator';
import Settings from './components/Settings/Settings';
import logoImg from './assets/logo.png';
import './design-system.css';
import './App.css';

// ── Types ────────────────────────────────────────────
type Tab = 'chat' | 'browser' | 'code' | 'terminal' | 'desktop' | 'calculator' | 'settings' | 'agent' | 'skills';

interface Conversation {
    id: string;
    title: string;
    message_count: number;
    created_at: string;
    updated_at: string;
}

// ── App ──────────────────────────────────────────────
function App() {
    // Navigation
    const [activeTab, setActiveTab] = useState<Tab>('chat');
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    // Gateway
    const [gatewayStatus, setGatewayStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
    const [automationAllowed, setAutomationAllowed] = useState(false);
    const [gatewayVersion, setGatewayVersion] = useState('');
    const [gatewayLatency, setGatewayLatency] = useState(0);

    // Conversations
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [activeConvId, setActiveConvId] = useState<string | null>(null);

    // Command palette
    const [showCommandPalette, setShowCommandPalette] = useState(false);
    const [commandQuery, setCommandQuery] = useState('');
    const commandInputRef = useRef<HTMLInputElement>(null);

    // ── Gateway health check ─────────────────────────
    useEffect(() => {
        checkGateway();
        loadConversations();
        const interval = setInterval(checkGateway, 30000);
        return () => clearInterval(interval);
    }, []);

    const checkGateway = async () => {
        try {
            const start = Date.now();
            const result = await window.diveAPI.gateway.health();
            const latency = Date.now() - start;
            setGatewayLatency(latency);
            setGatewayStatus(result.status === 'healthy' ? 'connected' : 'disconnected');
            if (result.version) setGatewayVersion(result.version);
        } catch {
            setGatewayStatus('disconnected');
        }
    };

    // ── Automation toggle (F3) ───────────────────────
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'F3') {
                e.preventDefault();
                toggleAutomation();
            }
            // Ctrl+K → Command palette
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                setShowCommandPalette(prev => !prev);
            }
            // Escape → Close command palette
            if (e.key === 'Escape') {
                setShowCommandPalette(false);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [automationAllowed]);

    const toggleAutomation = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/automation/toggle', {});
            setAutomationAllowed(result.allowed);
        } catch {}
    };

    // ── Conversations ────────────────────────────────
    const loadConversations = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/conversations', {});
            if (result.conversations) {
                setConversations(result.conversations);
            }
        } catch {}
    };

    const createNewChat = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/conversations', {
                method: 'POST',
                body: { title: 'New Chat' }
            });
            if (result.id) {
                setActiveConvId(result.id);
                setActiveTab('chat');
                loadConversations();
            }
        } catch {
            // Fallback: just switch to chat
            setActiveConvId(null);
            setActiveTab('chat');
        }
    };

    const deleteConversation = async (convId: string) => {
        try {
            await window.diveAPI.gateway.request(`/conversations/${convId}`, {
                method: 'DELETE'
            });
            if (activeConvId === convId) setActiveConvId(null);
            loadConversations();
        } catch {}
    };

    // ── Focus command palette input ──────────────────
    useEffect(() => {
        if (showCommandPalette && commandInputRef.current) {
            commandInputRef.current.focus();
        }
    }, [showCommandPalette]);

    // ── Tab config ───────────────────────────────────
    const navTabs: { id: Tab; icon: string; label: string; shortcut?: string }[] = [
        { id: 'chat', icon: '💬', label: 'Chat', shortcut: '1' },
        { id: 'code', icon: '⚡', label: 'Code', shortcut: '2' },
        { id: 'terminal', icon: '▶', label: 'Terminal', shortcut: '3' },
        { id: 'browser', icon: '🌐', label: 'Browser', shortcut: '4' },
        { id: 'desktop', icon: '🖥', label: 'Desktop', shortcut: '5' },
    ];

    const toolTabs: { id: Tab; icon: string; label: string }[] = [
        { id: 'calculator', icon: '📊', label: 'Calculator' },
        { id: 'agent', icon: '🤖', label: 'Agent' },
        { id: 'skills', icon: '🧩', label: 'Skills' },
    ];

    // ── Command palette commands ─────────────────────
    const commands = [
        { id: 'new-chat', label: 'New Chat', icon: '➕', action: createNewChat },
        { id: 'settings', label: 'Settings', icon: '⚙️', action: () => setActiveTab('settings') },
        ...navTabs.map(t => ({ id: t.id, label: t.label, icon: t.icon, action: () => setActiveTab(t.id) })),
        ...toolTabs.map(t => ({ id: t.id, label: t.label, icon: t.icon, action: () => setActiveTab(t.id) })),
    ];

    const filteredCommands = commandQuery
        ? commands.filter(c => c.label.toLowerCase().includes(commandQuery.toLowerCase()))
        : commands;

    // ── Render content ───────────────────────────────
    const renderContent = () => {
        switch (activeTab) {
            case 'chat': return <AIChat conversationId={activeConvId} />;
            case 'browser': return <BrowserView />;
            case 'code': return <CodeEditor />;
            case 'terminal': return <Terminal />;
            case 'desktop': return <DesktopController />;
            case 'calculator': return <Calculator />;
            case 'settings': return <Settings />;
            case 'agent': return <div className="placeholder-tab"><div className="placeholder-icon">🤖</div><h2>Agent Monitor</h2><p>Coming in V29.8 — Autonomous task monitoring</p></div>;
            case 'skills': return <div className="placeholder-tab"><div className="placeholder-icon">🧩</div><h2>Skills Hub</h2><p>Coming in V29.8 — Browse & execute 77+ skills</p></div>;
        }
    };

    // ── Format time ──────────────────────────────────
    const formatTime = (iso: string) => {
        try {
            const d = new Date(iso);
            const now = new Date();
            const diff = now.getTime() - d.getTime();
            if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
            if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
            return d.toLocaleDateString();
        } catch { return ''; }
    };

    return (
        <div className={`app ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            {/* ── SIDEBAR ── */}
            <aside className="sidebar">
                {/* Logo + collapse */}
                <div className="sidebar-header">
                    <div className="logo-area" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
                        <img src={logoImg} alt="Dive AI" className="logo-img" />
                        {!sidebarCollapsed && <span className="logo-text">Dive AI</span>}
                    </div>
                </div>

                {/* New Chat button */}
                <button className="new-chat-btn" onClick={createNewChat} title="New Chat (Ctrl+N)">
                    <span className="new-chat-icon">＋</span>
                    {!sidebarCollapsed && <span>New Chat</span>}
                </button>

                {/* Conversation list */}
                {!sidebarCollapsed && (
                    <div className="conversation-list">
                        {conversations.slice(0, 20).map(conv => (
                            <div
                                key={conv.id}
                                className={`conv-item ${activeConvId === conv.id ? 'active' : ''}`}
                                onClick={() => { setActiveConvId(conv.id); setActiveTab('chat'); }}
                            >
                                <span className="conv-title">{conv.title}</span>
                                <span className="conv-time">{formatTime(conv.updated_at)}</span>
                                <button
                                    className="conv-delete"
                                    onClick={(e) => { e.stopPropagation(); deleteConversation(conv.id); }}
                                    title="Delete"
                                >×</button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Nav tabs */}
                <div className="nav-divider"></div>
                <nav className="nav-tabs">
                    {navTabs.map(tab => (
                        <button
                            key={tab.id}
                            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                            title={`${tab.label}${tab.shortcut ? ` (Ctrl+${tab.shortcut})` : ''}`}
                        >
                            <span className="tab-icon">{tab.icon}</span>
                            {!sidebarCollapsed && <span className="tab-label">{tab.label}</span>}
                        </button>
                    ))}
                </nav>

                {/* Tools separator */}
                <div className="nav-divider"></div>
                <nav className="nav-tabs tools-section">
                    {toolTabs.map(tab => (
                        <button
                            key={tab.id}
                            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                            title={tab.label}
                        >
                            <span className="tab-icon">{tab.icon}</span>
                            {!sidebarCollapsed && <span className="tab-label">{tab.label}</span>}
                        </button>
                    ))}
                </nav>

                {/* Sidebar footer */}
                <div className="sidebar-footer">
                    {/* Automation toggle */}
                    <button
                        className={`footer-btn automation-btn ${automationAllowed ? 'allowed' : ''}`}
                        onClick={toggleAutomation}
                        title={`PC Control: ${automationAllowed ? 'ON' : 'OFF'} (F3)`}
                    >
                        <span className="footer-icon">{automationAllowed ? '🟢' : '🔴'}</span>
                        {!sidebarCollapsed && <span className="footer-label">F3</span>}
                    </button>

                    {/* Settings */}
                    <button
                        className={`footer-btn ${activeTab === 'settings' ? 'active' : ''}`}
                        onClick={() => setActiveTab('settings')}
                        title="Settings"
                    >
                        <span className="footer-icon">⚙️</span>
                        {!sidebarCollapsed && <span className="footer-label">Settings</span>}
                    </button>
                </div>
            </aside>

            {/* ── MAIN CONTENT ── */}
            <main className="content">
                <div className="content-area">
                    {renderContent()}
                </div>

                {/* Status bar */}
                <div className="status-bar">
                    <div className="status-left">
                        <span className={`gateway-status ${gatewayStatus}`}>
                            <span className="status-dot-mini"></span>
                            {gatewayStatus === 'connected' ? 'Gateway' : 'Offline'}
                        </span>
                        {gatewayLatency > 0 && (
                            <span className="latency">{gatewayLatency}ms</span>
                        )}
                        {gatewayVersion && (
                            <span className="version">v{gatewayVersion}</span>
                        )}
                    </div>
                    <div className="status-center">
                        <button className="cmd-palette-trigger" onClick={() => setShowCommandPalette(true)}>
                            <span>⌘K</span> Command Palette
                        </button>
                    </div>
                    <div className="status-right">
                        <span className="tab-indicator">{navTabs.find(t => t.id === activeTab)?.label || toolTabs.find(t => t.id === activeTab)?.label || 'Settings'}</span>
                    </div>
                </div>
            </main>

            {/* ── COMMAND PALETTE ── */}
            {showCommandPalette && (
                <div className="cmd-overlay" onClick={() => setShowCommandPalette(false)}>
                    <div className="cmd-palette" onClick={e => e.stopPropagation()}>
                        <input
                            ref={commandInputRef}
                            className="cmd-input"
                            placeholder="Type a command..."
                            value={commandQuery}
                            onChange={e => setCommandQuery(e.target.value)}
                            onKeyDown={e => {
                                if (e.key === 'Enter' && filteredCommands.length > 0) {
                                    filteredCommands[0].action();
                                    setShowCommandPalette(false);
                                    setCommandQuery('');
                                }
                            }}
                        />
                        <div className="cmd-list">
                            {filteredCommands.map(cmd => (
                                <button
                                    key={cmd.id}
                                    className="cmd-item"
                                    onClick={() => {
                                        cmd.action();
                                        setShowCommandPalette(false);
                                        setCommandQuery('');
                                    }}
                                >
                                    <span className="cmd-icon">{cmd.icon}</span>
                                    <span className="cmd-label">{cmd.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
