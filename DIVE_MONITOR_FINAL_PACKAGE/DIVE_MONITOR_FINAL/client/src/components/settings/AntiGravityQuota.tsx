import { useState, useEffect } from 'react';
import { Sparkles, RefreshCw, Loader2, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface AGModel {
  modelID: string;
  displayName: string;
  provider: string;
  remainingFraction: number;
  resetTime: string;
  isExhausted: boolean;
}

interface AGQuotaData {
  email: string;
  projectID: string;
  models: AGModel[];
  defaultModelID: string;
  fetchedAt: string;
  tier?: string;
}

export function AntiGravityQuota() {
  const [isLoading, setIsLoading] = useState(false);
  const [quotaData, setQuotaData] = useState<AGQuotaData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkQuota = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // In a real implementation, this would call a backend endpoint
      // that uses the AG-Quota library to fetch quota data
      // For now, show a message that this requires backend setup
      
      toast.info('Anti-Gravity quota checking requires backend setup');
      setError('Backend integration required');
      
      // Mock data for demonstration
      const mockData: AGQuotaData = {
        email: 'user@example.com',
        projectID: 'demo-project',
        tier: 'Pro',
        models: [
          {
            modelID: 'claude-sonnet-4-5',
            displayName: 'Claude 4 Sonnet',
            provider: 'claude',
            remainingFraction: 0.85,
            resetTime: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
            isExhausted: false,
          },
          {
            modelID: 'claude-opus-4',
            displayName: 'Claude 4 Opus',
            provider: 'claude',
            remainingFraction: 1.0,
            resetTime: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(),
            isExhausted: false,
          },
          {
            modelID: 'gemini-3-flash',
            displayName: 'Gemini 3 Flash',
            provider: 'gemini',
            remainingFraction: 0.0,
            resetTime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
            isExhausted: true,
          },
          {
            modelID: 'gemini-3-pro',
            displayName: 'Gemini 3 Pro',
            provider: 'gemini',
            remainingFraction: 0.5,
            resetTime: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(),
            isExhausted: false,
          },
        ],
        defaultModelID: 'claude-sonnet-4-5',
        fetchedAt: new Date().toISOString(),
      };

      // Uncomment to show mock data
      // setQuotaData(mockData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check quota');
      toast.error('Failed to check Anti-Gravity quota');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (model: AGModel) => {
    if (model.isExhausted) {
      return <XCircle className="w-4 h-4 text-red-500" />;
    }
    if (model.remainingFraction <= 0.1) {
      return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
    return <CheckCircle className="w-4 h-4 text-green-500" />;
  };

  const getStatusText = (model: AGModel) => {
    if (model.isExhausted) return 'EMPTY';
    if (model.remainingFraction <= 0.1) return 'LOW';
    return 'OK';
  };

  const getStatusColor = (model: AGModel) => {
    if (model.isExhausted) return 'text-red-600';
    if (model.remainingFraction <= 0.1) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatResetTime = (resetTime: string) => {
    const now = new Date();
    const reset = new Date(resetTime);
    const diff = reset.getTime() - now.getTime();
    
    if (diff <= 0) return 'Now';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
          <Sparkles className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold mb-1">Anti-Gravity Quota</h2>
              <p className="text-sm text-muted-foreground">
                Monitor your Claude Code AI model quota and usage
              </p>
            </div>
            <Button
              onClick={checkQuota}
              disabled={isLoading}
              variant="outline"
              size="sm"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Check Quota
            </Button>
          </div>
        </div>
      </div>

      {/* Setup Instructions */}
      <Card className="p-6 bg-muted/50">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
          <div className="text-sm space-y-2">
            <p className="font-medium">Backend Integration Required</p>
            <p className="text-muted-foreground">
              To use Anti-Gravity quota monitoring, you need to:
            </p>
            <ol className="list-decimal list-inside space-y-1 text-muted-foreground ml-2">
              <li>Install the AG-Quota CLI tool: <code className="px-1.5 py-0.5 rounded bg-background text-xs">go install github.com/gundamkid/anti-gravity-quota/cmd/ag-quota@latest</code></li>
              <li>Authenticate with Google: <code className="px-1.5 py-0.5 rounded bg-background text-xs">ag-quota login</code></li>
              <li>Integrate the backend API endpoint to fetch quota data</li>
            </ol>
            <p className="text-muted-foreground">
              Learn more: <a href="https://github.com/gundamkid/anti-gravity-quota" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">github.com/gundamkid/anti-gravity-quota</a>
            </p>
          </div>
        </div>
      </Card>

      {/* Quota Display */}
      {quotaData && (
        <Card className="p-6">
          <div className="space-y-4">
            {/* Account Info */}
            <div className="flex items-center justify-between pb-4 border-b border-border">
              <div>
                <div className="text-sm text-muted-foreground">Account</div>
                <div className="font-medium">{quotaData.email}</div>
              </div>
              {quotaData.tier && (
                <div className="px-3 py-1 rounded-lg bg-primary/10 text-primary text-sm font-medium">
                  {quotaData.tier}
                </div>
              )}
            </div>

            {/* Models Table */}
            <div className="space-y-3">
              <div className="text-sm font-semibold">Model Quotas</div>
              <div className="space-y-2">
                {quotaData.models.map((model) => (
                  <div
                    key={model.modelID}
                    className="flex items-center justify-between p-3 rounded-lg border border-border"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      {getStatusIcon(model)}
                      <div>
                        <div className="font-medium text-sm">{model.displayName}</div>
                        {model.modelID === quotaData.defaultModelID && (
                          <div className="text-xs text-primary">⭐ Default</div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <div className="text-sm font-medium">
                          {(model.remainingFraction * 100).toFixed(0)}%
                        </div>
                        <div className="text-xs text-muted-foreground">Remaining</div>
                      </div>

                      <div className="text-right">
                        <div className="text-sm font-medium">
                          {formatResetTime(model.resetTime)}
                        </div>
                        <div className="text-xs text-muted-foreground">Reset in</div>
                      </div>

                      <div className={`text-sm font-semibold ${getStatusColor(model)} min-w-[60px] text-right`}>
                        {getStatusText(model)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Fetched Time */}
            <div className="text-xs text-muted-foreground text-center pt-2">
              Last updated: {new Date(quotaData.fetchedAt).toLocaleString()}
            </div>
          </div>
        </Card>
      )}

      {/* Error Display */}
      {error && !quotaData && (
        <Card className="p-6">
          <div className="flex items-center gap-3 text-muted-foreground">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium mb-1">Unable to Check Quota</p>
              <p>{error}</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
