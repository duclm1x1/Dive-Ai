import { useState } from 'react';
import { RunList } from './RunList';
import { UnifiedTimelinePanel } from './UnifiedTimelinePanel';
import { ThinkingPanel } from './ThinkingPanel';
import { DiveCoderCLI } from './DiveCoderCLI';
import { LiveMetricsPanel } from './LiveMetricsPanel';
import { LLMProviderStatus } from '@/components/monitor/LLMProviderStatus';
import { useRuntimeStore } from '@/stores/runtimeStore';

export function ActivityTab() {
  const { runs, steps, events, metrics, selectedRunId } = useRuntimeStore();
  const [localSelectedRunId, setLocalSelectedRunId] = useState<string>(runs[0]?.run_id || '');
  const currentRunId = selectedRunId || localSelectedRunId;
  const selectedRun = runs.find(r => r.run_id === currentRunId);
  const isLive = selectedRun?.status === 'RUNNING';

  return (
    <div className="flex h-full">
      {/* Left Panel - Run List */}
      <div className="w-64 shrink-0 border-r border-border overflow-y-auto bg-card/30">
        <RunList 
          runs={runs.length > 0 ? runs : []} 
          selectedRunId={currentRunId}
          onSelectRun={setLocalSelectedRunId}
        />
      </div>

      {/* Main Panel - Split View */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top: Unified Timeline + Events */}
        <div className="h-1/2 border-b border-border overflow-hidden">
          <UnifiedTimelinePanel 
            steps={steps} 
            events={events} 
            isLive={isLive} 
          />
        </div>
        
        {/* Bottom: Thinking Model + CLI */}
        <div className="h-1/2 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-hidden">
            <ThinkingPanel isLive={isLive} />
          </div>
          <DiveCoderCLI />
        </div>
      </div>

      {/* Right Panel - Live Metrics */}
      <div className="w-72 shrink-0 border-l border-border overflow-y-auto bg-card/30 space-y-4 p-4">
        <LLMProviderStatus events={events} />
        <LiveMetricsPanel metrics={metrics || {
          total_duration_ms: 0,
          tool_time_ms: 0,
          llm_time_ms: 0,
          context_usage_chars: 0,
          max_context_chars: 128000,
          token_usage: { input: 0, output: 0 },
          latency: { p50: 0, p95: 0 },
        }} isLive={isLive} />
      </div>
    </div>
  );
}
