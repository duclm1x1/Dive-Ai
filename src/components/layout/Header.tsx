import { Wifi, WifiOff, Brain, RefreshCw } from 'lucide-react';

interface HeaderProps {
  connected: boolean;
  model: string;
  onRefresh?: () => void;
}

export function Header({ connected, model, onRefresh }: HeaderProps) {
  return (
    <header className="h-12 flex items-center justify-between px-4 border-b border-surface-800 bg-surface-950 flex-shrink-0">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-md bg-brand-600 flex items-center justify-center">
            <Brain size={15} className="text-white" />
          </div>
          <div className="leading-none">
            <span className="text-sm font-semibold text-white">Dive AI</span>
            <span className="text-[10px] text-surface-500 ml-1.5">v1.0</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-surface-900 border border-surface-800 text-xs">
          <span className="text-surface-500">Model:</span>
          <span className="text-surface-200 font-mono">{model}</span>
        </div>

        <button
          onClick={onRefresh}
          className="p-1.5 rounded-md text-surface-500 hover:text-white hover:bg-surface-800 transition-colors"
          title="Refresh"
        >
          <RefreshCw size={14} />
        </button>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-900 border border-surface-800">
          {connected ? (
            <>
              <Wifi size={12} className="text-emerald-400" />
              <span className="text-[11px] text-emerald-400">Connected</span>
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            </>
          ) : (
            <>
              <WifiOff size={12} className="text-surface-500" />
              <span className="text-[11px] text-surface-500">Offline</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
