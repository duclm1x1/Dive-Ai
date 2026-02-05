import { useState } from 'react';
import { RunList } from './RunList';
import { UnifiedTimelinePanel } from './UnifiedTimelinePanel';
import { ThinkingPanel } from './ThinkingPanel';
import { LiveMetricsPanel } from './LiveMetricsPanel';
import { mockRuns, mockExecutionSteps, mockLiveMetrics } from '@/data/mockData';
import { useRuntimeStore } from '@/stores/runtimeStore';

export function ActivityTab() {
  const [selectedRunId, setSelectedRunId] = useState<string>(mockRuns[0]?.run_id || '');
  const { events } = useRuntimeStore();
  const selectedRun = mockRuns.find(r => r.run_id === selectedRunId);
  const isLive = selectedRun?.status === 'RUNNING';

  return (
    <div className="flex h-full">
      {/* Left Panel - Run List */}
      <div className="w-64 shrink-0 border-r border-border overflow-y-auto bg-card/30">
        <RunList 
          runs={mockRuns} 
          selectedRunId={selectedRunId}
          onSelectRun={setSelectedRunId}
        />
      </div>

      {/* Main Panel - Split View */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top: Unified Timeline + Events */}
        <div className="h-1/2 border-b border-border overflow-hidden">
          <UnifiedTimelinePanel 
            steps={mockExecutionSteps} 
            events={events} 
            isLive={isLive} 
          />
        </div>
        
        {/* Bottom: Thinking Model */}
        <div className="h-1/2 overflow-hidden">
          <ThinkingPanel isLive={isLive} />
        </div>
      </div>

      {/* Right Panel - Live Metrics */}
      <div className="w-72 shrink-0 border-l border-border overflow-y-auto bg-card/30">
        <LiveMetricsPanel metrics={mockLiveMetrics} isLive={isLive} />
      </div>
    </div>
  );
}
