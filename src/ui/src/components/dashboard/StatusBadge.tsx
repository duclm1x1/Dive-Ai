import { cn } from '@/lib/utils';
import type { RunStatus } from '@/types/observability';

interface StatusBadgeProps {
  status: RunStatus;
  size?: 'sm' | 'md';
  showPulse?: boolean;
}

const statusConfig: Record<RunStatus, { label: string; className: string }> = {
  QUEUED: {
    label: 'Queued',
    className: 'bg-status-queued/20 text-status-queued border-status-queued/30',
  },
  RUNNING: {
    label: 'Running',
    className: 'bg-status-running/20 text-status-running border-status-running/30',
  },
  WAITING: {
    label: 'Waiting',
    className: 'bg-status-waiting/20 text-status-waiting border-status-waiting/30',
  },
  COMPLETED: {
    label: 'Completed',
    className: 'bg-status-completed/20 text-status-completed border-status-completed/30',
  },
  FAILED: {
    label: 'Failed',
    className: 'bg-status-failed/20 text-status-failed border-status-failed/30',
  },
};

export function StatusBadge({ status, size = 'sm', showPulse = false }: StatusBadgeProps) {
  const config = statusConfig[status];
  
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border font-medium',
        config.className,
        size === 'sm' ? 'px-2 py-0.5 text-2xs' : 'px-3 py-1 text-xs'
      )}
    >
      {(status === 'RUNNING' || showPulse) && (
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75" />
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-current" />
        </span>
      )}
      {config.label}
    </span>
  );
}
