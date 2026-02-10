import React, { useState, useEffect } from 'react';
import './Settings.css';

interface Provider {
    id: string;
    name: string;
    base_url: string;
    api_key_env: string;
    has_key: boolean;
    connected: boolean;
    latency_ms: number;
    model_count: number;
    is_primary: boolean;
}

interface AppSettings {
    app: { name: string; version: string };
    server: { host: string; port: number };
    features: Record<string, boolean>;
    providers: Provider[];
    routing: any;
}

interface StorageStats {
    path: string;
    used_bytes: number;
    used_mb: number;
    file_count: number;
    conversation_count: number;
    memory_initialized: boolean;
}

interface MemoryStatus {
    initialized: boolean;
    short_term_messages: number;
    max_short_term: number;
    long_term_facts: number;
    long_term_topics: number;
    preferences: Record<string, string>;
}

function Settings() {
    const [settings, setSettings] = useState<AppSettings | null>(null);
    const [activeSection, setActiveSection] = useState('providers');
    const [testResults, setTestResults] = useState<Record<string, any>>({});
    const [automationAllowed, setAutomationAllowed] = useState(false);

    // Storage state
    const [storageStats, setStorageStats] = useState<StorageStats | null>(null);
    const [memoryStatus, setMemoryStatus] = useState<MemoryStatus | null>(null);
    const [clearConfirm, setClearConfirm] = useState(false);

    // Connections state
    const [connections, setConnections] = useState<Record<string, any>>({});
    const [editingKeys, setEditingKeys] = useState<Record<string, string>>({});
    const [editingUrls, setEditingUrls] = useState<Record<string, string>>({});
    const [saveStatus, setSaveStatus] = useState<Record<string, string>>({});

    // Supabase connection state
    const [supabaseUrl, setSupabaseUrl] = useState('');
    const [supabaseKey, setSupabaseKey] = useState('');

    useEffect(() => {
        loadSettings();
        loadAutomationState();
    }, []);

    useEffect(() => {
        if (activeSection === 'storage') {
            loadStorageStats();
            loadMemoryStatus();
        }
        if (activeSection === 'connections') {
            loadConnections();
        }
    }, [activeSection]);

    const loadSettings = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/settings');
            setSettings(result);
        } catch (e) {
            console.error('Failed to load settings:', e);
        }
    };

    const loadAutomationState = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/automation/state');
            setAutomationAllowed(result.allowed);
        } catch (e) {}
    };

    const loadStorageStats = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/storage/stats');
            setStorageStats(result);
        } catch (e) {}
    };

    const loadMemoryStatus = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/memory/status');
            setMemoryStatus(result);
        } catch (e) {}
    };

    const loadConnections = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/settings/connections');
            setConnections(result.connections || {});
        } catch (e) {}
    };

    const testProvider = async (providerId: string) => {
        setTestResults(prev => ({ ...prev, [providerId]: { testing: true } }));
        try {
            const result = await window.diveAPI.gateway.request(`/providers/${providerId}/test`, {});
            setTestResults(prev => ({ ...prev, [providerId]: result }));
            loadSettings();
        } catch (e) {
            setTestResults(prev => ({
                ...prev,
                [providerId]: { connected: false, error: String(e) }
            }));
        }
    };

    const toggleAutomation = async () => {
        try {
            const result = await window.diveAPI.gateway.request('/automation/toggle', {});
            setAutomationAllowed(result.allowed);
        } catch (e) {}
    };

    const clearStorage = async () => {
        try {
            await window.diveAPI.gateway.request('/storage/clear', {});
            setClearConfirm(false);
            loadStorageStats();
        } catch (e) {}
    };

    const clearMemory = async () => {
        try {
            await window.diveAPI.gateway.request('/memory/clear', {});
            loadMemoryStatus();
        } catch (e) {}
    };

    const saveConnection = async (providerId: string) => {
        const apiKey = editingKeys[providerId];
        const url = editingUrls[providerId];
        if (!apiKey && !url) return;

        setSaveStatus(prev => ({ ...prev, [providerId]: 'saving' }));
        try {
            await window.diveAPI.gateway.request('/settings/connections', {
                provider_id: providerId,
                api_key: apiKey || undefined,
                url: url || undefined,
            });
            // Hot reload
            await window.diveAPI.gateway.request('/settings/connections/reload', {});
            setSaveStatus(prev => ({ ...prev, [providerId]: 'saved' }));
            loadSettings();
            loadConnections();
            setTimeout(() => setSaveStatus(prev => ({ ...prev, [providerId]: '' })), 2000);
        } catch (e) {
            setSaveStatus(prev => ({ ...prev, [providerId]: 'error' }));
        }
    };

    if (!settings) {
        return (
            <div className="settings-container">
                <div className="settings-loading">Loading settings...</div>
            </div>
        );
    }

    return (
        <div className="settings-container">
            <div className="settings-header">
                <h2>⚙️ Settings</h2>
                <span className="settings-version">v{settings.app.version}</span>
            </div>

            {/* Section Tabs */}
            <div className="settings-tabs">
                {[
                    { id: 'providers', label: '🔌 Providers' },
                    { id: 'connections', label: '🔗 Connections' },
                    { id: 'storage', label: '💾 Storage' },
                    { id: 'automation', label: '🤖 Automation' },
                    { id: 'features', label: '⚡ Features' },
                    { id: 'about', label: 'ℹ️ About' }
                ].map(tab => (
                    <button
                        key={tab.id}
                        className={`settings-tab ${activeSection === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveSection(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="settings-content">
                {/* Providers Section */}
                {activeSection === 'providers' && (
                    <div className="settings-section">
                        <h3>API Providers</h3>
                        <p className="section-desc">Manage your LLM API connections. Test to check latency.</p>

                        <div className="providers-list">
                            {settings.providers.map(provider => (
                                <div key={provider.id} className={`provider-card ${provider.connected ? 'connected' : 'disconnected'}`}>
                                    <div className="provider-header">
                                        <div className="provider-info">
                                            <span className={`provider-status ${provider.connected ? 'online' : 'offline'}`}></span>
                                            <h4>{provider.name}</h4>
                                            {provider.is_primary && <span className="primary-badge">⭐ Primary</span>}
                                        </div>
                                        <button
                                            className="test-btn"
                                            onClick={() => testProvider(provider.id)}
                                            disabled={testResults[provider.id]?.testing}
                                        >
                                            {testResults[provider.id]?.testing ? '⏳ Testing...' : '🔍 Test'}
                                        </button>
                                    </div>

                                    <div className="provider-details">
                                        <div className="detail-row">
                                            <span className="detail-label">URL</span>
                                            <span className="detail-value">{provider.base_url}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">API Key</span>
                                            <span className={`detail-value ${provider.has_key ? 'key-set' : 'key-missing'}`}>
                                                {provider.has_key ? '✅ Set' : '❌ Not set'} ({provider.api_key_env})
                                            </span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">Models</span>
                                            <span className="detail-value">{provider.model_count} available</span>
                                        </div>
                                        {provider.latency_ms > 0 && (
                                            <div className="detail-row">
                                                <span className="detail-label">Latency</span>
                                                <span className={`detail-value latency ${
                                                    provider.latency_ms < 500 ? 'fast' : 
                                                    provider.latency_ms < 1500 ? 'medium' : 'slow'
                                                }`}>
                                                    {Math.round(provider.latency_ms)}ms
                                                </span>
                                            </div>
                                        )}
                                    </div>

                                    {testResults[provider.id] && !testResults[provider.id].testing && (
                                        <div className={`test-result ${testResults[provider.id].connected ? 'success' : 'failure'}`}>
                                            {testResults[provider.id].connected 
                                                ? `✅ Connected (${Math.round(testResults[provider.id].latency_ms)}ms)`
                                                : `❌ Failed: ${testResults[provider.id].error || 'Connection error'}`}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Connections Section (Editable) */}
                {activeSection === 'connections' && (
                    <div className="settings-section">
                        <h3>🔗 Connection Settings</h3>
                        <p className="section-desc">Edit API keys and URLs. Changes apply immediately.</p>

                        {settings.providers.map(provider => (
                            <div key={provider.id} className="connection-card">
                                <div className="connection-header">
                                    <span className={`provider-status ${provider.connected ? 'online' : 'offline'}`}></span>
                                    <h4>{provider.name}</h4>
                                    {saveStatus[provider.id] === 'saved' && (
                                        <span className="save-badge saved">✅ Saved</span>
                                    )}
                                    {saveStatus[provider.id] === 'saving' && (
                                        <span className="save-badge saving">⏳ Saving...</span>
                                    )}
                                </div>

                                <div className="connection-fields">
                                    <div className="field-group">
                                        <label>API URL</label>
                                        <input
                                            type="text"
                                            placeholder={provider.base_url}
                                            value={editingUrls[provider.id] || ''}
                                            onChange={(e) => setEditingUrls(prev => ({
                                                ...prev, [provider.id]: e.target.value
                                            }))}
                                        />
                                    </div>
                                    <div className="field-group">
                                        <label>
                                            API Key ({provider.api_key_env})
                                            {provider.has_key && <span className="key-status set">● Set</span>}
                                            {!provider.has_key && <span className="key-status missing">● Missing</span>}
                                        </label>
                                        <input
                                            type="password"
                                            placeholder={provider.has_key ? '••••••••••' : 'Enter API key...'}
                                            value={editingKeys[provider.id] || ''}
                                            onChange={(e) => setEditingKeys(prev => ({
                                                ...prev, [provider.id]: e.target.value
                                            }))}
                                        />
                                    </div>
                                    <button
                                        className="save-connection-btn"
                                        onClick={() => saveConnection(provider.id)}
                                        disabled={!editingKeys[provider.id] && !editingUrls[provider.id]}
                                    >
                                        💾 Save & Reload
                                    </button>
                                </div>
                            </div>
                        ))}

                        {/* Supabase Section */}
                        <div className="connection-card supabase-card">
                            <div className="connection-header">
                                <span className="provider-status offline"></span>
                                <h4>☁️ Supabase (Cloud Sync)</h4>
                            </div>
                            <div className="connection-fields">
                                <div className="field-group">
                                    <label>Supabase URL</label>
                                    <input
                                        type="text"
                                        placeholder="https://your-project.supabase.co"
                                        value={supabaseUrl}
                                        onChange={(e) => setSupabaseUrl(e.target.value)}
                                    />
                                </div>
                                <div className="field-group">
                                    <label>Supabase Anon Key</label>
                                    <input
                                        type="password"
                                        placeholder="Enter anon key..."
                                        value={supabaseKey}
                                        onChange={(e) => setSupabaseKey(e.target.value)}
                                    />
                                </div>
                                <button
                                    className="save-connection-btn"
                                    onClick={async () => {
                                        if (!supabaseUrl || !supabaseKey) return;
                                        await window.diveAPI.gateway.request('/settings/connections', {
                                            provider_id: 'supabase',
                                            url: supabaseUrl,
                                            api_key: supabaseKey,
                                        });
                                    }}
                                    disabled={!supabaseUrl || !supabaseKey}
                                >
                                    💾 Save Supabase
                                </button>
                            </div>
                            <p className="connection-hint">
                                💡 Optional. Chat logs are saved locally by default.
                                Supabase enables cloud sync across devices.
                            </p>
                        </div>
                    </div>
                )}

                {/* Storage Section */}
                {activeSection === 'storage' && (
                    <div className="settings-section">
                        <h3>💾 Local Storage</h3>
                        <p className="section-desc">All data is stored locally. Supabase sync is optional.</p>

                        {storageStats && (
                            <div className="storage-card">
                                <div className="storage-stats-grid">
                                    <div className="stat-item">
                                        <span className="stat-value">{storageStats.used_mb} MB</span>
                                        <span className="stat-label">Used Space</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-value">{storageStats.file_count}</span>
                                        <span className="stat-label">Files</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-value">{storageStats.conversation_count}</span>
                                        <span className="stat-label">Conversations</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className={`stat-value ${storageStats.memory_initialized ? 'active' : 'inactive'}`}>
                                            {storageStats.memory_initialized ? '✅' : '❌'}
                                        </span>
                                        <span className="stat-label">Memory</span>
                                    </div>
                                </div>
                                <div className="storage-path">
                                    <span className="detail-label">📁 Path</span>
                                    <code>{storageStats.path}</code>
                                </div>
                            </div>
                        )}

                        {/* Memory Status */}
                        {memoryStatus && memoryStatus.initialized && (
                            <div className="storage-card memory-card">
                                <h4>🧠 Memory Status</h4>
                                <div className="storage-stats-grid">
                                    <div className="stat-item">
                                        <span className="stat-value">
                                            {memoryStatus.short_term_messages}/{memoryStatus.max_short_term}
                                        </span>
                                        <span className="stat-label">Short-term</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-value">{memoryStatus.long_term_facts}</span>
                                        <span className="stat-label">Facts</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-value">{memoryStatus.long_term_topics}</span>
                                        <span className="stat-label">Topics</span>
                                    </div>
                                </div>
                                {Object.keys(memoryStatus.preferences).length > 0 && (
                                    <div className="memory-prefs">
                                        <span className="detail-label">Learned Preferences:</span>
                                        {Object.entries(memoryStatus.preferences).map(([k, v]) => (
                                            <span key={k} className="pref-tag">{k}: {v}</span>
                                        ))}
                                    </div>
                                )}
                                <button className="clear-btn warning" onClick={clearMemory}>
                                    🗑️ Clear Memory
                                </button>
                            </div>
                        )}

                        {/* Clear Data */}
                        <div className="storage-card danger-zone">
                            <h4>⚠️ Danger Zone</h4>
                            {!clearConfirm ? (
                                <button className="clear-btn danger" onClick={() => setClearConfirm(true)}>
                                    🗑️ Clear All Conversations
                                </button>
                            ) : (
                                <div className="confirm-clear">
                                    <p>This will delete all conversations. Settings and memory are kept.</p>
                                    <button className="clear-btn danger" onClick={clearStorage}>
                                        ⚠️ Yes, Delete All
                                    </button>
                                    <button className="clear-btn cancel" onClick={() => setClearConfirm(false)}>
                                        Cancel
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Automation Section */}
                {activeSection === 'automation' && (
                    <div className="settings-section">
                        <h3>Automation & PC Control</h3>
                        <p className="section-desc">Control how Dive AI interacts with your desktop.</p>

                        <div className="automation-card">
                            <div className="automation-toggle">
                                <div>
                                    <h4>🖱️ Allow PC Control</h4>
                                    <p>Let Dive AI control mouse and keyboard for automation tasks</p>
                                </div>
                                <button
                                    className={`toggle-btn ${automationAllowed ? 'on' : 'off'}`}
                                    onClick={toggleAutomation}
                                >
                                    {automationAllowed ? 'ON' : 'OFF'}
                                </button>
                            </div>
                            <div className="hotkey-info">
                                <span className="hotkey-badge">F3</span>
                                <span>Press F3 anytime to toggle PC control on/off</span>
                            </div>
                        </div>

                        <div className="automation-card">
                            <h4>🛡️ Safety</h4>
                            <ul className="safety-list">
                                <li>A floating STOP button appears during automation</li>
                                <li>Press F3 or click STOP to immediately halt</li>
                                <li>All file modifications create backups first</li>
                                <li>Dangerous actions require explicit approval</li>
                            </ul>
                        </div>
                    </div>
                )}

                {/* Features Section */}
                {activeSection === 'features' && (
                    <div className="settings-section">
                        <h3>Features</h3>
                        <div className="features-grid">
                            {Object.entries(settings.features).map(([key, enabled]) => (
                                <div key={key} className={`feature-card ${enabled ? 'enabled' : 'disabled'}`}>
                                    <span className="feature-status">{enabled ? '✅' : '❌'}</span>
                                    <span className="feature-name">{key.replace(/_/g, ' ')}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* About Section */}
                {activeSection === 'about' && (
                    <div className="settings-section">
                        <h3>About Dive AI</h3>
                        <div className="about-card">
                            <div className="about-logo">🤿</div>
                            <h2>{settings.app.name}</h2>
                            <p className="about-version">Version {settings.app.version}</p>
                            <p className="about-desc">Self-aware AI assistant with multi-provider LLM support, desktop automation, and self-debugging capabilities.</p>
                            <div className="about-details">
                                <div className="detail-row">
                                    <span>Gateway</span>
                                    <span>{settings.server.host}:{settings.server.port}</span>
                                </div>
                                <div className="detail-row">
                                    <span>Providers</span>
                                    <span>{settings.providers.length}</span>
                                </div>
                                <div className="detail-row">
                                    <span>Inspired by</span>
                                    <span>UI-TARS, OpenClaw, Antigravity</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Settings;
