import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Loader2, ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CallRecord {
  timestamp: number;
  provider: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
  latency_ms: number;
  success: boolean;
}

interface CallHistoryData {
  calls: CallRecord[];
  count: number;
}

type SortField = 'timestamp' | 'model' | 'latency_ms' | 'total_tokens' | 'cost';
type SortOrder = 'asc' | 'desc';

export function CallHistoryTable() {
  const [historyData, setHistoryData] = useState<CallHistoryData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const loadHistory = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787'}/v1/providers/history?limit=100`
      );
      if (response.ok) {
        const data = await response.json();
        setHistoryData(data);
      }
    } catch (error) {
      console.error("Failed to load call history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
    const interval = setInterval(loadHistory, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const sortedCalls = historyData?.calls ? [...historyData.calls].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];
    const modifier = sortOrder === 'asc' ? 1 : -1;
    return aValue > bValue ? modifier : -modifier;
  }) : [];

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const formatLatency = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
            <span className="ml-2 text-sm text-muted-foreground">Loading call history...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!historyData || historyData.calls.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Call History</CardTitle>
          <CardDescription>Detailed log of all LLM API calls</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-sm text-muted-foreground py-8">
            No call history available. Make some LLM calls to see them here.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Call History</CardTitle>
            <CardDescription>
              {historyData.count} total call{historyData.count !== 1 ? 's' : ''} • Showing most recent {sortedCalls.length}
            </CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={loadHistory}>
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border border-border/50 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/30">
                <TableHead className="w-[180px]">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-2 -ml-2"
                    onClick={() => handleSort('timestamp')}
                  >
                    THỜI GIAN
                    <ArrowUpDown className="ml-2 h-3 w-3" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-2 -ml-2"
                    onClick={() => handleSort('model')}
                  >
                    MODEL
                    <ArrowUpDown className="ml-2 h-3 w-3" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-2 -mr-2"
                    onClick={() => handleSort('latency_ms')}
                  >
                    THỜI GIAN XỬ LÝ
                    <ArrowUpDown className="ml-2 h-3 w-3" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">INPUT</TableHead>
                <TableHead className="text-right">OUTPUT</TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-2 -mr-2"
                    onClick={() => handleSort('cost')}
                  >
                    CHI PHÍ
                    <ArrowUpDown className="ml-2 h-3 w-3" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedCalls.map((call, index) => (
                <TableRow key={index} className="hover:bg-muted/20">
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {formatTimestamp(call.timestamp)}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      <span className="font-medium text-foreground">{call.model}</span>
                      <span className="text-xs text-muted-foreground">{call.provider}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <Badge variant="outline" className="font-mono">
                      {formatLatency(call.latency_ms)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {call.input_tokens}
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {call.output_tokens}
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm text-primary font-semibold">
                    ${call.cost.toFixed(6)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
