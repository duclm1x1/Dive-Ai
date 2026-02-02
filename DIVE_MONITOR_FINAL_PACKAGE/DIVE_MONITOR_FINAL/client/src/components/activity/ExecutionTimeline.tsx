import { cn } from '@/lib/utils';
import { StatusBadge } from '../dashboard/StatusBadge';
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
  Sparkles
} from 'lucide-react';
import { useState } from 'react';

const stepIcons: Record<string, React.ElementType> = {
  'Router Decision': GitBranch,
  'Plan Generation': ListTree,
  'RAG Retrieval': Search,
  'Evidence Linking': Link2,
  'Report Generation': FileText,
};

interface ExecutionTimelineProps {
  steps: ExecutionStep[];
}

export function ExecutionTimeline({ steps }: ExecutionTimelineProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

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

  return (
    <div className="flex flex-col gap-1 p-4">
      <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        Execution Timeline
      </h2>
      
      <div className="relative">
        {steps.map((step, index) => {
          const Icon = stepIcons[step.name] || Cpu;
          const isExpanded = expandedSteps.has(step.id);
          const isLast = index === steps.length - 1;
          const isRunning = step.status === 'RUNNING';
          const isCompleted = step.status === 'COMPLETED';
          const isQueued = step.status === 'QUEUED';
          
          return (
            <div key={step.id} className="relative animate-fade-up" style={{ animationDelay: `${index * 50}ms` }}>
              {/* Connector Line */}
              {!isLast && (
                <div 
                  className={cn(
                    'absolute left-4 top-10 w-0.5 h-[calc(100%-1rem)]',
                    isCompleted ? 'bg-gradient-to-b from-primary/50 to-primary/20' : 'bg-border'
                  )}
                />
              )}
              
              <button
                onClick={() => toggleStep(step.id)}
                disabled={isQueued}
                className={cn(
                  'w-full flex items-start gap-3 p-3 rounded-lg text-left transition-all duration-200',
                  'hover:bg-muted/30',
                  isRunning && 'glass-card glow-border-green',
                  isQueued && 'opacity-50 cursor-default'
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
                  <Icon className="w-4 h-4" />
                  {isRunning && (
                    <span className="absolute inset-0 rounded-full animate-ping bg-accent/30" />
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-sm font-medium truncate">{step.name}</span>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={step.status} size="sm" />
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
                    {step.llm_used && (
                      <span className="flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        {step.llm_used}
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
                      <pre className="mt-1 text-2xs font-mono text-foreground/80 overflow-x-auto">
                        {JSON.stringify(step.inputs, null, 2)}
                      </pre>
                    </div>
                  )}
                  {step.outputs && Object.keys(step.outputs).length > 0 && (
                    <div>
                      <span className="text-2xs font-semibold text-muted-foreground uppercase">Outputs</span>
                      <pre className="mt-1 text-2xs font-mono text-foreground/80 overflow-x-auto">
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
    </div>
  );
}
