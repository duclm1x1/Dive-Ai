import { useState, useEffect } from 'react';
import { Zap, Clock, Activity, Loader2, Plus, Trash2, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { safeFetch } from '@/lib/api-config';

interface OptimizationRule {
  id: string;
  name: string;
  enabled: boolean;
  priority: number;
  rule_type: string;
  optimization_mode: string;
  is_active: boolean;
  time_ranges?: any[];
  conditions?: any[];
}

export function OptimizationRules() {
  const [isLoading, setIsLoading] = useState(true);
  const [rules, setRules] = useState<OptimizationRule[]>([]);
  const [activeMode, setActiveMode] = useState('balanced');

  useEffect(() => {
    loadRules();
    const interval = setInterval(loadRules, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadRules = async () => {
    const result = await safeFetch<any>('/v1/optimization/rules');
    
    if (result.data) {
      setRules(result.data.rules || []);
      setActiveMode(result.data.active_mode || 'balanced');
    } else {
      setRules([]);
    }
    
    setIsLoading(false);
  };

  const toggleRule = async (ruleId: string, enabled: boolean) => {
    const updatedRules = rules.map((rule) =>
      rule.id === ruleId ? { ...rule, enabled } : rule
    );

    const result = await safeFetch<any>('/v1/optimization/rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rules: updatedRules }),
    });

    if (!result.isBackendAvailable) {
      toast.error('Backend server not available');
      return;
    }

    if (result.data) {
      setRules(updatedRules);
      toast.success(`Rule ${enabled ? 'enabled' : 'disabled'}`);
      // Reload to get updated active mode
      setTimeout(loadRules, 500);
    } else {
      toast.error('Failed to update rule');
    }
  };

  const getRuleIcon = (ruleType: string) => {
    switch (ruleType) {
      case 'time_based':
        return <Clock className="w-4 h-4" />;
      case 'condition_based':
        return <Activity className="w-4 h-4" />;
      default:
        return <Zap className="w-4 h-4" />;
    }
  };

  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'fastest':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'cheapest':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-purple-600 bg-purple-50 border-purple-200';
    }
  };

  const getRuleDescription = (rule: OptimizationRule) => {
    if (rule.rule_type === 'time_based' && rule.time_ranges && rule.time_ranges.length > 0) {
      const tr = rule.time_ranges[0];
      const days = tr.days_of_week?.length > 0
        ? tr.days_of_week.map((d: number) => ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][d]).join(', ')
        : 'All days';
      return `${String(tr.start_hour).padStart(2, '0')}:${String(tr.start_minute).padStart(2, '0')} - ${String(tr.end_hour).padStart(2, '0')}:${String(tr.end_minute).padStart(2, '0')} • ${days}`;
    }

    if (rule.rule_type === 'condition_based' && rule.conditions && rule.conditions.length > 0) {
      const cond = rule.conditions[0];
      return `${cond.metric} ${cond.operator} ${cond.threshold}`;
    }

    return 'Always active';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Show backend unavailable message
  if (rules.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Zap className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-base font-semibold mb-1">Custom Optimization Rules</h2>
            <p className="text-sm text-muted-foreground">
              Define time-based and condition-based rules for automatic provider optimization
            </p>
          </div>
        </div>
        <Card className="p-6">
          <div className="flex items-start gap-3 text-muted-foreground">
            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium mb-1">Backend Server Required</p>
              <p>Custom optimization rules require a backend server to function. This feature is available when running the monitor server locally.</p>
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
          <Zap className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold mb-1">Custom Optimization Rules</h2>
              <p className="text-sm text-muted-foreground">
                Define time-based and condition-based rules for automatic provider optimization
              </p>
            </div>
            <div className={`px-4 py-2 rounded-lg border ${getModeColor(activeMode)}`}>
              <div className="text-xs font-medium">Active Mode</div>
              <div className="text-sm font-bold capitalize">{activeMode}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Rules List */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold">Rules (Priority Order)</h3>
          <Button size="sm" variant="outline" disabled>
            <Plus className="w-4 h-4 mr-2" />
            Add Rule
          </Button>
        </div>

        <div className="space-y-3">
          {rules.map((rule) => (
            <div
              key={rule.id}
              className={`p-4 border rounded-lg transition-all ${
                rule.is_active
                  ? 'border-primary bg-primary/5 shadow-sm'
                  : 'border-border'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="flex items-center gap-3 flex-1">
                  <Switch
                    checked={rule.enabled}
                    onCheckedChange={(checked) => toggleRule(rule.id, checked)}
                  />

                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-6 h-6 rounded bg-muted flex items-center justify-center">
                        {getRuleIcon(rule.rule_type)}
                      </div>
                      <span className="font-medium text-sm">{rule.name}</span>
                      {rule.is_active && (
                        <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700 font-medium">
                          Active
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground ml-8">
                      {getRuleDescription(rule)}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">Priority</div>
                    <div className="text-sm font-medium">{rule.priority}</div>
                  </div>
                  <div className={`px-3 py-1.5 rounded-lg text-xs font-medium border ${getModeColor(rule.optimization_mode)}`}>
                    {rule.optimization_mode}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Info Card */}
      <Card className="p-4 bg-muted/50">
        <div className="text-sm space-y-2">
          <p className="font-medium">How it works:</p>
          <ul className="space-y-1 text-muted-foreground text-xs">
            <li>• Rules are evaluated in priority order (lower number = higher priority)</li>
            <li>• The first active rule determines the optimization mode</li>
            <li>• Time-based rules activate during specified time ranges</li>
            <li>• Condition-based rules activate when metrics meet thresholds</li>
            <li>• Disabled rules are skipped during evaluation</li>
          </ul>
        </div>
      </Card>
    </div>
  );
}
