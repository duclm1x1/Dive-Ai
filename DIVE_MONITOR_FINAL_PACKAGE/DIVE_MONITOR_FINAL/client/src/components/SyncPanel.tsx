import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Zap,
  Activity,
  Settings,
  Copy,
  RefreshCw,
} from 'lucide-react';
import { useSyncStore } from '@/stores/syncStore';
import { useSyncClient } from '@/hooks/useSyncClient';
import { cn } from '@/lib/utils';

export const SyncPanel: React.FC = () => {
  const syncStore = useSyncStore();
  const [showDetails, setShowDetails] = useState(false);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const syncClient = useSyncClient({
    websocketUrl: syncStore.websocketUrl,
    clientName: 'Dive Monitor 2',
    autoConnect: true,
  });

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const handleRefresh = () => {
    syncClient.getState();
  };

  const handleControl = (action: string) => {
    syncClient.sendControl(action);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'bg-green-500/20 text-green-700 border-green-200';
      case 'connecting':
        return 'bg-yellow-500/20 text-yellow-700 border-yellow-200';
      case 'disconnected':
        return 'bg-red-500/20 text-red-700 border-red-200';
      default:
        return 'bg-gray-500/20 text-gray-700 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'connecting':
        return <Clock className="w-4 h-4 animate-spin" />;
      case 'disconnected':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      {/* Connection Status Card */}
      <Card className="border-l-4 border-l-cyan-500">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-500" />
              <CardTitle className="text-lg">Sync Status</CardTitle>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              className="h-8 w-8 p-0"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Connection Status */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Connection</span>
            <div
              className={cn(
                'flex items-center gap-2 px-3 py-1 rounded-full border',
                getStatusColor(syncStore.connectionStatus)
              )}
            >
              {getStatusIcon(syncStore.connectionStatus)}
              <span className="text-xs font-semibold capitalize">
                {syncStore.connectionStatus}
              </span>
            </div>
          </div>

          {/* Session Info */}
          {syncStore.sessionId && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">Session ID</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-xs"
                  onClick={() => handleCopy(syncStore.sessionId || '', 'Session ID')}
                >
                  <Copy className="w-3 h-3 mr-1" />
                  {copiedText === 'Session ID' ? 'Copied!' : 'Copy'}
                </Button>
              </div>
              <code className="block text-xs bg-gray-900 text-cyan-400 p-2 rounded font-mono break-all">
                {syncStore.sessionId}
              </code>
            </div>
          )}

          {/* Metrics Summary */}
          {syncStore.metrics && (
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-200">
              {syncStore.metrics.total_duration_ms && (
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-amber-500" />
                  <div>
                    <div className="text-xs text-gray-500">Duration</div>
                    <div className="text-sm font-semibold">
                      {(syncStore.metrics.total_duration_ms / 1000).toFixed(2)}s
                    </div>
                  </div>
                </div>
              )}

              {syncStore.metrics.token_usage && (
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-yellow-500" />
                  <div>
                    <div className="text-xs text-gray-500">Tokens</div>
                    <div className="text-sm font-semibold">
                      {syncStore.metrics.token_usage.input +
                        syncStore.metrics.token_usage.output}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Events and Details Tabs */}
      {syncStore.events.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Sync Events</CardTitle>
              <Badge variant="secondary">{syncStore.events.length}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="recent" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="recent">Recent</TabsTrigger>
                <TabsTrigger value="metrics">Metrics</TabsTrigger>
              </TabsList>

              <TabsContent value="recent" className="space-y-2">
                <ScrollArea className="h-64 w-full rounded-md border border-gray-200 p-2">
                  <div className="space-y-1">
                    {syncStore.events
                      .slice()
                      .reverse()
                      .slice(0, 20)
                      .map((event, idx) => (
                        <div
                          key={idx}
                          className="text-xs p-2 rounded bg-gray-50 border border-gray-100 hover:bg-gray-100 transition-colors cursor-pointer"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1">
                              <div className="font-mono font-semibold text-cyan-600">
                                {event.type}
                              </div>
                              <div className="text-gray-600 mt-1">
                                {event.explain && (
                                  <div className="italic">{event.explain}</div>
                                )}
                                {event.payload && Object.keys(event.payload).length > 0 && (
                                  <div className="text-gray-500 mt-1">
                                    {Object.entries(event.payload)
                                      .slice(0, 2)
                                      .map(([k, v]) => (
                                        <div key={k}>
                                          {k}: {String(v).substring(0, 30)}
                                        </div>
                                      ))}
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="text-gray-400 text-xs whitespace-nowrap">
                              {event.timestamp
                                ? new Date(event.timestamp * 1000).toLocaleTimeString()
                                : '-'}
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="metrics" className="space-y-2">
                {syncStore.metrics ? (
                  <div className="space-y-2 text-sm">
                    <div className="grid grid-cols-2 gap-2">
                      {syncStore.metrics.total_duration_ms && (
                        <div className="p-2 bg-gray-50 rounded border border-gray-100">
                          <div className="text-xs text-gray-500">Total Duration</div>
                          <div className="font-semibold">
                            {(syncStore.metrics.total_duration_ms / 1000).toFixed(2)}s
                          </div>
                        </div>
                      )}

                      {syncStore.metrics.tool_time_ms && (
                        <div className="p-2 bg-gray-50 rounded border border-gray-100">
                          <div className="text-xs text-gray-500">Tool Time</div>
                          <div className="font-semibold">
                            {(syncStore.metrics.tool_time_ms / 1000).toFixed(2)}s
                          </div>
                        </div>
                      )}

                      {syncStore.metrics.llm_time_ms && (
                        <div className="p-2 bg-gray-50 rounded border border-gray-100">
                          <div className="text-xs text-gray-500">LLM Time</div>
                          <div className="font-semibold">
                            {(syncStore.metrics.llm_time_ms / 1000).toFixed(2)}s
                          </div>
                        </div>
                      )}

                      {syncStore.metrics.token_usage && (
                        <div className="p-2 bg-gray-50 rounded border border-gray-100">
                          <div className="text-xs text-gray-500">Tokens Used</div>
                          <div className="font-semibold">
                            {syncStore.metrics.token_usage.input +
                              syncStore.metrics.token_usage.output}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-gray-500 text-center py-4">
                    No metrics available
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Control Panel */}
      {syncStore.isConnected && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Controls
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleControl('PAUSE')}
                className="text-xs"
              >
                Pause
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleControl('RESUME')}
                className="text-xs"
              >
                Resume
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleControl('CANCEL')}
                className="text-xs text-red-600 hover:text-red-700"
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Connection Info */}
      <Card className="bg-gray-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Connection Info</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">WebSocket URL:</span>
            <code className="text-gray-700 font-mono">{syncStore.websocketUrl}</code>
          </div>
          {syncStore.clientId && (
            <div className="flex justify-between">
              <span className="text-gray-600">Client ID:</span>
              <code className="text-gray-700 font-mono">{syncStore.clientId}</code>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-gray-600">Events Received:</span>
            <span className="font-semibold">{syncStore.lastEventCount}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SyncPanel;
