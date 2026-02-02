import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface DemoModeProps {
  onRetry: () => void;
}

export function DemoMode({ onRetry }: DemoModeProps) {
  return (
    <div className="container py-12">
      <Alert className="border-warning/50 bg-warning/10">
        <AlertCircle className="h-5 w-5 text-warning" />
        <AlertTitle className="text-lg font-semibold mb-2">
          Monitor Server Unavailable
        </AlertTitle>
        <AlertDescription className="space-y-4">
          <p className="text-sm text-muted-foreground">
            The Dive Monitor server is not running or not accessible. This UI requires a running monitor server to display real-time events.
          </p>
          
          <div className="bg-card p-4 rounded border border-border">
            <p className="text-sm font-semibold mb-2">To start the monitor server:</p>
            <pre className="text-xs font-mono bg-muted/30 p-3 rounded overflow-x-auto">
              {`# Start monitor server
python3 /home/ubuntu/dive_monitor_server.py

# Or use the complete startup script
bash /home/ubuntu/start_dive_monitor.sh`}
            </pre>
          </div>

          <div className="bg-card p-4 rounded border border-border">
            <p className="text-sm font-semibold mb-2">Expected server URL:</p>
            <code className="text-xs font-mono text-primary">
              {import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787'}
            </code>
          </div>

          <div className="flex gap-3">
            <Button onClick={onRetry} variant="default" size="sm">
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry Connection
            </Button>
            <Button 
              onClick={() => window.open('/home/ubuntu/DIVE_MONITOR_GUIDE.md', '_blank')}
              variant="outline" 
              size="sm"
            >
              View Setup Guide
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    </div>
  );
}
