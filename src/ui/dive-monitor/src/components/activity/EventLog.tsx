import { useState } from 'react';
import { ChevronRight, HelpCircle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRuntimeStore, type EventEnvelope } from '@/stores/runtimeStore';
import { Button } from '@/components/ui/button';

const eventTypeColors: Record<string, string> = {
  'ROUTER_DECISION': 'bg-primary/20 text-primary border-primary/30',
  'PLAN_GENERATED': 'bg-accent/20 text-accent border-accent/30',
  'RAG_RETRIEVAL': 'bg-info/20 text-info border-info/30',
  'RAG_RERANK': 'bg-info/20 text-info border-info/30',
  'TOOL_CALL': 'bg-warning/20 text-warning border-warning/30',
  'EVIDENCE_LINKED': 'bg-success/20 text-success border-success/30',
  'CLAIM_CREATED': 'bg-success/20 text-success border-success/30',
  'REPORT_GENERATED': 'bg-primary/20 text-primary border-primary/30',
  'LLM_CALL': 'bg-accent/20 text-accent border-accent/30',
  'ERROR': 'bg-destructive/20 text-destructive border-destructive/30',
};

interface EventLogProps {
  events: EventEnvelope[];
  maxEvents?: number;
}

export function EventLog({ events, maxEvents = 20 }: EventLogProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { openWhyDrawer } = useRuntimeStore();
  
  const displayedEvents = isExpanded ? events : events.slice(-maxEvents);
  
  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Event Stream
        </h3>
        <div className="flex items-center gap-2 text-2xs text-muted-foreground">
          <span>{events.length} events</span>
          {events.length > maxEvents && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-2xs"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Collapse' : 'Show All'}
            </Button>
          )}
        </div>
      </div>
      
      <div className="space-y-1 max-h-64 overflow-y-auto">
        {displayedEvents.map((event) => (
          <button
            key={`${event.run_id}-${event.seq}`}
            onClick={() => openWhyDrawer(event)}
            className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-muted/30 transition-colors text-left group"
          >
            {/* Sequence number */}
            <span className="text-2xs font-mono text-muted-foreground w-6 text-right shrink-0">
              #{event.seq}
            </span>
            
            {/* Event type badge */}
            <span className={cn(
              'px-2 py-0.5 rounded text-2xs font-medium border shrink-0',
              eventTypeColors[event.type] || 'bg-muted text-foreground border-border'
            )}>
              {event.type.replace(/_/g, ' ')}
            </span>
            
            {/* Payload preview */}
            <span className="flex-1 text-2xs text-muted-foreground truncate font-mono">
              {JSON.stringify(event.payload).slice(0, 60)}...
            </span>
            
            {/* Timestamp */}
            <span className="text-2xs text-muted-foreground shrink-0 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(event.ts).toLocaleTimeString()}
            </span>
            
            {/* Why button */}
            <div className="opacity-0 group-hover:opacity-100 transition-opacity">
              <HelpCircle className="w-4 h-4 text-primary" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
