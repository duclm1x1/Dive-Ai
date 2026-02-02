import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, CheckCircle2, Loader2, Circle, Clock } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useRuntimeStore } from '@/stores/runtimeStore';

interface ThinkingEvent {
  timestamp: number;
  message: string;
  duration?: number;
  step?: string;
}

interface RealTimeThinkingPanelProps {
  runId?: string;
}

export function RealTimeThinkingPanel({ runId }: RealTimeThinkingPanelProps) {
  const { events } = useRuntimeStore();
  const [thinkingEvents, setThinkingEvents] = useState<ThinkingEvent[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Filter thinking events from real DiveCoder execution
  useEffect(() => {
    const thinking = events.filter(
      (e) =>
        e.type === 'THINKING' &&
        (!runId || e.run_id === runId)
    );

    if (thinking.length > 0) {
      setThinkingEvents(
        thinking.map((e) => ({
          timestamp: e.ts,
          message: String(e.explain || (e.payload as any)?.message || 'Processing...'),
          duration: (e.payload as any)?.duration as number | undefined,
          step: (e.payload as any)?.step as string | undefined,
        }))
      );
      setIsThinking(true);
      setCurrentMessage(thinking[thinking.length - 1].explain || 'Thinking...');
      
      if (!startTime) {
        setStartTime(thinking[0].ts);
      }
    } else {
      setIsThinking(false);
    }
  }, [events, runId, startTime]);

  // Update elapsed time
  useEffect(() => {
    if (!isThinking || !startTime) return;

    const interval = setInterval(() => {
      setElapsedTime((Date.now() / 1000) - startTime);
    }, 100);

    return () => clearInterval(interval);
  }, [isThinking, startTime]);

  // If no thinking events, show idle state
  if (!isThinking && thinkingEvents.length === 0) {
    return (
      <Card className="p-6 bg-card/50 backdrop-blur-sm border-border/50">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Brain className="w-16 h-16 text-muted-foreground/30 mb-4" />
          <p className="text-sm text-muted-foreground">
            Waiting for DiveCoder to start...
          </p>
          <p className="text-xs text-muted-foreground/60 mt-2">
            The thinking panel will show AI reasoning when a task is running
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-card/50 backdrop-blur-sm border-cyan-500/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <motion.div
            animate={
              isThinking
                ? {
                    scale: [1, 1.2, 1],
                    rotate: [0, 360],
                  }
                : {}
            }
            transition={{
              duration: 2,
              repeat: isThinking ? Infinity : 0,
              ease: 'easeInOut',
            }}
          >
            <Brain className={`w-6 h-6 ${isThinking ? 'text-cyan-400' : 'text-green-500'}`} />
          </motion.div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              {isThinking ? 'AI is Thinking...' : 'Thinking Complete'}
            </h3>
            <p className="text-sm text-muted-foreground">
              {thinkingEvents.length} reasoning {thinkingEvents.length === 1 ? 'step' : 'steps'}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4" />
            <span className="font-mono">{elapsedTime.toFixed(1)}s</span>
          </div>
        </div>
      </div>

      {/* Current Thinking Message */}
      {isThinking && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 rounded-lg bg-cyan-500/5 border border-cyan-500/20"
        >
          <div className="flex items-start gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <Loader2 className="w-5 h-5 text-cyan-400 flex-shrink-0" />
            </motion.div>
            <div className="flex-1">
              <p className="text-sm text-foreground leading-relaxed">
                {currentMessage}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Thinking History */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {thinkingEvents.map((event, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="flex items-start gap-3 p-3 rounded-lg bg-background/50 border border-border/50"
          >
            <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-foreground/90 leading-relaxed">
                {event.message}
              </p>
              {event.duration && (
                <p className="text-xs text-muted-foreground mt-1">
                  Took {event.duration.toFixed(1)}s
                </p>
              )}
            </div>
            <span className="text-xs text-muted-foreground font-mono flex-shrink-0">
              {new Date(event.timestamp * 1000).toLocaleTimeString()}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Active Indicator */}
      {isThinking && (
        <div className="mt-4 pt-4 border-t border-border">
          <div className="flex items-center gap-2 text-xs text-cyan-400">
            <motion.div
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-2 h-2 rounded-full bg-cyan-400"
            />
            <span>Actively reasoning...</span>
          </div>
        </div>
      )}
    </Card>
  );
}
