import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import { StatusBadge } from '@/components/dashboard/StatusBadge';
import type { Run, RunType } from '@/types/observability';
import { Code, GitPullRequest, Hammer, Database, BarChart3 } from 'lucide-react';

const typeConfig: Record<RunType, { label: string; icon: React.ElementType; className: string }> = {
  review: { label: 'Review', icon: Code, className: 'text-primary' },
  resolve: { label: 'Resolve', icon: GitPullRequest, className: 'text-accent' },
  build: { label: 'Build', icon: Hammer, className: 'text-warning' },
  rag_ingest: { label: 'RAG Ingest', icon: Database, className: 'text-info' },
  rag_eval: { label: 'RAG Eval', icon: BarChart3, className: 'text-secondary-foreground' },
};

interface RunListProps {
  runs: Run[];
  selectedRunId?: string;
  onSelectRun: (runId: string) => void;
}

export function RunList({ runs, selectedRunId, onSelectRun }: RunListProps) {
  if (runs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center p-6">
        <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mb-4">
          <Code className="w-8 h-8 text-muted-foreground" />
        </div>
        <h3 className="text-sm font-medium text-foreground mb-1">No runs yet</h3>
        <p className="text-2xs text-muted-foreground">
          Runs will appear here when Dive Coder executes commands
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 p-3">
      <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 mb-1">
        Run History
      </h2>
      {runs.map((run) => {
        const config = typeConfig[run.type];
        const Icon = config.icon;
        const isSelected = selectedRunId === run.run_id;
        
        return (
          <button
            key={run.run_id}
            onClick={() => onSelectRun(run.run_id)}
            className={cn(
              'flex flex-col gap-2 p-3 rounded-lg text-left transition-all duration-200',
              'hover:bg-muted/50',
              isSelected
                ? 'glass-card-elevated border-primary/30 glow-border'
                : 'bg-card/30 border border-border/50'
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Icon className={cn('w-4 h-4', config.className)} />
                <span className="text-sm font-medium">{config.label}</span>
              </div>
              <StatusBadge status={run.status} />
            </div>
            
            <div className="flex items-center justify-between text-2xs text-muted-foreground">
              <span className="font-mono">{run.run_id.slice(0, 12)}</span>
              <span>
                {formatDistanceToNow(run.start_time, { addSuffix: true })}
              </span>
            </div>
            
            {run.duration_ms && (
              <div className="text-2xs text-muted-foreground">
                Duration: {(run.duration_ms / 1000).toFixed(1)}s
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}
