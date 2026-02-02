import { useState, useEffect } from 'react';
import { TrendingUp, Activity, DollarSign, Loader2 } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface PerformanceDataPoint {
  timestamp: number;
  provider: string;
  latency: number;
  cost: number;
  success: boolean;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }[];
}

const PROVIDER_COLORS: Record<string, { border: string; bg: string }> = {
  'V98 API': { border: 'rgb(59, 130, 246)', bg: 'rgba(59, 130, 246, 0.1)' },
  'AI Coding': { border: 'rgb(16, 185, 129)', bg: 'rgba(16, 185, 129, 0.1)' },
  'OpenAI': { border: 'rgb(139, 92, 246)', bg: 'rgba(139, 92, 246, 0.1)' },
  'Anthropic': { border: 'rgb(236, 72, 153)', bg: 'rgba(236, 72, 153, 0.1)' },
};

export function ProviderPerformanceCharts() {
  const [isLoading, setIsLoading] = useState(true);
  const [latencyData, setLatencyData] = useState<ChartData | null>(null);
  const [successRateData, setSuccessRateData] = useState<ChartData | null>(null);
  const [costData, setCostData] = useState<ChartData | null>(null);

  useEffect(() => {
    loadPerformanceData();
    const interval = setInterval(loadPerformanceData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadPerformanceData = async () => {
    try {
      const response = await fetch('http://localhost:8787/v1/providers/history?limit=100');
      if (!response.ok) {
        throw new Error('Failed to fetch history');
      }

      const data = await response.json();
      const calls: PerformanceDataPoint[] = data.calls || [];

      if (calls.length === 0) {
        setIsLoading(false);
        return;
      }

      // Group by time buckets (15 minute intervals)
      const bucketSize = 15 * 60 * 1000; // 15 minutes in ms
      const now = Date.now();
      const last24h = now - 24 * 60 * 60 * 1000;

      // Create time buckets for last 24 hours
      const buckets: Map<number, Map<string, { latencies: number[]; costs: number[]; successes: number; total: number }>> = new Map();

      calls.forEach((call) => {
        const timestamp = call.timestamp * 1000; // Convert to ms
        if (timestamp < last24h) return; // Skip old data

        const bucketTime = Math.floor(timestamp / bucketSize) * bucketSize;

        if (!buckets.has(bucketTime)) {
          buckets.set(bucketTime, new Map());
        }

        const bucket = buckets.get(bucketTime)!;
        if (!bucket.has(call.provider)) {
          bucket.set(call.provider, { latencies: [], costs: [], successes: 0, total: 0 });
        }

        const providerData = bucket.get(call.provider)!;
        providerData.latencies.push(call.latency || 0);
        providerData.costs.push(call.cost || 0);
        if (call.success) providerData.successes++;
        providerData.total++;
      });

      // Sort buckets by time
      const sortedBuckets = Array.from(buckets.entries()).sort((a, b) => a[0] - b[0]);

      // Get unique providers
      const providers = Array.from(
        new Set(calls.map((c) => c.provider))
      );

      // Generate labels (time)
      const labels = sortedBuckets.map(([time]) => {
        const date = new Date(time);
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      });

      // Generate latency chart data
      const latencyDatasets = providers.map((provider) => {
        const color = PROVIDER_COLORS[provider] || { border: 'rgb(156, 163, 175)', bg: 'rgba(156, 163, 175, 0.1)' };
        return {
          label: provider,
          data: sortedBuckets.map(([, bucket]) => {
            const data = bucket.get(provider);
            if (!data || data.latencies.length === 0) return 0;
            return data.latencies.reduce((a, b) => a + b, 0) / data.latencies.length;
          }),
          borderColor: color.border,
          backgroundColor: color.bg,
          tension: 0.4,
        };
      });

      setLatencyData({ labels, datasets: latencyDatasets });

      // Generate success rate chart data
      const successRateDatasets = providers.map((provider) => {
        const color = PROVIDER_COLORS[provider] || { border: 'rgb(156, 163, 175)', bg: 'rgba(156, 163, 175, 0.1)' };
        return {
          label: provider,
          data: sortedBuckets.map(([, bucket]) => {
            const data = bucket.get(provider);
            if (!data || data.total === 0) return 0;
            return (data.successes / data.total) * 100;
          }),
          borderColor: color.border,
          backgroundColor: color.bg,
          tension: 0.4,
        };
      });

      setSuccessRateData({ labels, datasets: successRateDatasets });

      // Generate cost chart data
      const costDatasets = providers.map((provider) => {
        const color = PROVIDER_COLORS[provider] || { border: 'rgb(156, 163, 175)', bg: 'rgba(156, 163, 175, 0.1)' };
        return {
          label: provider,
          data: sortedBuckets.map(([, bucket]) => {
            const data = bucket.get(provider);
            if (!data || data.costs.length === 0) return 0;
            return data.costs.reduce((a, b) => a + b, 0);
          }),
          borderColor: color.border,
          backgroundColor: color.bg,
          tension: 0.4,
        };
      });

      setCostData({ labels, datasets: costDatasets });
    } catch (error) {
      console.warn('Failed to load performance data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderSimpleChart = (data: ChartData | null, title: string, unit: string, icon: React.ReactNode) => {
    if (!data || data.labels.length === 0) {
      return (
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              {icon}
            </div>
            <h3 className="text-base font-semibold">{title}</h3>
          </div>
          <div className="text-center py-8 text-muted-foreground text-sm">
            No data available. Run some DiveCoder commands to see performance metrics.
          </div>
        </Card>
      );
    }

    // Find max value for scaling
    const maxValue = Math.max(
      ...data.datasets.flatMap((ds) => ds.data)
    );

    return (
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            {icon}
          </div>
          <h3 className="text-base font-semibold">{title}</h3>
        </div>

        {/* Simple ASCII-style chart */}
        <div className="space-y-4">
          {data.datasets.map((dataset) => (
            <div key={dataset.label} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: dataset.borderColor }}
                  />
                  <span className="text-sm font-medium">{dataset.label}</span>
                </div>
                <span className="text-xs text-muted-foreground">
                  Avg: {(dataset.data.reduce((a, b) => a + b, 0) / dataset.data.length).toFixed(2)} {unit}
                </span>
              </div>

              {/* Mini sparkline */}
              <div className="flex items-end gap-0.5 h-12">
                {dataset.data.slice(-20).map((value, i) => {
                  const height = maxValue > 0 ? (value / maxValue) * 100 : 0;
                  return (
                    <div
                      key={i}
                      className="flex-1 rounded-t transition-all"
                      style={{
                        height: `${Math.max(height, 2)}%`,
                        backgroundColor: dataset.borderColor,
                        opacity: 0.7,
                      }}
                      title={`${value.toFixed(2)} ${unit}`}
                    />
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-border">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Last 24 hours</span>
            <span>{data.labels.length} data points</span>
          </div>
        </div>
      </Card>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
          <TrendingUp className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-base font-semibold mb-1">Performance Trends</h2>
          <p className="text-sm text-muted-foreground">
            Real-time provider performance metrics over the past 24 hours
          </p>
        </div>
      </div>

      <div className="grid gap-6">
        {renderSimpleChart(
          latencyData,
          'Response Latency',
          'ms',
          <Activity className="w-5 h-5 text-primary" />
        )}

        {renderSimpleChart(
          successRateData,
          'Success Rate',
          '%',
          <TrendingUp className="w-5 h-5 text-primary" />
        )}

        {renderSimpleChart(
          costData,
          'Cost per Interval',
          '$',
          <DollarSign className="w-5 h-5 text-primary" />
        )}
      </div>
    </div>
  );
}
