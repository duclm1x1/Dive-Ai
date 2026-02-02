import { useEffect, useState } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  Zap, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRuntimeStore } from '@/stores/runtimeStore';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  trend?: {
    value: string;
    positive: boolean;
  };
  color?: 'primary' | 'success' | 'warning' | 'accent';
}

function StatCard({ title, value, subtitle, icon: Icon, trend, color = 'primary' }: StatCardProps) {
  const colorClasses = {
    primary: 'bg-gray-100 text-gray-600 border-gray-200',
    success: 'bg-green-100 text-green-600 border-green-200',
    warning: 'bg-orange-100 text-orange-600 border-orange-200',
    accent: 'bg-blue-100 text-blue-600 border-blue-200',
  };

  return (
    <div className="border border-gray-200 p-6 rounded-lg hover:shadow-md transition-shadow bg-white">
      <div className="flex items-start justify-between mb-4">
        <div className={cn(
          'p-3 rounded-xl border',
          colorClasses[color]
        )}>
          <Icon className="w-5 h-5" />
        </div>
        {trend && (
          <div className={cn(
            'flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full',
            trend.positive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          )}>
            <TrendingUp className={cn('w-3 h-3', !trend.positive && 'rotate-180')} />
            {trend.value}
          </div>
        )}
      </div>
      <div>
        <p className="text-xs text-gray-600 uppercase tracking-wider mb-1 font-medium">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
        {subtitle && (
          <p className="text-xs text-gray-500">{subtitle}</p>
        )}
      </div>
    </div>
  );
}

interface RecentRunProps {
  run: {
    id: string;
    type: string;
    status: 'success' | 'running' | 'failed';
    duration: string;
    timestamp: string;
  };
}

function RecentRun({ run }: RecentRunProps) {
  const statusConfig = {
    success: { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-500/10' },
    running: { icon: Zap, color: 'text-cyan-500', bg: 'bg-cyan-500/10' },
    failed: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-500/10' },
  };

  const config = statusConfig[run.status];
  const StatusIcon = config.icon;

  return (
    <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors group border border-gray-100">
      <div className="flex items-center gap-3 flex-1">
        <div className={cn('p-2 rounded-lg', config.bg)}>
          <StatusIcon className={cn('w-4 h-4', config.color)} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">{run.type}</p>
          <p className="text-xs text-gray-500">{run.timestamp}</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <p className="text-xs text-gray-500">Duration</p>
          <p className="text-sm font-medium text-gray-900">{run.duration}</p>
        </div>
        <ArrowRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
    </div>
  );
}

export function DashboardOverview() {
  const { runs, isConnected } = useRuntimeStore();
  const [healthData, setHealthData] = useState<any>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        // Try to fetch health data, but don't fail if server is not running
        const response = await fetch('http://localhost:8787/v1/providers/health');
        if (response.ok) {
          const data = await response.json();
          setHealthData(data);
        }
      } catch (error) {
        // Silently fail - server might not be running yet
        // This is expected behavior when monitor server is not started
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const totalRuns = runs.length;
  const completedRuns = runs.filter(r => r.status === 'COMPLETED').length;
  const successRate = totalRuns > 0 ? Math.round((completedRuns / totalRuns) * 100) : 0;
  const totalCost = healthData?.total_cost || 0;
  const totalCalls = healthData?.total_calls || 0;

  const recentRuns = runs.slice(0, 5).map(run => ({
    id: run.run_id,
    type: run.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    status: run.status === 'COMPLETED' ? 'success' as const : 
            run.status === 'RUNNING' ? 'running' as const : 
            'failed' as const,
    duration: run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : 'In progress',
    timestamp: new Date(run.start_time).toLocaleTimeString(),
  }));

  const activeProvider = healthData?.providers?.find((p: any) => p.success_rate > 0);

  return (
    <div className="h-full overflow-y-auto p-8 space-y-8 bg-white">
      {/* Hero Section */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Dive Monitor Dashboard</h1>
        <p className="text-gray-600">
          Real-time monitoring and analytics for your AI coding assistant
        </p>
      </div>

      {/* Connection Status Banner */}
      {!isConnected && (
        <div className="p-4 border border-yellow-200 rounded-lg bg-yellow-50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-yellow-100">
              <Sparkles className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-yellow-900">Waiting for DiveCoder</p>
              <p className="text-xs text-yellow-700">
                Start DiveCoder to see live monitoring data
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Runs"
          value={totalRuns}
          subtitle="All time"
          icon={Zap}
          color="primary"
        />
        <StatCard
          title="Success Rate"
          value={`${successRate}%`}
          subtitle={`${completedRuns} completed`}
          icon={CheckCircle2}
          color="success"
          trend={{ value: '+12%', positive: true }}
        />
        <StatCard
          title="Total Cost"
          value={`$${totalCost.toFixed(4)}`}
          subtitle={`${totalCalls} API calls`}
          icon={DollarSign}
          color="warning"
        />
        <StatCard
          title="Active Provider"
          value={activeProvider?.name || 'None'}
          subtitle={activeProvider?.model || 'Waiting...'}
          icon={Sparkles}
          color="accent"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="border border-gray-200 p-6 rounded-lg bg-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
            <Clock className="w-4 h-4 text-gray-400" />
          </div>
          <div className="space-y-2">
            {recentRuns.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <p>No runs yet</p>
                <p className="text-xs mt-2">Activity will appear when DiveCoder starts working</p>
              </div>
            ) : (
              recentRuns.map(run => (
                <RecentRun key={run.id} run={run} />
              ))
            )}
          </div>
        </div>

        {/* Provider Health */}
        <div className="border border-gray-200 p-6 rounded-lg bg-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Provider Health</h2>
            <Sparkles className="w-4 h-4 text-gray-400" />
          </div>
          <div className="space-y-3">
            {healthData?.providers?.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <p>No providers configured</p>
                <p className="text-xs mt-2">Configure LLM providers in Settings</p>
              </div>
            ) : (
              healthData?.providers?.map((provider: any) => (
                <div key={provider.name} className="p-3 rounded-lg bg-gray-50 border border-gray-100">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-900">{provider.name}</p>
                    <div className={cn(
                      'px-2 py-1 rounded-full text-2xs font-medium',
                      provider.success_rate >= 80 ? 'bg-green-100 text-green-700' :
                      provider.success_rate >= 50 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    )}>
                      {(provider.success_rate || 0).toFixed(0)}% Success
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <p className="text-gray-600">Calls</p>
                      <p className="font-medium text-gray-900">{provider.total_calls}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Latency</p>
                      <p className="font-medium text-gray-900">{(provider.avg_latency || 0).toFixed(1)}s</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Cost</p>
                      <p className="font-medium text-gray-900">${(provider.total_cost || 0).toFixed(4)}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 rounded-lg border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-all text-left group bg-white">
            <div className="p-2 bg-gray-100 group-hover:bg-gray-200 rounded-lg transition-colors w-fit mb-2">
              <Zap className="w-5 h-5 text-gray-600" />
            </div>
            <p className="text-sm font-semibold text-gray-900 mb-1">Start Monitoring</p>
            <p className="text-sm text-gray-600">Begin tracking DiveCoder activity</p>
          </button>
          <button className="p-4 rounded-lg border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-all text-left group bg-white">
            <div className="p-2 bg-gray-100 group-hover:bg-gray-200 rounded-lg transition-colors w-fit mb-2">
              <Sparkles className="w-5 h-5 text-gray-600" />
            </div>
            <p className="text-sm font-semibold text-gray-900 mb-1">Configure Providers</p>
            <p className="text-sm text-gray-600">Set up LLM API providers</p>
          </button>
          <button className="p-4 rounded-lg border-2 border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-all text-left group bg-white">
            <div className="p-2 bg-gray-100 group-hover:bg-gray-200 rounded-lg transition-colors w-fit mb-2">
              <TrendingUp className="w-5 h-5 text-gray-600" />
            </div>
            <p className="text-sm font-semibold text-gray-900 mb-1">View Analytics</p>
            <p className="text-sm text-gray-600">Detailed performance metrics</p>
          </button>
        </div>
      </div>
    </div>
  );
}
