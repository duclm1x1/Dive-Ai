import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import type { LiveMetrics } from '@/types/observability';
import { 
  Clock, 
  Cpu, 
  Sparkles, 
  FileText,
  Zap,
  TrendingUp
} from 'lucide-react';

interface LiveMetricsPanelProps {
  metrics: LiveMetrics;
  isLive?: boolean;
}

export function LiveMetricsPanel({ metrics: initialMetrics, isLive = true }: LiveMetricsPanelProps) {
  const [metrics, setMetrics] = useState(initialMetrics);
  const [pulseKey, setPulseKey] = useState(0);

  // Simulate live metrics updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        total_duration_ms: prev.total_duration_ms + 200,
        tool_time_ms: prev.tool_time_ms + Math.random() * 50,
        llm_time_ms: prev.llm_time_ms + Math.random() * 30,
        context_usage_chars: Math.min(
          prev.context_usage_chars + Math.random() * 500,
          prev.max_context_chars * 0.85
        ),
        token_usage: prev.token_usage ? {
          input: prev.token_usage.input + Math.floor(Math.random() * 20),
          output: prev.token_usage.output + Math.floor(Math.random() * 10),
        } : undefined,
      }));
      setPulseKey(k => k + 1);
    }, 500);

    return () => clearInterval(interval);
  }, [isLive]);

  const contextPercent = (metrics.context_usage_chars / metrics.max_context_chars) * 100;
  
  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatNumber = (n: number) => {
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
    return Math.round(n).toString();
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Live Metrics
        </h2>
        {isLive && (
          <div className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
            </span>
          </div>
        )}
      </div>

      {/* Total Duration - Hero metric */}
      <div className="glass-card p-4 border border-primary/20">
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-4 h-4 text-primary" />
          <span className="text-2xs text-muted-foreground uppercase">Total Duration</span>
        </div>
        <div 
          key={`duration-${pulseKey}`}
          className={cn(
            "text-2xl font-bold text-gradient-cyan font-mono tabular-nums",
            isLive && "animate-pulse"
          )}
        >
          {formatDuration(metrics.total_duration_ms)}
        </div>
      </div>

      {/* Time Breakdown */}
      <div className="space-y-3">
        <div className="text-2xs text-muted-foreground uppercase font-semibold">Time Breakdown</div>
        
        <div className="glass-card p-3 space-y-3">
          {/* Tool Time */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <Cpu className="w-3 h-3 text-info" />
                <span className="text-2xs">Tool Execution</span>
              </div>
              <span className="text-xs font-mono text-info">
                {formatDuration(metrics.tool_time_ms)}
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-muted overflow-hidden">
              <div 
                className="h-full bg-info transition-all duration-300 rounded-full"
                style={{ 
                  width: `${(metrics.tool_time_ms / metrics.total_duration_ms) * 100}%` 
                }}
              />
            </div>
          </div>

          {/* LLM Time */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <Sparkles className="w-3 h-3 text-accent" />
                <span className="text-2xs">LLM Processing</span>
              </div>
              <span className="text-xs font-mono text-accent">
                {formatDuration(metrics.llm_time_ms)}
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-muted overflow-hidden">
              <div 
                className="h-full bg-accent transition-all duration-300 rounded-full"
                style={{ 
                  width: `${(metrics.llm_time_ms / metrics.total_duration_ms) * 100}%` 
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Context Usage */}
      <div className="space-y-3">
        <div className="text-2xs text-muted-foreground uppercase font-semibold">Context Usage</div>
        
        <div className="glass-card p-3">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <FileText className="w-3 h-3 text-primary" />
              <span className="text-2xs">Characters</span>
            </div>
            <span className="text-xs font-mono">
              <span className={cn(
                "transition-colors",
                contextPercent > 80 ? "text-status-failed" : 
                contextPercent > 60 ? "text-yellow-500" : "text-foreground"
              )}>
                {formatNumber(metrics.context_usage_chars)}
              </span>
              <span className="text-muted-foreground">
                /{formatNumber(metrics.max_context_chars)}
              </span>
            </span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div 
              className={cn(
                "h-full transition-all duration-300 rounded-full",
                contextPercent > 80 ? "bg-status-failed" : 
                contextPercent > 60 ? "bg-yellow-500" : "bg-primary"
              )}
              style={{ width: `${contextPercent}%` }}
            />
          </div>
          <div className="mt-1 text-2xs text-muted-foreground text-right">
            {contextPercent.toFixed(1)}% used
          </div>
        </div>
      </div>

      {/* Token Usage */}
      {metrics.token_usage && (
        <div className="space-y-3">
          <div className="text-2xs text-muted-foreground uppercase font-semibold">Token Usage</div>
          
          <div className="grid grid-cols-2 gap-2">
            <div className="glass-card p-3 text-center">
              <div className="text-2xs text-muted-foreground mb-1">Input</div>
              <div 
                key={`input-${pulseKey}`}
                className="text-lg font-bold font-mono text-foreground"
              >
                {formatNumber(metrics.token_usage.input)}
              </div>
            </div>
            <div className="glass-card p-3 text-center">
              <div className="text-2xs text-muted-foreground mb-1">Output</div>
              <div 
                key={`output-${pulseKey}`}
                className="text-lg font-bold font-mono text-accent"
              >
                {formatNumber(metrics.token_usage.output)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Latency */}
      <div className="space-y-3">
        <div className="text-2xs text-muted-foreground uppercase font-semibold">Latency</div>
        
        <div className="grid grid-cols-2 gap-2">
          <div className="glass-card p-3 text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Zap className="w-3 h-3 text-status-completed" />
              <span className="text-2xs text-muted-foreground">p50</span>
            </div>
            <div className="text-sm font-bold font-mono text-status-completed">
              {metrics.latency.p50}ms
            </div>
          </div>
          <div className="glass-card p-3 text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <TrendingUp className="w-3 h-3 text-yellow-500" />
              <span className="text-2xs text-muted-foreground">p95</span>
            </div>
            <div className="text-sm font-bold font-mono text-yellow-500">
              {metrics.latency.p95}ms
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
