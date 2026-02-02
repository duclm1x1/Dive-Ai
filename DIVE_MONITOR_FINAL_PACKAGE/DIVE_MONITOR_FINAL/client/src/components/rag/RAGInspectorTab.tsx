import { useState } from 'react';
import { 
  Search, 
  ArrowRight, 
  ChevronDown, 
  ChevronRight,
  FileText,
  Database,
  Network,
  Layers
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRuntimeStore } from '@/stores/runtimeStore';
import type { RAGChunk } from '@/types/observability';

const methodIcons: Record<string, React.ElementType> = {
  bm25: Search,
  graphrag: Network,
  raptor: Layers,
};

const methodColors: Record<string, string> = {
  bm25: 'text-primary',
  graphrag: 'text-accent',
  raptor: 'text-warning',
};

function ChunkCard({ chunk, isExpanded, onToggle }: { 
  chunk: RAGChunk; 
  isExpanded: boolean; 
  onToggle: () => void;
}) {
  const MethodIcon = methodIcons[chunk.retrieval_method] || Database;
  
  return (
    <div className="glass-card overflow-hidden animate-fade-up">
      <button
        onClick={onToggle}
        className="w-full flex items-start gap-3 p-3 text-left hover:bg-muted/30 transition-colors"
      >
        {/* Rank Badge */}
        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold shrink-0">
          {chunk.rank}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <div className="flex items-center gap-2">
              <FileText className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-sm font-medium truncate">{chunk.source_file}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xs font-mono text-muted-foreground">
                {(chunk.score * 100).toFixed(0)}%
              </span>
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-muted-foreground" />
              ) : (
                <ChevronRight className="w-4 h-4 text-muted-foreground" />
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-3 text-2xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <MethodIcon className={cn('w-3 h-3', methodColors[chunk.retrieval_method])} />
              {chunk.retrieval_method.toUpperCase()}
            </span>
            <span className="truncate">{chunk.section}</span>
          </div>
        </div>
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 animate-scale-in">
          <div className="mb-3">
            <span className="text-2xs font-semibold text-muted-foreground uppercase">
              Reason Selected
            </span>
            <p className="text-xs text-foreground/80 mt-1">{chunk.reason_selected}</p>
          </div>
          
          <div>
            <span className="text-2xs font-semibold text-muted-foreground uppercase">
              Content
            </span>
            <pre className="mt-1 p-2 rounded bg-background text-2xs font-mono text-foreground/80 overflow-x-auto whitespace-pre-wrap">
              {chunk.content}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export function RAGInspectorTab() {
  const { ragQuery, ragChunks } = useRuntimeStore();
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set());

  const toggleChunk = (id: string) => {
    setExpandedChunks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Calculate context meter
  const totalChars = ragChunks.reduce((sum, c) => sum + c.content.length, 0);
  const maxChars = 128000;
  const usagePercent = (totalChars / maxChars) * 100;

  return (
    <div className="flex h-full">
      {/* Left Panel - Query Evolution */}
      <div className="w-80 shrink-0 border-r border-border overflow-y-auto bg-card/30 p-4">
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">
          Query Evolution
        </h2>

        {/* Original Query */}
        <div className="mb-4">
          <span className="text-2xs text-muted-foreground">Original Query</span>
          <div className="mt-1 p-3 rounded-lg bg-background border border-border">
            <p className="text-sm text-foreground">{ragQuery?.original || 'No query yet'}</p>
          </div>
        </div>

        {/* Enhanced Queries */}
        <div className="mb-4">
          <span className="text-2xs text-muted-foreground">Enhanced Queries</span>
          <div className="mt-1 space-y-2">
            {(ragQuery?.enhanced || []).map((query, index) => (
              <div 
                key={index}
                className="flex items-start gap-2 p-2 rounded-lg bg-primary/5 border border-primary/20"
              >
                <ArrowRight className="w-3 h-3 text-primary mt-0.5 shrink-0" />
                <p className="text-xs text-foreground/80">{query}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Step-Back Query */}
        {ragQuery?.step_back && (
          <div>
            <span className="text-2xs text-muted-foreground">Step-Back Query</span>
            <div className="mt-1 p-3 rounded-lg bg-accent/5 border border-accent/20">
              <p className="text-sm text-foreground/80">{ragQuery.step_back}</p>
            </div>
          </div>
        )}

        {/* Context Meter */}
        <div className="mt-6 p-4 glass-card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xs font-semibold text-muted-foreground uppercase">
              Context Usage
            </span>
            <span className="text-2xs text-muted-foreground">
              {(totalChars / 1000).toFixed(1)}k / {(maxChars / 1000).toFixed(0)}k
            </span>
          </div>
          <div className="h-2 rounded-full overflow-hidden bg-muted">
            <div 
              className={cn(
                'h-full rounded-full transition-all',
                usagePercent > 80 ? 'bg-destructive' : 
                usagePercent > 50 ? 'bg-warning' : 'bg-primary'
              )}
              style={{ width: `${usagePercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main Panel - Retrieval Results */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Retrieval Breakdown
          </h2>
          <div className="flex items-center gap-3 text-2xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Search className="w-3 h-3 text-primary" />
              BM25
            </span>
            <span className="flex items-center gap-1">
              <Network className="w-3 h-3 text-accent" />
              GraphRAG
            </span>
            <span className="flex items-center gap-1">
              <Layers className="w-3 h-3 text-warning" />
              RAPTOR
            </span>
          </div>
        </div>

        <div className="space-y-3">
          {ragChunks.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <p>No RAG retrieval results yet</p>
              <p className="text-xs mt-2">Results will appear when DiveCoder performs RAG queries</p>
            </div>
          ) : (
            ragChunks.map((chunk) => (
              <ChunkCard
                key={chunk.id}
                chunk={chunk}
                isExpanded={expandedChunks.has(chunk.id)}
                onToggle={() => toggleChunk(chunk.id)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
