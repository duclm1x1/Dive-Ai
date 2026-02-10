import { useEffect, useState } from 'react';
import { X, Command, Keyboard } from 'lucide-react';

interface Shortcut {
  keys: string[];
  description: string;
  category: string;
}

const shortcuts: Shortcut[] = [
  { keys: ['?'], description: 'Show keyboard shortcuts', category: 'General' },
  { keys: ['Esc'], description: 'Close modals and overlays', category: 'General' },

  { keys: ['Ctrl', 'N'], description: 'New conversation', category: 'Navigation' },
  { keys: ['Ctrl', 'K'], description: 'Quick command palette', category: 'Navigation' },
  { keys: ['Ctrl', '/'], description: 'Toggle sidebar', category: 'Navigation' },
  { keys: ['Ctrl', 'F'], description: 'Search messages', category: 'Navigation' },

  { keys: ['Enter'], description: 'Send message', category: 'Chat' },
  { keys: ['Shift', 'Enter'], description: 'New line in message', category: 'Chat' },
  { keys: ['Ctrl', 'Enter'], description: 'Send message (alternative)', category: 'Chat' },

  { keys: ['Ctrl', 'C'], description: 'Copy message', category: 'Messages' },
  { keys: ['Ctrl', 'E'], description: 'Edit last message', category: 'Messages' },
  { keys: ['Ctrl', 'R'], description: 'Regenerate response', category: 'Messages' },
  { keys: ['Ctrl', 'D'], description: 'Delete message', category: 'Messages' },
];

export function KeyboardShortcuts() {
  const [isOpen, setIsOpen] = useState(false);
  const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          e.preventDefault();
          setIsOpen(prev => !prev);
        }
      }

      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  if (!isOpen) return null;

  const formatKey = (key: string) => {
    if (isMac) {
      if (key === 'Ctrl') return '⌘';
      if (key === 'Alt') return '⌥';
      if (key === 'Shift') return '⇧';
    }
    return key;
  };

  const categories = Array.from(new Set(shortcuts.map(s => s.category)));

  return (
    <>
      <div
        className="fixed inset-0 bg-surface-950/80 backdrop-blur-sm z-50 animate-fade-in"
        onClick={() => setIsOpen(false)}
      />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div className="bg-surface-900 border border-surface-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden pointer-events-auto animate-scale-in">
          <div className="flex items-center justify-between px-5 py-4 border-b border-surface-800">
            <div className="flex items-center gap-2">
              <Keyboard size={18} className="text-brand-400" />
              <h2 className="text-lg font-semibold text-white">Keyboard Shortcuts</h2>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-lg hover:bg-surface-800 text-surface-400 hover:text-white transition-colors"
              title="Close (Esc)"
            >
              <X size={18} />
            </button>
          </div>

          <div className="overflow-y-auto max-h-[calc(80vh-80px)] p-5">
            {categories.map(category => (
              <div key={category} className="mb-6 last:mb-0">
                <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wider mb-3">
                  {category}
                </h3>
                <div className="space-y-2">
                  {shortcuts
                    .filter(s => s.category === category)
                    .map((shortcut, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-surface-800/50 transition-colors"
                      >
                        <span className="text-sm text-surface-300">{shortcut.description}</span>
                        <div className="flex items-center gap-1">
                          {shortcut.keys.map((key, keyIdx) => (
                            <div key={keyIdx} className="flex items-center gap-1">
                              <kbd className="inline-flex items-center justify-center min-w-[24px] h-6 px-2 rounded border border-surface-700 bg-surface-800 text-[11px] font-mono text-surface-300 font-semibold">
                                {formatKey(key)}
                              </kbd>
                              {keyIdx < shortcut.keys.length - 1 && (
                                <span className="text-surface-600 text-xs">+</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>

          <div className="px-5 py-3 border-t border-surface-800 bg-surface-800/30">
            <p className="text-xs text-surface-500 text-center">
              Press <kbd className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded border border-surface-700 bg-surface-800 text-[10px] font-mono text-surface-400 mx-1">?</kbd> anytime to toggle this dialog
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
