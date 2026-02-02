import { useState, useEffect } from 'react';
import { Download, FileText, FileSpreadsheet, Loader2, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { safeFetch, buildApiUrl } from '@/lib/api-config';

interface ProviderStat {
  provider_name: string;
  total_calls: number;
  success_rate: number;
  avg_latency_ms: number;
  total_cost: number;
  avg_cost_per_call: number;
}

export function PerformanceExport() {
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<ProviderStat[]>([]);
  const [selectedDays, setSelectedDays] = useState(30);
  const [includeHistory, setIncludeHistory] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    loadStats();
  }, [selectedDays]);

  const loadStats = async () => {
    const result = await safeFetch<any>(`/v1/export/stats?days=${selectedDays}`);
    
    if (result.data) {
      setStats(result.data.stats || []);
    } else {
      setStats([]);
    }
    
    setIsLoading(false);
  };

  const exportCSV = async () => {
    const url = buildApiUrl(`/v1/export/csv?days=${selectedDays}&include_history=${includeHistory}`);
    
    if (!url) {
      toast.error('Backend server not available');
      return;
    }
    
    setIsExporting(true);
    try {
      const response = await fetch(url);

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `dive_monitor_performance_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);

        toast.success('CSV report downloaded');
      } else {
        toast.error('Failed to export CSV');
      }
    } catch (error) {
      toast.error('Failed to export CSV');
    } finally {
      setIsExporting(false);
    }
  };

  const exportPDF = async () => {
    setIsExporting(true);
    try {
      const url = `http://localhost:8787/v1/export/pdf?days=${selectedDays}`;
      const response = await fetch(url);

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `dive_monitor_performance_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);

        toast.success('PDF report downloaded');
      } else {
        toast.error('Failed to export PDF');
      }
    } catch (error) {
      toast.error('Failed to export PDF');
    } finally {
      setIsExporting(false);
    }
  };

  const totalCalls = stats.reduce((sum, s) => sum + s.total_calls, 0);
  const totalCost = stats.reduce((sum, s) => sum + s.total_cost, 0);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Show backend unavailable message
  if (stats.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Download className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-base font-semibold mb-1">Export Performance Reports</h2>
            <p className="text-sm text-muted-foreground">
              Download detailed performance data for analysis and cost tracking
            </p>
          </div>
        </div>
        <Card className="p-6">
          <div className="flex items-start gap-3 text-muted-foreground">
            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium mb-1">Backend Server Required</p>
              <p>Performance report export requires a backend server to function. This feature is available when running the monitor server locally.</p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
          <Download className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-base font-semibold mb-1">Export Performance Reports</h2>
          <p className="text-sm text-muted-foreground">
            Download detailed performance data for analysis and cost tracking
          </p>
        </div>
      </div>

      {/* Export Options */}
      <Card className="p-6">
        <h3 className="text-sm font-semibold mb-4">Export Options</h3>

        <div className="space-y-4">
          {/* Time Range */}
          <div>
            <label className="text-sm font-medium mb-2 block">Time Range</label>
            <div className="flex gap-2">
              {[7, 30, 90].map((days) => (
                <Button
                  key={days}
                  variant={selectedDays === days ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedDays(days)}
                >
                  Last {days} days
                </Button>
              ))}
            </div>
          </div>

          {/* Include History */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="includeHistory"
              checked={includeHistory}
              onChange={(e) => setIncludeHistory(e.target.checked)}
              className="w-4 h-4 rounded border-border"
            />
            <label htmlFor="includeHistory" className="text-sm">
              Include detailed call history (CSV only)
            </label>
          </div>

          {/* Export Buttons */}
          <div className="flex gap-3 pt-2">
            <Button
              onClick={exportCSV}
              disabled={isExporting}
              className="flex-1"
            >
              {isExporting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <FileSpreadsheet className="w-4 h-4 mr-2" />
              )}
              Export CSV
            </Button>
            <Button
              onClick={exportPDF}
              disabled={isExporting}
              variant="outline"
              className="flex-1"
            >
              {isExporting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <FileText className="w-4 h-4 mr-2" />
              )}
              Export PDF
            </Button>
          </div>
        </div>
      </Card>

      {/* Preview */}
      <Card className="p-6">
        <h3 className="text-sm font-semibold mb-4">Preview (Last {selectedDays} days)</h3>

        {stats.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No data available for the selected time range
          </div>
        ) : (
          <>
            {/* Summary */}
            <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-muted/50 rounded-lg">
              <div>
                <div className="text-xs text-muted-foreground mb-1">Total API Calls</div>
                <div className="text-2xl font-bold">{totalCalls.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Total Cost</div>
                <div className="text-2xl font-bold">${totalCost.toFixed(2)}</div>
              </div>
            </div>

            {/* Provider Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-2 font-medium">Provider</th>
                    <th className="text-right py-2 font-medium">Calls</th>
                    <th className="text-right py-2 font-medium">Success Rate</th>
                    <th className="text-right py-2 font-medium">Avg Latency</th>
                    <th className="text-right py-2 font-medium">Total Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.map((stat) => (
                    <tr key={stat.provider_name} className="border-b border-border">
                      <td className="py-3">{stat.provider_name}</td>
                      <td className="text-right">{stat.total_calls}</td>
                      <td className="text-right">{stat.success_rate.toFixed(1)}%</td>
                      <td className="text-right">{stat.avg_latency_ms.toFixed(0)}ms</td>
                      <td className="text-right">${stat.total_cost.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
