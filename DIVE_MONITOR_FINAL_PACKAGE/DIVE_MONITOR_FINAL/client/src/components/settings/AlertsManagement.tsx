import { useState, useEffect } from 'react';
import { Bell, AlertTriangle, CheckCircle, XCircle, Settings, Loader2, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { safeFetch } from '@/lib/api-config';

interface AlertRule {
  id: string;
  name: string;
  enabled: boolean;
  condition_type: string;
  threshold: number;
  notification_channels: string[];
  cooldown_minutes: number;
}

interface Alert {
  id: string;
  timestamp: number;
  provider_name: string;
  condition: string;
  message: string;
  severity: string;
}

export function AlertsManagement() {
  const [isLoading, setIsLoading] = useState(true);
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [notificationConfig, setNotificationConfig] = useState<any>({});

  useEffect(() => {
    loadAlertData();
  }, []);

  const loadAlertData = async () => {
    const rulesResult = await safeFetch<any>('/v1/alerts/rules');
    
    if (!rulesResult.isBackendAvailable) {
      // Backend not available, use empty data
      setRules([]);
      setAlerts([]);
      setIsLoading(false);
      return;
    }
    
    if (rulesResult.data) {
      setRules(rulesResult.data.rules || []);
      setNotificationConfig(rulesResult.data.notification_config || {});
    }

    const alertsResult = await safeFetch<any>('/v1/alerts?limit=20');
    if (alertsResult.data) {
      setAlerts(alertsResult.data.alerts || []);
    }
    
    setIsLoading(false);
  };

  const toggleRule = async (ruleId: string, enabled: boolean) => {
    const updatedRules = rules.map((rule) =>
      rule.id === ruleId ? { ...rule, enabled } : rule
    );

    const result = await safeFetch<any>('/v1/alerts/rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rules: updatedRules, notification_config: notificationConfig }),
    });

    if (!result.isBackendAvailable) {
      toast.error('Backend server not available');
      return;
    }

    if (result.data) {
      setRules(updatedRules);
      toast.success(`Alert rule ${enabled ? 'enabled' : 'disabled'}`);
    } else {
      toast.error('Failed to update alert rule');
    }
  };

  const updateThreshold = async (ruleId: string, threshold: number) => {
    const updatedRules = rules.map((rule) =>
      rule.id === ruleId ? { ...rule, threshold } : rule
    );

    try {
      const response = await fetch('http://localhost:8787/v1/alerts/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rules: updatedRules, notification_config: notificationConfig }),
      });

      if (response.ok) {
        setRules(updatedRules);
        toast.success('Threshold updated');
      }
    } catch (error) {
      toast.error('Failed to update threshold');
    }
  };

  const checkAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8787/v1/alerts/check', {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        if (data.new_alerts > 0) {
          toast.info(`Generated ${data.new_alerts} new alerts`);
          loadAlertData();
        } else {
          toast.success('All providers healthy');
        }
      }
    } catch (error) {
      toast.error('Failed to check alerts');
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
      case 'critical':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default:
        return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
      case 'critical':
        return 'border-l-red-500 bg-red-50';
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50';
      default:
        return 'border-l-green-500 bg-green-50';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Show backend unavailable message
  if (rules.length === 0 && alerts.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Bell className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-base font-semibold mb-1">Provider Alerts</h2>
            <p className="text-sm text-muted-foreground">
              Configure alerts for provider health monitoring
            </p>
          </div>
        </div>
        <Card className="p-6">
          <div className="flex items-start gap-3 text-muted-foreground">
            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium mb-1">Backend Server Required</p>
              <p>The alerting system requires a backend server to function. This feature is available when running the monitor server locally.</p>
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
          <Bell className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold mb-1">Provider Alerts</h2>
              <p className="text-sm text-muted-foreground">
                Configure alerts for provider health monitoring
              </p>
            </div>
            <Button onClick={checkAlerts} variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Check Now
            </Button>
          </div>
        </div>
      </div>

      {/* Alert Rules */}
      <Card className="p-6">
        <h3 className="text-sm font-semibold mb-4">Alert Rules</h3>
        <div className="space-y-4">
          {rules.map((rule) => (
            <div
              key={rule.id}
              className="flex items-center justify-between p-4 border border-border rounded-lg"
            >
              <div className="flex items-center gap-4 flex-1">
                <Switch
                  checked={rule.enabled}
                  onCheckedChange={(checked) => toggleRule(rule.id, checked)}
                />
                <div className="flex-1">
                  <div className="font-medium text-sm">{rule.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {rule.condition_type} • Cooldown: {rule.cooldown_minutes}min
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Threshold:</span>
                  <Input
                    type="number"
                    value={rule.threshold}
                    onChange={(e) => {
                      const value = parseFloat(e.target.value);
                      if (!isNaN(value)) {
                        updateThreshold(rule.id, value);
                      }
                    }}
                    className="w-20 h-8 text-xs"
                  />
                </div>
                <div className="flex gap-1">
                  {rule.notification_channels.map((channel) => (
                    <span
                      key={channel}
                      className="px-2 py-1 text-xs rounded bg-primary/10 text-primary"
                    >
                      {channel}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Alerts */}
      <Card className="p-6">
        <h3 className="text-sm font-semibold mb-4">Recent Alerts</h3>
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm">
            No alerts yet. Alerts will appear here when provider health issues are detected.
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 border-l-4 rounded-lg ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start gap-3">
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm">{alert.provider_name}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(alert.timestamp * 1000).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{alert.message}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
