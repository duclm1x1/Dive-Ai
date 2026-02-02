import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Zap, DollarSign, Clock } from "lucide-react";
import { toast } from "sonner";

interface SpeedTestResult {
  provider: string;
  model: string;
  response: string;
  time: number;
  tokens: { input: number; output: number; total: number };
  cost: number;
  success: boolean;
  error?: string;
}

export function ProviderSpeedTest() {
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState<SpeedTestResult[]>([]);
  const [fastest, setFastest] = useState<string | null>(null);
  const [cheapest, setCheapest] = useState<string | null>(null);

  const runSpeedTest = async () => {
    setTesting(true);
    setResults([]);
    
    try {
      const response = await fetch(
        `${import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787'}/v1/providers/speed-test`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'Hello from DiveCoder' })
        }
      );
      
      if (!response.ok) {
        throw new Error('Speed test failed');
      }
      
      const data = await response.json();
      
      if (data.success && data.benchmarks) {
        const benchmarkData = data.benchmarks;
        const testResults: SpeedTestResult[] = [];
        
        // Parse results from benchmarks
        for (const [provider, stats] of Object.entries(benchmarkData)) {
          if (stats && typeof stats === 'object') {
            const providerStats = stats as any;
            testResults.push({
              provider: provider,
              model: providerStats.model || 'unknown',
              response: providerStats.last_response || '',
              time: providerStats.avg_latency || 0,
              tokens: {
                input: providerStats.total_input_tokens || 0,
                output: providerStats.total_output_tokens || 0,
                total: providerStats.total_tokens || 0
              },
              cost: providerStats.total_cost || 0,
              success: providerStats.success_rate > 0
            });
          }
        }
        
        // Sort by speed
        testResults.sort((a, b) => a.time - b.time);
        setResults(testResults);
        
        // Find fastest and cheapest
        if (testResults.length > 0) {
          setFastest(testResults[0].provider);
          const cheapestProvider = [...testResults].sort((a, b) => a.cost - b.cost)[0];
          setCheapest(cheapestProvider.provider);
        }
        
        toast.success(`Speed test complete! Tested ${testResults.length} providers`);
      } else {
        toast.error(data.error || 'Speed test failed');
      }
    } catch (error) {
      console.error('Speed test error:', error);
      toast.error('Failed to run speed test');
    } finally {
      setTesting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Provider Speed Test</CardTitle>
        <CardDescription>
          Compare response time and cost across all configured providers
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button 
          onClick={runSpeedTest} 
          disabled={testing}
          className="w-full"
        >
          {testing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Testing providers...
            </>
          ) : (
            <>
              <Zap className="mr-2 h-4 w-4" />
              Run Speed Test
            </>
          )}
        </Button>

        {results.length > 0 && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Card className="border-green-500/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Zap className="h-4 w-4 text-green-500" />
                    Fastest
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{fastest}</div>
                  <div className="text-sm text-muted-foreground">
                    {results.find(r => r.provider === fastest)?.time.toFixed(2)}s
                  </div>
                </CardContent>
              </Card>

              <Card className="border-blue-500/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-blue-500" />
                    Cheapest
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{cheapest}</div>
                  <div className="text-sm text-muted-foreground">
                    ${results.find(r => r.provider === cheapest)?.cost.toFixed(6)}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-2">
              <h4 className="text-sm font-medium">Detailed Results</h4>
              {results.map((result, index) => (
                <Card key={index} className={result.provider === fastest ? 'border-green-500/30' : ''}>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <div className="font-medium">{result.provider}</div>
                        <div className="text-sm text-muted-foreground">{result.model}</div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-1 text-sm">
                          <Clock className="h-3 w-3" />
                          {result.time.toFixed(2)}s
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <DollarSign className="h-3 w-3" />
                          ${result.cost.toFixed(6)}
                        </div>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Tokens: {result.tokens.input} in / {result.tokens.output} out
                    </div>
                    {result.response && (
                      <div className="mt-2 p-2 bg-muted/50 rounded text-xs">
                        {result.response.substring(0, 100)}...
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
