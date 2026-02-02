import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Sparkles, Zap, Clock, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRuntimeStore } from '@/stores/runtimeStore';

interface ThinkingStep {
  id: string;
  message: string;
  timestamp: number;
  duration?: number;
  completed: boolean;
}

export function ElegantThinkingPanel() {
  const { events } = useRuntimeStore();
  const [steps, setSteps] = useState<ThinkingStep[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [isThinking, setIsThinking] = useState(false);
  const [totalDuration, setTotalDuration] = useState(0);

  useEffect(() => {
    const thinkingEvents = events.filter(e => 
      e.type === 'THINKING' || 
      e.type === 'ROUTER_DECISION' ||
      e.type === 'PLAN_GENERATED' ||
      e.type === 'TOOL_CALL' ||
      e.type === 'RAG_RETRIEVAL'
    );

    if (thinkingEvents.length > 0) {
      const newSteps = thinkingEvents.map((e, idx) => ({
        id: `step-${idx}`,
        message: e.explain || String(e.payload.message) || 'Processing...',
        timestamp: e.ts,
        duration: (e.payload.duration as number) || undefined,
        completed: idx < thinkingEvents.length - 1,
      }));

      setSteps(newSteps);
      setCurrentStep(newSteps[newSteps.length - 1]?.message || '');
      setIsThinking(true);

      const total = newSteps.reduce((sum, s) => sum + (s.duration || 0), 0);
      setTotalDuration(total);
    } else {
      setIsThinking(false);
    }
  }, [events]);

  if (!isThinking && steps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="relative mb-6">
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.6, 0.3],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute inset-0 rounded-full bg-primary/20 blur-2xl"
            />
            <Brain className="relative w-20 h-20 text-muted-foreground/40 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-foreground mb-2">
            Waiting for DiveCoder to start...
          </h3>
          <p className="text-sm text-muted-foreground max-w-md">
            The thinking panel will show AI reasoning when a task is running
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-6 overflow-hidden">
      {/* Header Section */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.div
              animate={isThinking ? {
                rotate: [0, 360],
                scale: [1, 1.1, 1],
              } : {}}
              transition={{
                duration: 3,
                repeat: isThinking ? Infinity : 0,
                ease: "easeInOut",
              }}
              className={cn(
                "p-3 rounded-2xl",
                isThinking 
                  ? "bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30" 
                  : "bg-green-500/20 border border-green-500/30"
              )}
            >
              {isThinking ? (
                <Sparkles className="w-6 h-6 text-cyan-400" />
              ) : (
                <CheckCircle2 className="w-6 h-6 text-green-500" />
              )}
            </motion.div>
            <div>
              <h2 className="text-xl font-semibold text-foreground">
                {isThinking ? 'AI is Thinking' : 'Thinking Complete'}
              </h2>
              <p className="text-sm text-muted-foreground">
                {steps.length} reasoning {steps.length === 1 ? 'step' : 'steps'}
              </p>
            </div>
          </div>
          {totalDuration > 0 && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-muted/50">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-mono text-foreground">
                {totalDuration.toFixed(1)}s
              </span>
            </div>
          )}
        </div>

        {/* Current Step Highlight */}
        {isThinking && currentStep && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative overflow-hidden rounded-2xl p-6 bg-gradient-to-br from-cyan-500/10 via-blue-500/10 to-purple-500/10 border border-cyan-500/20"
          >
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0"
              animate={{
                x: ['-100%', '100%'],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "linear",
              }}
            />
            <div className="relative flex items-start gap-4">
              <motion.div
                animate={{
                  rotate: 360,
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear",
                }}
              >
                <Zap className="w-5 h-5 text-cyan-400 flex-shrink-0" />
              </motion.div>
              <div className="flex-1">
                <p className="text-base text-foreground leading-relaxed">
                  {currentStep}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Steps Timeline */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ delay: index * 0.05 }}
              className={cn(
                "relative group",
                !step.completed && "opacity-60"
              )}
            >
              <div className={cn(
                "flex items-start gap-4 p-4 rounded-xl border transition-all duration-200",
                step.completed 
                  ? "bg-background/50 border-border/50 hover:border-primary/30 hover:bg-background/80" 
                  : "bg-muted/30 border-muted"
              )}>
                {/* Step Indicator */}
                <div className="flex-shrink-0 mt-0.5">
                  {step.completed ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 200, damping: 15 }}
                    >
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    </motion.div>
                  ) : (
                    <motion.div
                      animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.5, 1, 0.5],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                      className="w-5 h-5 rounded-full border-2 border-cyan-400/50 bg-cyan-400/20"
                    />
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground/90 leading-relaxed">
                    {step.message}
                  </p>
                  <div className="flex items-center gap-3 mt-2">
                    {step.duration && (
                      <span className="text-xs text-muted-foreground">
                        {step.duration.toFixed(1)}s
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground font-mono">
                      {new Date(step.timestamp * 1000).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="absolute left-[30px] top-[52px] w-[2px] h-[calc(100%+12px)] bg-gradient-to-b from-border to-transparent" />
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Active Indicator */}
      {isThinking && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 pt-4 border-t border-border/50"
        >
          <div className="flex items-center gap-3">
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                opacity: [1, 0.5, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="w-2 h-2 rounded-full bg-cyan-400"
            />
            <span className="text-xs text-cyan-400 font-medium">
              Actively reasoning...
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}
