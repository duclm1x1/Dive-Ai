import React, { useState } from 'react';
import './BrowserView.css';

function BrowserView() {
    const [url, setUrl] = useState('https://www.google.com');
    const [instruction, setInstruction] = useState('');
    const [result, setResult] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const navigate = () => {
        // URL validation
        let targetUrl = url;
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            targetUrl = `https://${url}`;
            setUrl(targetUrl);
        }
    };

    const executeAutomation = async () => {
        if (!instruction.trim()) return;
        setIsLoading(true);
        try {
            const data = await window.diveAPI.gateway.request('/automation/browser', {
                instruction: instruction.trim(),
                url: url
            });
            setResult(JSON.stringify(data, null, 2));
        } catch (error) {
            setResult(`Error: ${error}`);
        } finally {
            setIsLoading(false);
        }
    };

    const quickAction = async (action: string) => {
        setIsLoading(true);
        try {
            const data = await window.diveAPI.gateway.request('/automation/browser', {
                action,
                url
            });
            setResult(JSON.stringify(data, null, 2));
        } catch (error) {
            setResult(`Error: ${error}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="browser-view">
            <div className="url-bar">
                <button className="nav-btn" title="Back">←</button>
                <button className="nav-btn" title="Forward">→</button>
                <button className="nav-btn" title="Refresh" onClick={navigate}>↻</button>

                <input
                    type="text"
                    value={url}
                    onChange={e => setUrl(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && navigate()}
                    placeholder="Enter URL..."
                    className="url-input"
                />

                <button className="btn btn-primary" onClick={navigate}>Go</button>
            </div>

            <div className="browser-content">
                <div className="browser-frame">
                    <iframe
                        src={url}
                        title="Browser"
                        sandbox="allow-same-origin allow-scripts allow-forms"
                    />
                </div>

                <div className="automation-panel">
                    <h3>🤖 Browser Automation</h3>

                    <div className="instruction-area">
                        <input
                            type="text"
                            value={instruction}
                            onChange={e => setInstruction(e.target.value)}
                            placeholder="Describe action (e.g., 'click search button')"
                            onKeyDown={e => e.key === 'Enter' && executeAutomation()}
                        />
                        <button
                            className="btn btn-primary"
                            onClick={executeAutomation}
                            disabled={isLoading}
                        >
                            {isLoading ? '...' : '▶️'}
                        </button>
                    </div>

                    <div className="quick-actions">
                        <button onClick={() => quickAction('scrape')}>📄 Scrape</button>
                        <button onClick={() => quickAction('screenshot')}>📸 Screenshot</button>
                        <button onClick={() => quickAction('links')}>🔗 Get Links</button>
                        <button onClick={() => quickAction('forms')}>📝 Find Forms</button>
                    </div>

                    <div className="result-area">
                        <pre>{result || 'Results will appear here'}</pre>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default BrowserView;
