import { X, Lightbulb, Clock, Cpu, FileText, ArrowRight, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useRuntimeStore, type EventEnvelope } from '@/stores/runtimeStore';
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
  DrawerClose,
} from '@/components/ui/drawer';

const eventTypeLabels: Record<string, string> = {
  'ROUTER_DECISION': 'Router Decision',
  'PLAN_GENERATED': 'Plan Generated',
  'RAG_RETRIEVAL': 'RAG Retrieval',
  'RAG_RERANK': 'Reranking',
  'TOOL_CALL': 'Tool Execution',
  'EVIDENCE_LINKED': 'Evidence Linked',
  'CLAIM_CREATED': 'Claim Created',
  'REPORT_GENERATED': 'Report Generated',
  'LLM_CALL': 'LLM Call',
  'STEP_STARTED': 'Step Started',
  'STEP_COMPLETED': 'Step Completed',
  'ERROR': 'Error',
};

const eventTypeColors: Record<string, string> = {
  'ROUTER_DECISION': 'text-primary',
  'PLAN_GENERATED': 'text-accent',
  'RAG_RETRIEVAL': 'text-info',
  'RAG_RERANK': 'text-info',
  'TOOL_CALL': 'text-warning',
  'EVIDENCE_LINKED': 'text-success',
  'CLAIM_CREATED': 'text-success',
  'REPORT_GENERATED': 'text-primary',
  'LLM_CALL': 'text-accent',
  'ERROR': 'text-destructive',
};

interface SignalItem {
  label: string;
  value: string | number | boolean;
  type: 'string' | 'number' | 'boolean' | 'array';
}

function extractSignals(payload: Record<string, unknown>): SignalItem[] {
  const signals: SignalItem[] = [];
  
  for (const [key, value] of Object.entries(payload)) {
    if (value === null || value === undefined) continue;
    
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    
    if (typeof value === 'boolean') {
      signals.push({ label, value, type: 'boolean' });
    } else if (typeof value === 'number') {
      signals.push({ label, value, type: 'number' });
    } else if (typeof value === 'string') {
      signals.push({ label, value, type: 'string' });
    } else if (Array.isArray(value)) {
      signals.push({ label, value: value.join(', '), type: 'array' });
    }
  }
  
  return signals;
}

function SignalBadge({ signal }: { signal: SignalItem }) {
  const colorClass = 
    signal.type === 'boolean' 
      ? (signal.value ? 'bg-success/20 text-success' : 'bg-destructive/20 text-destructive')
      : signal.type === 'number'
      ? 'bg-primary/20 text-primary'
      : 'bg-muted text-foreground';
  
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg bg-background border border-border">
      <span className="text-2xs text-muted-foreground">{signal.label}</span>
      <span className={cn('text-xs font-mono px-2 py-0.5 rounded', colorClass)}>
        {typeof signal.value === 'boolean' ? (signal.value ? 'Yes' : 'No') : String(signal.value)}
      </span>
    </div>
  );
}

export function WhyDrawer() {
  const { isWhyDrawerOpen, selectedEventForWhy, closeWhyDrawer } = useRuntimeStore();
  
  if (!selectedEventForWhy) return null;
  
  const event = selectedEventForWhy;
  const signals = extractSignals(event.payload);
  const eventLabel = eventTypeLabels[event.type] || event.type;
  const colorClass = eventTypeColors[event.type] || 'text-foreground';
  
  return (
    <Drawer open={isWhyDrawerOpen} onOpenChange={(open) => !open && closeWhyDrawer()}>
      <DrawerContent className="max-h-[85vh]">
        <div className="mx-auto w-full max-w-2xl">
          <DrawerHeader className="text-left">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn('p-2 rounded-lg bg-primary/10', colorClass)}>
                  <Lightbulb className="w-5 h-5" />
                </div>
                <div>
                  <DrawerTitle className="text-lg">Why This Happened</DrawerTitle>
                  <DrawerDescription className={cn('text-sm font-medium', colorClass)}>
                    {eventLabel}
                  </DrawerDescription>
                </div>
              </div>
              <DrawerClose asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <X className="w-4 h-4" />
                </Button>
              </DrawerClose>
            </div>
          </DrawerHeader>
          
          <div className="px-4 pb-6 space-y-6">
            {/* Explanation */}
            <div className="glass-card p-4">
              <div className="flex items-start gap-3">
                <Zap className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                <p className="text-sm text-foreground leading-relaxed">
                  {event.explain || 'No explanation available for this event.'}
                </p>
              </div>
            </div>
            
            {/* Signals Grid */}
            {signals.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                  Signals & Parameters
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {signals.map((signal, i) => (
                    <SignalBadge key={i} signal={signal} />
                  ))}
                </div>
              </div>
            )}
            
            {/* Timing */}
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>
                  {new Date(event.ts).toLocaleTimeString()}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xs text-muted-foreground">seq</span>
                <span className="font-mono text-xs">{event.seq}</span>
              </div>
              {event.step_id && (
                <div className="flex items-center gap-2">
                  <span className="text-2xs text-muted-foreground">step</span>
                  <span className="font-mono text-xs">{event.step_id}</span>
                </div>
              )}
            </div>
            
            {/* Raw Payload */}
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                Raw Payload
              </h4>
              <pre className="p-3 rounded-lg bg-background border border-border text-2xs font-mono text-foreground/80 overflow-x-auto max-h-48">
                {JSON.stringify(event.payload, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
