import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import { StatusBadge } from '../dashboard/StatusBadge';
import { useRuntimeStore, type EventEnvelope } from '@/stores/runtimeStore';
import type { ExecutionStep, RunStatus } from '@/types/observability';
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
  HelpCircle
} from 'lucide-react';

const stepIcons: Record<string, React.ElementType> = {
  'Router Decision': GitBranch,
  'Plan Generation': ListTree,
  'RAG Retrieval': Search,
  'Tool Execution': Terminal,
  'Evidence Linking': Link2,
  'Report Generation': FileText,
};

// Live action messages for each step type
const liveMessages: Record<string, string[]> = {
  'Router Decision': [
    'Analyzing user intent...',
    'Classifying request type...',
    'Selecting optimal route...',
    'Route: code_review (95% confidence)',
  ],
  'Plan Generation': [
    'Decomposing task...',
    'Identifying required tools...',
    'Estimating resource budget...',
    'Plan ready: 5 steps, 3 tools',
  ],
  'RAG Retrieval': [
    'Enhancing query...',
    'Running BM25 search...',
    'Fetching GraphRAG neighbors...',
    'Reranking 24 chunks...',
    'Selected top 8 chunks (45k chars)',
  ],
  'Tool Execution': [
    'Reading src/auth/handler.ts...',
    'Parsing AST...',
    'Extracting function signatures...',
    'Found 12 relevant symbols',
  ],
  'Evidence Linking': [
    'Mapping code to claims...',
    'Validating evidence chain...',
    'Computing confidence scores...',
    'Linked 3 evidence items',
  ],
  'Report Generation': [
    'Synthesizing findings...',
    'Formatting markdown...',
    'Adding code references...',
    'Report complete ✓',
  ],
};

interface LiveStep extends ExecutionStep {
  liveMessage?: string;
  messageIndex?: number;
  elapsedMs?: number;
}

interface LiveExecutionTimelineProps {
  steps: ExecutionStep[];
  isLive?: boolean;
}

// Generate explanation for a step
function generateStepExplanation(step: ExecutionStep): string {
  switch (step.name) {
    case 'Router Decision':
      return `Analyzed the user request and determined the optimal processing route based on intent classification and available tools.`;
    case 'Plan Generation':
      return `Decomposed the task into ${step.outputs?.steps || 'multiple'} executable steps using ${(step.outputs?.tools as string[])?.join(', ') || 'available tools'}.`;
    case 'RAG Retrieval':
      return `Searched the codebase using ${step.tool_used || 'hybrid retrieval'} to find relevant context for: "${step.inputs?.query || 'the query'}".`;
    case 'Tool Execution':
      return `Executed tool to gather information needed for the analysis.`;
    case 'Evidence Linking':
      return `Mapped discovered code patterns to verifiable claims with confidence scoring.`;
    case 'Report Generation':
      return `Synthesized all findings and evidence into a structured report.`;
    default:
      return `Completed processing step as part of the execution plan.`;
  }
}

export function LiveExecutionTimeline({ steps: initialSteps, isLive = true }: LiveExecutionTimelineProps) {
  const [steps, setSteps] = useState<LiveStep[]>(initialSteps);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(Date.now());
  const { openWhyDrawer } = useRuntimeStore();

  // Simulate live updates
  useEffect(() => {
    if (!isLive) return;

    intervalRef.current = setInterval(() => {
      setSteps(prev => {
        const newSteps = [...prev];
        const runningIndex = newSteps.findIndex(s => s.status === 'RUNNING');
        
        if (runningIndex === -1) return prev;
        
        const runningStep = { ...newSteps[runningIndex] };
        const messages = liveMessages[runningStep.name] || ['Processing...'];
        const currentMsgIndex = runningStep.messageIndex ?? 0;
        
        // Update elapsed time
        runningStep.elapsedMs = (runningStep.elapsedMs || 0) + 200;
        
        // Cycle through messages
        if (currentMsgIndex < messages.length) {
          runningStep.liveMessage = messages[currentMsgIndex];
          runningStep.messageIndex = currentMsgIndex + 1;
        }
        
        // Complete step after all messages
        if (currentMsgIndex >= messages.length - 1 && runningStep.elapsedMs > 2000) {
          runningStep.status = 'COMPLETED';
          runningStep.duration_ms = runningStep.elapsedMs;
          runningStep.end_time = Date.now();
          
          // Start next step
          const nextIndex = runningIndex + 1;
          if (nextIndex < newSteps.length && newSteps[nextIndex].status === 'QUEUED') {
            newSteps[nextIndex] = {
              ...newSteps[nextIndex],
              status: 'RUNNING',
              start_time: Date.now(),
              messageIndex: 0,
              elapsedMs: 0,
            };
          }
        }
        
        newSteps[runningIndex] = runningStep;
        return newSteps;
      });
    }, 400);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isLive]);

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

  const allCompleted = steps.every(s => s.status === 'COMPLETED');
  const anyRunning = steps.some(s => s.status === 'RUNNING');

  return (
    <div className="flex flex-col gap-1 p-4">
      {/* Header with live indicator */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Execution Timeline
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
      
      <div className="relative">
        {steps.map((step, index) => {
          const Icon = stepIcons[step.name] || Cpu;
          const isExpanded = expandedSteps.has(step.id);
          const isLast = index === steps.length - 1;
          const isRunning = step.status === 'RUNNING';
          const isCompleted = step.status === 'COMPLETED';
          const isQueued = step.status === 'QUEUED';
          const liveStep = step as LiveStep;
          
          return (
            <div 
              key={step.id} 
              className={cn(
                "relative transition-all duration-300",
                isCompleted && "animate-fade-in"
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Connector Line */}
              {!isLast && (
                <div 
                  className={cn(
                    'absolute left-4 top-10 w-0.5 transition-all duration-500',
                    isCompleted ? 'bg-gradient-to-b from-primary via-primary/50 to-primary/20' : 'bg-border',
                    isRunning ? 'h-[calc(100%-1rem)] animate-pulse' : 'h-[calc(100%-1rem)]'
                  )}
                >
                  {isRunning && (
                    <div className="absolute inset-0 bg-gradient-to-b from-accent to-transparent animate-pulse" />
                  )}
                </div>
              )}
              
              <button
                onClick={() => toggleStep(step.id)}
                disabled={isQueued}
                className={cn(
                  'w-full flex items-start gap-3 p-3 rounded-lg text-left transition-all duration-300',
                  'hover:bg-muted/30',
                  isRunning && 'glass-card border border-accent/30 shadow-[0_0_20px_rgba(0,245,255,0.15)]',
                  isQueued && 'opacity-40 cursor-default',
                  isCompleted && 'hover:border-primary/20'
                )}
              >
                {/* Step Icon */}
                <div 
                  className={cn(
                    'relative flex items-center justify-center w-8 h-8 rounded-full shrink-0 transition-all duration-300',
                    isCompleted && 'bg-primary/20 text-primary',
                    isRunning && 'bg-accent/20 text-accent',
                    isQueued && 'bg-muted text-muted-foreground',
                    step.status === 'FAILED' && 'bg-destructive/20 text-destructive'
                  )}
                >
                  <Icon className={cn("w-4 h-4", isRunning && "animate-pulse")} />
                  {isRunning && (
                    <>
                      <span className="absolute inset-0 rounded-full animate-ping bg-accent/40" />
                      <span className="absolute inset-[-4px] rounded-full border-2 border-accent/30 animate-pulse" />
                    </>
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className={cn(
                      "text-sm font-medium truncate transition-colors",
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
                            // Create a synthetic event envelope for this step
                            const stepEvent: EventEnvelope = {
                              v: 1,
                              seq: index + 1,
                              ts: step.start_time,
                              run_id: 'current',
                              type: step.name.replace(/ /g, '_').toUpperCase(),
                              step_id: step.id,
                              payload: {
                                ...step.inputs,
                                ...step.outputs,
                                duration_ms: step.duration_ms,
                                tool: step.tool_used,
                                llm: step.llm_used,
                              },
                              explain: generateStepExplanation(step),
                            };
                            openWhyDrawer(stepEvent);
                          }}
                          className="p-1 rounded hover:bg-primary/20 transition-colors"
                          title="Why did this happen?"
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
                  
                  {/* Live Message - Typewriter effect */}
                  {isRunning && liveStep.liveMessage && (
                    <div className="flex items-center gap-2 mb-2">
                      <span className="inline-flex h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
                      <span className="text-xs text-accent font-mono animate-fade-in">
                        {liveStep.liveMessage}
                      </span>
                    </div>
                  )}
                  
                  {/* Meta info */}
                  <div className="flex items-center gap-3 text-2xs text-muted-foreground">
                    {(step.duration_ms !== undefined || liveStep.elapsedMs) && (
                      <span className={cn(
                        "flex items-center gap-1",
                        isRunning && "text-accent"
                      )}>
                        <Clock className="w-3 h-3" />
                        {isRunning ? `${liveStep.elapsedMs || 0}ms` : `${step.duration_ms}ms`}
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
                <div className="ml-11 mt-1 mb-3 p-3 rounded-lg bg-background border border-border animate-scale-in overflow-hidden">
                  {step.inputs && Object.keys(step.inputs).length > 0 && (
                    <div className="mb-3">
                      <span className="text-2xs font-semibold text-muted-foreground uppercase">Inputs</span>
                      <pre className="mt-1 text-2xs font-mono text-foreground/80 overflow-x-auto max-h-32">
                        {JSON.stringify(step.inputs, null, 2)}
                      </pre>
                    </div>
                  )}
                  {step.outputs && Object.keys(step.outputs).length > 0 && (
                    <div>
                      <span className="text-2xs font-semibold text-muted-foreground uppercase">Outputs</span>
                      <pre className="mt-1 text-2xs font-mono text-foreground/80 overflow-x-auto max-h-32">
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
