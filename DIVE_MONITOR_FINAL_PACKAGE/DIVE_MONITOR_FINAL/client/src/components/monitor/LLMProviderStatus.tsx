import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Zap, AlertCircle, CheckCircle2 } from "lucide-react";

interface ProviderStatus {
  name: string;
  model: string;
  type: string;
  active: boolean;
  lastUsed?: number;
}

interface LLMProviderStatusProps {
  events?: any[];
}

export function LLMProviderStatus({ events = [] }: LLMProviderStatusProps) {
  const [currentProvider, setCurrentProvider] = useState<ProviderStatus | null>(null);
  const [providerHistory, setProviderHistory] = useState<ProviderStatus[]>([]);

  useEffect(() => {
    // Find the most recent LLM provider event
    const statusEvents = events
      .filter(e => e.event_type === 'status' && e.data?.provider)
      .reverse();

    if (statusEvents.length > 0) {
      const latestEvent = statusEvents[0];
      const provider: ProviderStatus = {
        name: latestEvent.data.provider,
        model: latestEvent.data.model,
        type: latestEvent.data.type,
        active: true,
        lastUsed: latestEvent.timestamp
      };
      
      setCurrentProvider(provider);
      
      // Update history (keep last 5)
      setProviderHistory(prev => {
        const newHistory = [provider, ...prev.filter(p => p.name !== provider.name)];
        return newHistory.slice(0, 5);
      });
    }
  }, [events]);

  if (!currentProvider && providerHistory.length === 0) {
    return null;
  }

  return (
    <Card className="border-border/50 bg-background/40 backdrop-blur-sm">
      <CardContent className="p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">LLM Provider</h3>
            <p className="text-xs text-muted-foreground">Current AI model in use</p>
          </div>
        </div>

        {currentProvider && (
          <div className="space-y-3">
            {/* Current Provider */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-primary/5 border border-primary/20">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Zap className="w-5 h-5 text-primary" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full animate-pulse" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">
                    {currentProvider.name}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {currentProvider.model}
                  </div>
                </div>
              </div>
              <Badge variant="default" className="bg-primary/20 text-primary border-primary/30">
                <CheckCircle2 className="w-3 h-3 mr-1" />
                Active
              </Badge>
            </div>

            {/* Provider History */}
            {providerHistory.length > 1 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-muted-foreground">Recent Providers</div>
                <div className="space-y-1">
                  {providerHistory.slice(1).map((provider, idx) => (
                    <div
                      key={`${provider.name}-${idx}`}
                      className="flex items-center justify-between p-2 rounded bg-muted/30"
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-1 h-1 rounded-full bg-muted-foreground/50" />
                        <div className="text-xs text-muted-foreground">
                          {provider.name} ({provider.model})
                        </div>
                      </div>
                      {provider.lastUsed && (
                        <div className="text-2xs text-muted-foreground/70">
                          {new Date(provider.lastUsed * 1000).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Provider Type Badge */}
            <div className="flex items-center gap-2 pt-2 border-t border-border/50">
              <div className="text-2xs text-muted-foreground">Type:</div>
              <Badge variant="outline" className="text-2xs">
                {currentProvider.type}
              </Badge>
            </div>
          </div>
        )}

        {!currentProvider && providerHistory.length > 0 && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-muted/30">
            <AlertCircle className="w-4 h-4 text-muted-foreground" />
            <div className="text-xs text-muted-foreground">
              No active provider. Last used: {providerHistory[0].name}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
