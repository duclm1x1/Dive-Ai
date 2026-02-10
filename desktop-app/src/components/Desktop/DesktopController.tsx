import React, { useState } from 'react';
import './DesktopController.css';

function DesktopController() {
    const [screenshot, setScreenshot] = useState<string>('');
    const [instruction, setInstruction] = useState('');
    const [result, setResult] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const captureScreen = async () => {
        try {
            const data = await window.diveAPI.automation.screenshot();
            if (data.screenshot) {
                setScreenshot(`data:image/png;base64,${data.screenshot}`);
                setResult(`Screenshot captured at ${data.timestamp}`);
            }
        } catch (error) {
            setResult(`Error: ${error}`);
        }
    };

    const executeInstruction = async () => {
        if (!instruction.trim()) return;
        setIsLoading(true);
        try {
            const data = await window.diveAPI.gateway.request('/automation/ui-tars', {
                instruction: instruction.trim(),
                mode: 'local'
            });
            setResult(JSON.stringify(data, null, 2));
        } catch (error) {
            setResult(`Error: ${error}`);
        } finally {
            setIsLoading(false);
        }
    };

    const quickAction = async (action: string, params: any = {}) => {
        try {
            const data = await window.diveAPI.automation.execute(action, params);
            setResult(JSON.stringify(data, null, 2));
        } catch (error) {
            setResult(`Error: ${error}`);
        }
    };

    return (
        <div className="desktop-controller">
            <div className="preview-section">
                <div className="preview-header">
                    <h3>🖥️ Screen Preview</h3>
                    <button className="btn btn-secondary" onClick={captureScreen}>
                        📸 Capture
                    </button>
                </div>
                <div className="preview-area">
                    {screenshot ? (
                        <img src={screenshot} alt="Desktop Screenshot" />
                    ) : (
                        <div className="placeholder">
                            Click "Capture" to take a screenshot
                        </div>
                    )}
                </div>
            </div>

            <div className="control-section">
                <div className="instruction-panel">
                    <h3>🤖 AI Automation</h3>
                    <p>Describe what you want to do in natural language:</p>
                    <textarea
                        value={instruction}
                        onChange={e => setInstruction(e.target.value)}
                        placeholder="e.g., Click on the search button and type 'hello world'"
                        rows={3}
                    />
                    <button
                        className="btn btn-primary execute-btn"
                        onClick={executeInstruction}
                        disabled={isLoading || !instruction.trim()}
                    >
                        {isLoading ? '⏳ Executing...' : '▶️ Execute'}
                    </button>
                </div>

                <div className="quick-actions">
                    <h3>⚡ Quick Actions</h3>
                    <div className="action-grid">
                        <button onClick={captureScreen}>📸 Screenshot</button>
                        <button onClick={() => quickAction('click', { x: 500, y: 500 })}>
                            🖱️ Click Center
                        </button>
                        <button onClick={() => {
                            const text = prompt('Text to type:');
                            if (text) quickAction('type', { text });
                        }}>
                            ⌨️ Type Text
                        </button>
                        <button onClick={() => quickAction('keypress', { key: 'enter' })}>
                            ↵ Enter
                        </button>
                    </div>
                </div>

                <div className="result-panel">
                    <h3>📋 Result</h3>
                    <pre>{result || 'Results will appear here'}</pre>
                </div>
            </div>
        </div>
    );
}

export default DesktopController;
