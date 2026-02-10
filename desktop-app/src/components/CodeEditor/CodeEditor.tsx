import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';

const LANGUAGES = ['python', 'javascript', 'typescript', 'html', 'css', 'json', 'yaml', 'sql'];

function CodeEditor() {
    const [code, setCode] = useState('# Welcome to Dive AI Code Editor\n\nprint("Hello, World!")\n');
    const [language, setLanguage] = useState('python');
    const [filePath, setFilePath] = useState('');
    const [aiOutput, setAiOutput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const askAI = async (prompt: string) => {
        setIsLoading(true);
        try {
            const fullPrompt = `${prompt}\n\nCode:\n\`\`\`${language}\n${code}\n\`\`\``;
            const result = await window.diveAPI.gateway.chat(fullPrompt);
            setAiOutput(result.response || result.error || 'No response');
        } catch (error) {
            setAiOutput(`Error: ${error}`);
        } finally {
            setIsLoading(false);
        }
    };

    const openFile = async () => {
        if (!filePath) return;
        try {
            const result = await window.diveAPI.fs.readFile(filePath);
            if (result.content) {
                setCode(result.content);
                // Auto-detect language
                const ext = filePath.split('.').pop()?.toLowerCase();
                if (ext && LANGUAGES.includes(ext)) {
                    setLanguage(ext);
                }
            }
        } catch (error) {
            setAiOutput(`Failed to open file: ${error}`);
        }
    };

    const saveFile = async () => {
        if (!filePath) {
            setAiOutput('Please enter a file path first');
            return;
        }
        try {
            await window.diveAPI.fs.writeFile(filePath, code);
            setAiOutput(`Saved to ${filePath}`);
        } catch (error) {
            setAiOutput(`Failed to save: ${error}`);
        }
    };

    return (
        <div className="editor-container">
            <div className="editor-main">
                <div className="toolbar">
                    <select value={language} onChange={e => setLanguage(e.target.value)}>
                        {LANGUAGES.map(lang => (
                            <option key={lang} value={lang}>{lang.toUpperCase()}</option>
                        ))}
                    </select>

                    <input
                        type="text"
                        placeholder="File path..."
                        value={filePath}
                        onChange={e => setFilePath(e.target.value)}
                        className="file-input"
                    />

                    <button className="btn btn-secondary" onClick={openFile}>Open</button>
                    <button className="btn btn-primary" onClick={saveFile}>Save</button>
                </div>

                <div className="monaco-wrapper">
                    <Editor
                        height="100%"
                        language={language}
                        value={code}
                        onChange={value => setCode(value || '')}
                        theme="vs-dark"
                        options={{
                            fontSize: 14,
                            fontFamily: "'Cascadia Code', 'Fira Code', monospace",
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            padding: { top: 16 },
                            lineNumbers: 'on',
                            wordWrap: 'on'
                        }}
                    />
                </div>
            </div>

            <div className="ai-panel">
                <h3>🤖 AI Assistant</h3>

                <div className="quick-prompts">
                    <button onClick={() => askAI('Explain this code in detail:')}>
                        📖 Explain
                    </button>
                    <button onClick={() => askAI('Find and fix any bugs in this code:')}>
                        🐛 Fix Bugs
                    </button>
                    <button onClick={() => askAI('Optimize this code for performance:')}>
                        ⚡ Optimize
                    </button>
                    <button onClick={() => askAI('Add comments to this code:')}>
                        💬 Comment
                    </button>
                </div>

                <div className="ai-output">
                    {isLoading ? (
                        <div className="loading">Thinking...</div>
                    ) : (
                        <pre>{aiOutput || 'AI responses will appear here'}</pre>
                    )}
                </div>
            </div>
        </div>
    );
}

export default CodeEditor;
