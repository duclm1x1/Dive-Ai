import { useState } from 'react';
import { cn } from '@/lib/utils';
import { StatusBadge } from '../dashboard/StatusBadge';
import { useRuntimeStore, type EventEnvelope } from '@/stores/runtimeStore';
import type { ExecutionStep } from '@/types/observability';
import { 
  GitBranch, 
  ListTree, 
  Search, 
  Link2, 
  FileText,
  ChevronDown,
  ChevronRight,
  Clock,
  Cpu,
  Sparkles,
  Terminal,
  Zap,
  HelpCircle,
  Activity,
  Radio
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const stepIcons: Record<string, React.ElementType> = {
  'Router Decision': GitBranch,
  'Plan Generation': ListTree,
  'RAG Retrieval': Search,
  'Tool Execution': Terminal,
  'Evidence Linking': Link2,
  'Report Generation': FileText,
};

const eventTypeColors: Record<string, string> = {
  'ROUTER_DECISION': 'bg-primary/20 text-primary border-primary/30',
  'PLAN_GENERATED': 'bg-accent/20 text-accent border-accent/30',
  'RAG_RETRIEVAL': 'bg-info/20 text-info border-info/30',
  'TOOL_CALL': 'bg-warning/20 text-warning border-warning/30',
  'EVIDENCE_LINKED': 'bg-success/20 text-success border-success/30',
  'ERROR': 'bg-destructive/20 text-destructive border-destructive/30',
};

interface UnifiedTimelinePanelProps {
  steps: ExecutionStep[];
  events: EventEnvelope[];
  isLive?: boolean;
}

export function UnifiedTimelinePanel({ steps, events, isLive = false }: UnifiedTimelinePanelProps) {
  const [activeView, setActiveView] = useState<'timeline' | 'events'>('timeline');
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const { openWhyDrawer } = useRuntimeStore();

  const toggleStep = (stepId: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepId)) {
        next.delete(stepId);
      } else {
        next.add(stepId);
      }
      return next;
    });
  };

  const anyRunning = steps.some(s => s.status === 'RUNNING');
  const allCompleted = steps.every(s => s.status === 'COMPLETED');

  return (
    <div className="flex flex-col h-full">
      {/* Header with view toggle */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card/50">
        <div className="flex items-center gap-3">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Execution Flow
          </h2>
          
          {anyRunning && (
            <div className="flex items-center gap-2 px-2 py-1 rounded-full bg-accent/10 border border-accent/30">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
              </span>
              <span className="text-2xs font-medium text-accent">LIVE</span>
            </div>
          )}
          
          {allCompleted && (
            <div className="flex items-center gap-2 px-2 py-1 rounded-full bg-status-completed/10 border border-status-completed/30">
              <Zap className="w-3 h-3 text-status-completed" />
              <span className="text-2xs font-medium text-status-completed">COMPLETE</span>
            </div>
          )}
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1 p-1 rounded-lg bg-muted/50">
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "h-7 text-2xs gap-1.5",
              activeView === 'timeline' && "bg-background shadow-sm"
            )}
            onClick={() => setActiveView('timeline')}
          >
            <Activity className="w-3 h-3" />
            Timeline
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "h-7 text-2xs gap-1.5",
              activeView === 'events' && "bg-background shadow-sm"
            )}
            onClick={() => setActiveView('events')}
          >
            <Radio className="w-3 h-3" />
            Events
            {events.length > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-primary/20 text-primary text-2xs">
                {events.length}
              </span>
            )}
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeView === 'timeline' ? (
          /* Timeline View */
          <div className="space-y-1">
            {steps.map((step, index) => {
              const Icon = stepIcons[step.name] || Cpu;
              const isExpanded = expandedSteps.has(step.id);
              const isLast = index === steps.length - 1;
              const isRunning = step.status === 'RUNNING';
              const isCompleted = step.status === 'COMPLETED';
              const isQueued = step.status === 'QUEUED';
              
              return (
                <div key={step.id} className="relative">
                  {/* Connector Line */}
                  {!isLast && (
                    <div 
                      className={cn(
                        'absolute left-4 top-10 w-0.5 h-[calc(100%-1rem)]',
                        isCompleted ? 'bg-gradient-to-b from-primary via-primary/50 to-primary/20' : 'bg-border',
                        isRunning && 'animate-pulse'
                      )}
                    />
                  )}
                  
                  <button
                    onClick={() => toggleStep(step.id)}
                    disabled={isQueued}
                    className={cn(
                      'w-full flex items-start gap-3 p-3 rounded-lg text-left transition-all',
                      'hover:bg-muted/30',
                      isRunning && 'glass-card border border-accent/30 shadow-[0_0_15px_rgba(0,245,255,0.1)]',
                      isQueued && 'opacity-40 cursor-default'
                    )}
                  >
                    {/* Step Icon */}
                    <div 
                      className={cn(
                        'relative flex items-center justify-center w-8 h-8 rounded-full shrink-0',
                        isCompleted && 'bg-primary/20 text-primary',
                        isRunning && 'bg-accent/20 text-accent',
                        isQueued && 'bg-muted text-muted-foreground',
                        step.status === 'FAILED' && 'bg-destructive/20 text-destructive'
                      )}
                    >
                      <Icon className={cn("w-4 h-4", isRunning && "animate-pulse")} />
                      {isRunning && (
                        <span className="absolute inset-0 rounded-full animate-ping bg-accent/40" />
                      )}
                    </div>

                    {/* Step Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className={cn(
                          "text-sm font-medium truncate",
                          isRunning && "text-accent"
                        )}>
                          {step.name}
                        </span>
                        <div className="flex items-center gap-2">
                          <StatusBadge status={step.status} size="sm" />
                          {!isQueued && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                const stepEvent: EventEnvelope = {
                                  v: 1,
                                  seq: index + 1,
                                  ts: step.start_time,
                                  run_id: 'current',
                                  type: step.name.replace(/ /g, '_').toUpperCase(),
                                  step_id: step.id,
                                  payload: { ...step.inputs, ...step.outputs },
                                  explain: `Executed ${step.name} as part of the analysis flow.`,
                                };
                                openWhyDrawer(stepEvent);
                              }}
                              className="p-1 rounded hover:bg-primary/20 transition-colors"
                            >
                              <HelpCircle className="w-4 h-4 text-primary" />
                            </button>
                          )}
                          {!isQueued && (
                            isExpanded 
                              ? <ChevronDown className="w-4 h-4 text-muted-foreground" />
                              : <ChevronRight className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                      
                      {/* Meta info */}
                      <div className="flex items-center gap-3 text-2xs text-muted-foreground">
                        {step.duration_ms !== undefined && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {step.duration_ms}ms
                          </span>
                        )}
                        {step.tool_used && (
                          <span className="flex items-center gap-1">
                            <Cpu className="w-3 h-3" />
                            {step.tool_used}
                          </span>
                        )}
                      </div>
                    </div>
                  </button>
                  
                  {/* Expanded Details */}
                  {isExpanded && !isQueued && (
                    <div className="ml-11 mt-1 mb-3 p-3 rounded-lg bg-background border border-border animate-scale-in">
                      {step.inputs && Object.keys(step.inputs).length > 0 && (
                        <div className="mb-3">
                          <span className="text-2xs font-semibold text-muted-foreground uppercase">Inputs</span>
                          <pre className="mt-1 text-2xs font-mono text-foreground/80 overflow-x-auto max-h-24">
                            {JSON.stringify(step.inputs, null, 2)}
                          </pre>
                        </div>
                      )}
                      {step.outputs && Object.keys(step.outputs).length > 0 && (
                        <div>
                          <span className="text-2xs font-semibold text-muted-foreground uppercase">Outputs</span>
                          <pre className="mt-1 text-2xs font-mono text-foreground/80 overflow-x-auto max-h-24">
                            {JSON.stringify(step.outputs, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          /* Events View */
          <div className="space-y-1">
            {events.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm">
                No events yet
              </div>
            ) : (
              events.map((event) => (
                <button
                  key={`${event.run_id}-${event.seq}`}
                  onClick={() => openWhyDrawer(event)}
                  className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-muted/30 transition-colors text-left group"
                >
                  <span className="text-2xs font-mono text-muted-foreground w-6 text-right shrink-0">
                    #{event.seq}
                  </span>
                  
                  <span className={cn(
                    'px-2 py-0.5 rounded text-2xs font-medium border shrink-0',
                    eventTypeColors[event.type] || 'bg-muted text-foreground border-border'
                  )}>
                    {event.type.replace(/_/g, ' ')}
                  </span>
                  
                  <span className="flex-1 text-2xs text-muted-foreground truncate font-mono">
                    {JSON.stringify(event.payload).slice(0, 50)}...
                  </span>
                  
                  <span className="text-2xs text-muted-foreground shrink-0">
                    {new Date(event.ts).toLocaleTimeString()}
                  </span>
                  
                  <HelpCircle className="w-4 h-4 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
