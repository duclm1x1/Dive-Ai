import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Activity, DollarSign, Zap, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { CallHistoryTable } from "./CallHistoryTable";

interface ProviderHealth {
  provider_id: string;
  provider_name: string;
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  total_tokens: number;
  total_cost: number;
  avg_latency_ms: number;
  last_success?: number;
  last_failure?: number;
  consecutive_failures: number;
  is_healthy: boolean;
  success_rate: number;
  failure_rate: number;
}

interface HealthSummary {
  providers: ProviderHealth[];
  total_calls: number;
  total_cost: number;
  total_tokens: number;
}

export function ProviderHealthDashboard() {
  const [healthData, setHealthData] = useState<HealthSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadHealthData = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787'}/v1/providers/health`);
      if (response.ok) {
        const data = await response.json();
        setHealthData(data);
      }
    } catch (error) {
      console.error("Failed to load health data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHealthData();
    const interval = setInterval(loadHealthData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <Activity className="w-5 h-5 animate-spin text-muted-foreground" />
            <span className="ml-2 text-sm text-muted-foreground">Loading health data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!healthData || healthData.providers.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-sm text-muted-foreground">
            No health data available. Make some LLM calls to see metrics.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Overall Summary */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="text-lg">Provider Health & Cost Tracking</CardTitle>
          <CardDescription>Real-time monitoring of LLM provider performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1">
              <div className="text-xs text-muted-foreground">Total Calls</div>
              <div className="text-2xl font-bold text-foreground">{healthData.total_calls}</div>
            </div>
            <div className="space-y-1">
              <div className="text-xs text-muted-foreground">Total Cost</div>
              <div className="text-2xl font-bold text-primary">${healthData.total_cost.toFixed(4)}</div>
            </div>
            <div className="space-y-1">
              <div className="text-xs text-muted-foreground">Total Tokens</div>
              <div className="text-2xl font-bold text-foreground">{healthData.total_tokens.toLocaleString()}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Provider Details */}
      {healthData.providers.map((provider) => (
        <Card key={provider.provider_id} className="border-border/50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${provider.is_healthy ? 'bg-green-500' : 'bg-red-500'}`} />
                <CardTitle className="text-base">{provider.provider_name}</CardTitle>
              </div>
              <Badge 
                variant={provider.is_healthy ? "default" : "destructive"}
                className="text-xs"
              >
                {provider.is_healthy ? (
                  <>
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Healthy
                  </>
                ) : (
                  <>
                    <XCircle className="w-3 h-3 mr-1" />
                    Unhealthy
                  </>
                )}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Success Rate */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Success Rate</span>
                <span className="font-medium text-foreground">{provider.success_rate.toFixed(1)}%</span>
              </div>
              <Progress 
                value={provider.success_rate} 
                className="h-2"
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{provider.successful_calls} successful</span>
                <span>{provider.failed_calls} failed</span>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-2 mb-1">
                  <Activity className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Total Calls</span>
                </div>
                <div className="text-lg font-semibold text-foreground">{provider.total_calls}</div>
              </div>

              <div className="p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-2 mb-1">
                  <Zap className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Avg Latency</span>
                </div>
                <div className="text-lg font-semibold text-foreground">{provider.avg_latency_ms.toFixed(0)}ms</div>
              </div>

              <div className="p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-2 mb-1">
                  <DollarSign className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Total Cost</span>
                </div>
                <div className="text-lg font-semibold text-primary">${provider.total_cost.toFixed(4)}</div>
              </div>

              <div className="p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-2 mb-1">
                  <Activity className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Tokens Used</span>
                </div>
                <div className="text-lg font-semibold text-foreground">{provider.total_tokens.toLocaleString()}</div>
              </div>
            </div>

            {/* Warnings */}
            {provider.consecutive_failures > 0 && (
              <div className="flex items-start gap-2 p-2 rounded bg-yellow-500/10 border border-yellow-500/20">
                <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                <div className="text-xs text-yellow-500">
                  {provider.consecutive_failures} consecutive failure{provider.consecutive_failures > 1 ? 's' : ''}.
                  {provider.consecutive_failures >= 3 && " Provider will be auto-disabled."}
                </div>
              </div>
            )}

            {/* Last Activity */}
            <div className="pt-2 border-t border-border/50 text-xs text-muted-foreground">
              {provider.last_success && (
                <div>Last success: {new Date(provider.last_success * 1000).toLocaleString()}</div>
              )}
              {provider.last_failure && (
                <div>Last failure: {new Date(provider.last_failure * 1000).toLocaleString()}</div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Call History Table */}
      <CallHistoryTable />
    </div>
  );
}
