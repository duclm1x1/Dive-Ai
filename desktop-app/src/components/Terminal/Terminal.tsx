import React, { useState, useRef, useEffect } from 'react';
import './Terminal.css';

interface HistoryItem {
    type: 'input' | 'output' | 'error';
    content: string;
}

function Terminal() {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [command, setCommand] = useState('');
    const [cwd, setCwd] = useState('D:\\Antigravity\\Dive AI\\desktop-app');
    const [commandHistory, setCommandHistory] = useState<string[]>([]);
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [isExecuting, setIsExecuting] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const outputRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        outputRef.current?.scrollTo(0, outputRef.current.scrollHeight);
    }, [history]);

    // Welcome message on mount
    useEffect(() => {
        setHistory([
            { type: 'output', content: '🦞 Dive AI V29.7 Terminal' },
            { type: 'output', content: 'Type "help" for available commands\n' }
        ]);
    }, []);

    const executeCommand = async () => {
        if (!command.trim() || isExecuting) return;

        const cmd = command.trim();
        setCommandHistory(prev => [...prev, cmd]);
        setHistoryIndex(-1);

        setHistory(prev => [...prev, { type: 'input', content: `${cwd}> ${cmd}` }]);
        setCommand('');
        setIsExecuting(true);

        // Built-in commands
        if (cmd === 'clear' || cmd === 'cls') {
            setHistory([]);
            setIsExecuting(false);
            return;
        }

        if (cmd === 'help') {
            setHistory(prev => [...prev, {
                type: 'output',
                content: `Available commands:
  clear/cls     - Clear terminal
  cd <path>     - Change directory
  help          - Show this help
  
Any other command will be executed via PowerShell.
Use arrow keys ↑↓ to navigate command history.`
            }]);
            setIsExecuting(false);
            return;
        }

        if (cmd.startsWith('cd ')) {
            const newDir = cmd.slice(3).trim();
            // Handle relative and absolute paths
            if (newDir === '..') {
                const parts = cwd.split('\\');
                parts.pop();
                setCwd(parts.join('\\') || 'C:\\');
            } else if (newDir.includes(':')) {
                setCwd(newDir);
            } else {
                setCwd(`${cwd}\\${newDir}`);
            }
            setHistory(prev => [...prev, { type: 'output', content: `Changed to: ${cwd}` }]);
            setIsExecuting(false);
            return;
        }

        try {
            const result = await window.diveAPI.terminal.execute(cmd, cwd);

            if (result.output && result.output.trim()) {
                setHistory(prev => [...prev, { type: 'output', content: result.output.trim() }]);
            }
            if (result.error && result.error.trim()) {
                setHistory(prev => [...prev, { type: 'error', content: result.error.trim() }]);
            }
            if (result.code !== undefined && result.code !== 0 && !result.error) {
                setHistory(prev => [...prev, { type: 'error', content: `Exit code: ${result.code}` }]);
            }
        } catch (error) {
            setHistory(prev => [...prev, { type: 'error', content: `Error: ${error}` }]);
        } finally {
            setIsExecuting(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            executeCommand();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (commandHistory.length > 0) {
                const newIndex = historyIndex < commandHistory.length - 1 ? historyIndex + 1 : historyIndex;
                setHistoryIndex(newIndex);
                setCommand(commandHistory[commandHistory.length - 1 - newIndex] || '');
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex > 0) {
                setHistoryIndex(historyIndex - 1);
                setCommand(commandHistory[commandHistory.length - historyIndex] || '');
            } else {
                setHistoryIndex(-1);
                setCommand('');
            }
        }
    };

    return (
        <div className="terminal" onClick={() => inputRef.current?.focus()}>
            <div className="terminal-header">
                <span className="terminal-title">🖥️ Terminal</span>
                <span className="terminal-cwd">{cwd}</span>
            </div>

            <div className="terminal-output" ref={outputRef}>
                {history.map((item, idx) => (
                    <div key={idx} className={`line ${item.type}`}>
                        {item.content}
                    </div>
                ))}
            </div>

            <div className="prompt">
                <span className="prompt-symbol">{isExecuting ? '⏳' : '❯'}</span>
                <input
                    ref={inputRef}
                    type="text"
                    value={command}
                    onChange={e => setCommand(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Enter command..."
                    disabled={isExecuting}
                    autoFocus
                />
            </div>
        </div>
    );
}

export default Terminal;
