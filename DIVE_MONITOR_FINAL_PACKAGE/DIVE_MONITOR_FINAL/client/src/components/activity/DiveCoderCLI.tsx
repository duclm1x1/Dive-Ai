import { useState, useRef, useEffect } from 'react';
import { Send, Terminal, ArrowUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useEventStream } from '@/providers/EventStreamProvider';

export function DiveCoderCLI() {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const { sendCommand } = useEventStream();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add to history
    setHistory(prev => [...prev, input]);
    setHistoryIndex(-1);

    // Send command to monitor server for execution
    try {
      const response = await fetch('http://localhost:8787/v1/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: input })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Command started:', result);
      }
    } catch (error) {
      console.error('Failed to execute command:', error);
    }

    // Clear input
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (history.length === 0) return;
      
      const newIndex = historyIndex === -1 
        ? history.length - 1 
        : Math.max(0, historyIndex - 1);
      
      setHistoryIndex(newIndex);
      setInput(history[newIndex]);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex === -1) return;
      
      const newIndex = historyIndex + 1;
      if (newIndex >= history.length) {
        setHistoryIndex(-1);
        setInput('');
      } else {
        setHistoryIndex(newIndex);
        setInput(history[newIndex]);
      }
    }
  };

  return (
    <div className={cn(
      "border-t border-border bg-card/50 backdrop-blur-sm transition-all duration-200",
      isFocused && "border-primary/50 bg-card/80"
    )}>
      <form onSubmit={handleSubmit} className="flex items-center gap-3 p-3">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Terminal className="w-4 h-4" />
          <span className="text-xs font-mono">$</span>
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Type command for DiveCoder... (e.g., 'fix this bug', 'explain main.py')"
          className="flex-1 bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground/50 font-mono"
        />

        {history.length > 0 && (
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <ArrowUp className="w-3 h-3" />
            <span>History</span>
          </div>
        )}

        <button
          type="submit"
          disabled={!input.trim()}
          className={cn(
            "p-2 rounded-lg transition-all duration-200",
            input.trim()
              ? "bg-primary/10 text-primary hover:bg-primary/20 hover:scale-105"
              : "bg-muted/30 text-muted-foreground/30 cursor-not-allowed"
          )}
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
