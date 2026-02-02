import { useState, useEffect } from 'react';
import { Zap, DollarSign, Scale, Info, CheckCircle2, Loader2 } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

type OptimizationMode = 'fastest' | 'cheapest' | 'balanced';

interface OptimizationModeOption {
  id: OptimizationMode;
  name: string;
  icon: React.ReactNode;
  description: string;
  color: string;
  bgColor: string;
  borderColor: string;
}

const OPTIMIZATION_MODES: OptimizationModeOption[] = [
  {
    id: 'fastest',
    name: 'Fastest',
    icon: <Zap className="w-5 h-5" />,
    description: 'Prioritize speed - use the fastest responding provider',
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/50',
  },
  {
    id: 'cheapest',
    name: 'Cheapest',
    icon: <DollarSign className="w-5 h-5" />,
    description: 'Prioritize cost - use the most economical provider',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/50',
  },
  {
    id: 'balanced',
    name: 'Balanced',
    icon: <Scale className="w-5 h-5" />,
    description: 'Balance speed and cost - optimal for most use cases',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/50',
  },
];

export function OptimizationModeSettings() {
  const [selectedMode, setSelectedMode] = useState<OptimizationMode>('balanced');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();

  // Load current optimization mode from backend
  useEffect(() => {
    loadOptimizationMode();
  }, []);

  const loadOptimizationMode = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8787/v1/optimization/mode');
      if (response.ok) {
        const data = await response.json();
        setSelectedMode(data.mode || 'balanced');
      }
    } catch (error) {
      console.warn('Failed to load optimization mode:', error);
      // Use default mode if backend is not available
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeChange = async (mode: OptimizationMode) => {
    setSelectedMode(mode);
    setIsSaving(true);

    try {
      const response = await fetch('http://localhost:8787/v1/optimization/mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Optimization mode updated',
          description: `Now using ${mode} provider: ${data.selected_provider || 'Auto'}`,
        });
      } else {
        throw new Error('Failed to update optimization mode');
      }
    } catch (error) {
      console.error('Failed to save optimization mode:', error);
      toast({
        title: 'Failed to update mode',
        description: 'Could not connect to monitor server',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="glass-card p-6">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-start gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
          <Scale className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1">
          <h2 className="text-base font-semibold mb-1">Provider Optimization</h2>
          <p className="text-sm text-muted-foreground">
            Choose how DiveCoder selects the best LLM provider for each request
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {OPTIMIZATION_MODES.map((mode) => {
          const isSelected = selectedMode === mode.id;
          
          return (
            <button
              key={mode.id}
              onClick={() => handleModeChange(mode.id)}
              disabled={isSaving}
              className={`
                w-full p-4 rounded-lg border-2 transition-all text-left
                ${isSelected 
                  ? `${mode.borderColor} ${mode.bgColor}` 
                  : 'border-border bg-card/50 hover:bg-card hover:border-border/80'
                }
                ${isSaving ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="flex items-start gap-3">
                <div className={`${isSelected ? mode.color : 'text-muted-foreground'}`}>
                  {mode.icon}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-semibold">{mode.name}</h3>
                    {isSelected && (
                      <CheckCircle2 className={`w-4 h-4 ${mode.color}`} />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {mode.description}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="mt-6 p-4 rounded-lg bg-muted/50 border border-border">
        <div className="flex items-start gap-2">
          <Info className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div className="text-xs text-muted-foreground">
            <p className="mb-2">
              The optimizer automatically selects the best provider based on real-time performance data:
            </p>
            <ul className="space-y-1 ml-4 list-disc">
              <li><strong>Fastest:</strong> Uses provider with lowest average latency</li>
              <li><strong>Cheapest:</strong> Uses provider with lowest cost per token</li>
              <li><strong>Balanced:</strong> Optimizes for speed/cost ratio (recommended)</li>
            </ul>
            <p className="mt-2">
              Unhealthy providers are automatically excluded from selection.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
