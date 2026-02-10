import React, { useState, useEffect } from 'react';
import AIChat from './components/AIChat/AIChat';
import BrowserView from './components/Browser/BrowserView';
import CodeEditor from './components/CodeEditor/CodeEditor';
import Terminal from './components/Terminal/Terminal';
import DesktopController from './components/Desktop/DesktopController';
import Calculator from './components/Calculator/Calculator';
import Settings from './components/Settings/Settings';
import logoImg from './assets/logo.png';
import './design-system.css';

type Tab = 'chat' | 'browser' | 'code' | 'terminal' | 'desktop' | 'calculator' | 'settings';

function App() {
    const [activeTab, setActiveTab] = useState<Tab>('chat');
    const [gatewayStatus, setGatewayStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
    const [automationAllowed, setAutomationAllowed] = useState(false);

    useEffect(() => {
        checkGateway();
        const interval = setInterval(checkGateway, 30000);
        return () => clearInterval(interval);
    }, []);

    // Global F3 hotkey for automation toggle
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'F3') {
                e.preventDefault();
                toggleAutomation();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [automationAllowed]);

    const checkGateway = async () => {
        try {
            const result = await window.diveAPI.gateway.health();
            setGatewayStatus(result.status === 'healthy' ? 'connected' : 'disconnected');
        } catch {
            setGatewayStatus('disconnected');
        }
    };

    const toggleAutomation = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/automation/toggle', {});
            setAutomationAllowed(result.allowed);
        } catch {}
    };

    const tabs: { id: Tab; icon: string; label: string }[] = [
        { id: 'chat', icon: '💬', label: 'Chat' },
        { id: 'browser', icon: '🌐', label: 'Browser' },
        { id: 'code', icon: '📝', label: 'Code' },
        { id: 'terminal', icon: '⌨️', label: 'Terminal' },
        { id: 'desktop', icon: '🖥️', label: 'Desktop' },
        { id: 'calculator', icon: '🧮', label: 'Calculator' },
    ];

    const renderContent = () => {
        switch (activeTab) {
            case 'chat': return <AIChat />;
            case 'browser': return <BrowserView />;
            case 'code': return <CodeEditor />;
            case 'terminal': return <Terminal />;
            case 'desktop': return <DesktopController />;
            case 'calculator': return <Calculator />;
            case 'settings': return <Settings />;
        }
    };

    return (
        <div className="app">
            <aside className="sidebar">
                <div className="logo">
                    <img src={logoImg} alt="Dive AI" style={{width: '48px', height: '48px', borderRadius: '8px'}} />
                </div>

                <nav className="nav-tabs">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                            title={tab.label}
                        >
                            <span className="tab-icon">{tab.icon}</span>
                            <span className="tab-label">{tab.label}</span>
                        </button>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    {/* Automation toggle indicator */}
                    <button
                        className={`automation-indicator ${automationAllowed ? 'allowed' : ''}`}
                        onClick={toggleAutomation}
                        title={`PC Control: ${automationAllowed ? 'ON' : 'OFF'} (F3)`}
                    >
                        <span>{automationAllowed ? '🟢' : '🔴'}</span>
                        <span className="automation-label">F3</span>
                    </button>

                    {/* Settings button */}
                    <button
                        className={`tab-btn settings-btn ${activeTab === 'settings' ? 'active' : ''}`}
                        onClick={() => setActiveTab('settings')}
                        title="Settings"
                    >
                        <span className="tab-icon">⚙️</span>
                        <span className="tab-label">Settings</span>
                    </button>

                    <div className={`status-indicator ${gatewayStatus}`} title={`Gateway: ${gatewayStatus}`}>
                        <span className="status-dot"></span>
                        <span className="status-text">{gatewayStatus}</span>
                    </div>
                </div>
            </aside>

            <main className="content">
                <header className="header">
                    <h1>Dive AI</h1>
                    <span className="subtitle">
                        {activeTab === 'settings' ? 'Settings' : tabs.find(t => t.id === activeTab)?.label}
                    </span>
                </header>

                <div className="content-area">
                    {renderContent()}
                </div>
            </main>
        </div>
    );
}

export default App;
