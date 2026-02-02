import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, CheckCircle2, Loader2, Circle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface ThinkingStep {
  id: number;
  name: string;
  analogy: string;
  status: 'complete' | 'active' | 'pending';
  icon: string;
}

interface EnhancedThinkingPanelProps {
  thinkingText: string;
  duration?: number;
  isActive?: boolean;
}

const DEFAULT_STEPS: ThinkingStep[] = [
  { id: 1, name: 'Understanding', analogy: 'Reading your code...', status: 'complete', icon: '📖' },
  { id: 2, name: 'Searching', analogy: 'Looking for patterns...', status: 'active', icon: '🔍' },
  { id: 3, name: 'Planning', analogy: 'Designing solution...', status: 'pending', icon: '📋' },
  { id: 4, name: 'Creating', analogy: 'Writing code...', status: 'pending', icon: '✍️' },
  { id: 5, name: 'Validating', analogy: 'Checking quality...', status: 'pending', icon: '✅' },
];

export function EnhancedThinkingPanel({ 
  thinkingText, 
  duration = 11, 
  isActive = true 
}: EnhancedThinkingPanelProps) {
  const [steps, setSteps] = useState<ThinkingStep[]>(DEFAULT_STEPS);
  const [currentStep, setCurrentStep] = useState(2);
  const [progress, setProgress] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(duration);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Simulate thinking progress
  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      setElapsedTime((prev) => {
        const next = prev + 0.1;
        if (next >= duration) {
          clearInterval(interval);
          return duration;
        }
        return next;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isActive, duration]);

  // Update progress and current step
  useEffect(() => {
    const progressPercent = Math.min((elapsedTime / duration) * 100, 100);
    setProgress(progressPercent);
    setTimeRemaining(Math.max(duration - elapsedTime, 0));

    // Update current step based on progress
    const stepIndex = Math.min(Math.floor((progressPercent / 100) * steps.length), steps.length - 1);
    setCurrentStep(stepIndex + 1);

    // Update step statuses
    setSteps((prevSteps) =>
      prevSteps.map((step, idx) => ({
        ...step,
        status:
          idx < stepIndex
            ? 'complete'
            : idx === stepIndex
            ? 'active'
            : 'pending',
      }))
    );
  }, [elapsedTime, duration, steps.length]);

  return (
    <Card className="p-6 bg-card/50 backdrop-blur-sm border-cyan-500/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 360],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <Brain className="w-6 h-6 text-cyan-400" />
          </motion.div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              AI is Thinking...
            </h3>
            <p className="text-sm text-muted-foreground">
              Step {currentStep} of {steps.length}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-cyan-400">
            {Math.round(progress)}%
          </div>
          <p className="text-xs text-muted-foreground">
            {timeRemaining.toFixed(1)}s remaining
          </p>
        </div>
      </div>

      {/* Step Visualization */}
      <div className="mb-6">
        <div className="flex items-center justify-between gap-2">
          {steps.map((step, idx) => (
            <div key={step.id} className="flex items-center flex-1">
              {/* Step Circle */}
              <motion.div
                className="relative"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: idx * 0.1 }}
              >
                <div
                  className={`
                    w-12 h-12 rounded-full flex items-center justify-center text-xl
                    transition-all duration-300
                    ${
                      step.status === 'complete'
                        ? 'bg-green-500/20 border-2 border-green-500'
                        : step.status === 'active'
                        ? 'bg-cyan-500/20 border-2 border-cyan-500 animate-pulse'
                        : 'bg-muted border-2 border-border'
                    }
                  `}
                >
                  {step.status === 'complete' ? (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  ) : step.status === 'active' ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Loader2 className="w-6 h-6 text-cyan-400" />
                    </motion.div>
                  ) : (
                    <Circle className="w-6 h-6 text-muted-foreground" />
                  )}
                </div>

                {/* Step Label */}
                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 w-20 text-center">
                  <p className="text-xs font-medium text-foreground truncate">
                    {step.name}
                  </p>
                </div>
              </motion.div>

              {/* Arrow */}
              {idx < steps.length - 1 && (
                <div className="flex-1 h-0.5 bg-border mx-2">
                  <motion.div
                    className="h-full bg-cyan-500"
                    initial={{ width: '0%' }}
                    animate={{
                      width:
                        step.status === 'complete'
                          ? '100%'
                          : step.status === 'active'
                          ? `${progress % 20}%`
                          : '0%',
                    }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Thinking Text with Analogy */}
      <div className="mt-12 space-y-4">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="p-4 rounded-lg bg-cyan-500/5 border border-cyan-500/20"
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{steps[currentStep - 1]?.icon}</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-cyan-400 mb-1">
                  {steps[currentStep - 1]?.analogy}
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {thinkingText || 'Processing your request...'}
                </p>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Progress Bar */}
        <div className="space-y-2">
          <Progress value={progress} className="h-2" />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>⏱️ Thinking for {elapsedTime.toFixed(1)}s</span>
            <span className="font-mono">{Math.round(progress)}% complete</span>
          </div>
        </div>
      </div>

      {/* Tasks List (if available) */}
      {progress > 50 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
          className="mt-6 pt-6 border-t border-border"
        >
          <h4 className="text-sm font-semibold text-foreground mb-3">
            Current Tasks
          </h4>
          <div className="space-y-2">
            {[
              'Analyzing code structure',
              'Identifying patterns',
              'Generating solution',
            ].map((task, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-center gap-2 text-sm"
              >
                {idx < currentStep - 2 ? (
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                ) : (
                  <Circle className="w-4 h-4 text-muted-foreground" />
                )}
                <span
                  className={
                    idx < currentStep - 2
                      ? 'text-green-500 line-through'
                      : 'text-foreground'
                  }
                >
                  {task}
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </Card>
  );
}
