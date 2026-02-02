import { useState } from 'react';
import { 
  FileText, 
  FileCode,
  Link2,
  Sparkles,
  ChevronRight,
  ChevronDown,
  Download,
  ExternalLink,
  Shield
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { mockEvidence, mockClaims, mockEvidencePack } from '@/data/mockData';
import type { Evidence, Claim } from '@/types/observability';

const evidenceIcons: Record<string, React.ElementType> = {
  file: FileCode,
  snippet: FileText,
  url: ExternalLink,
  generated: Sparkles,
};

function EvidenceItem({ evidence, isExpanded, onToggle }: {
  evidence: Evidence;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const Icon = evidenceIcons[evidence.type] || FileText;
  
  return (
    <div className="glass-card overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/30 transition-colors"
      >
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 text-primary shrink-0">
          <Icon className="w-4 h-4" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium truncate">{evidence.source}</span>
            <span className="text-2xs px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
              {evidence.type}
            </span>
          </div>
          <div className="text-2xs text-muted-foreground font-mono">
            {evidence.id}
          </div>
        </div>
        
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 animate-scale-in">
          <div className="mb-2">
            <span className="text-2xs font-semibold text-muted-foreground uppercase">Metadata</span>
            <pre className="mt-1 text-2xs font-mono text-foreground/80">
              {JSON.stringify(evidence.metadata, null, 2)}
            </pre>
          </div>
          <div>
            <span className="text-2xs font-semibold text-muted-foreground uppercase">Content Preview</span>
            <p className="mt-1 text-xs text-foreground/80 line-clamp-3">{evidence.content}</p>
          </div>
        </div>
      )}
    </div>
  );
}

function ClaimRow({ claim, evidence }: { claim: Claim; evidence: Evidence[] }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const supportingEvidence = evidence.filter((e) => claim.supported_by.includes(e.id));
  
  const confidenceColor = 
    claim.confidence >= 0.9 ? 'bg-status-completed' :
    claim.confidence >= 0.7 ? 'bg-warning' : 'bg-status-failed';
  
  return (
    <div className="glass-card overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left p-4 hover:bg-muted/30 transition-colors"
      >
        <div className="flex items-start gap-3">
          <Shield className="w-4 h-4 text-primary mt-0.5 shrink-0" />
          
          <div className="flex-1 min-w-0">
            <p className="text-sm text-foreground leading-relaxed">{claim.claim_text}</p>
            
            <div className="flex items-center gap-4 mt-2">
              {/* Confidence bar */}
              <div className="flex items-center gap-2">
                <span className="text-2xs text-muted-foreground">Confidence</span>
                <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                  <div 
                    className={cn('h-full rounded-full', confidenceColor)}
                    style={{ width: `${claim.confidence * 100}%` }}
                  />
                </div>
                <span className="text-2xs font-mono text-muted-foreground">
                  {(claim.confidence * 100).toFixed(0)}%
                </span>
              </div>
              
              <span className="text-2xs text-muted-foreground">
                {supportingEvidence.length} evidence
              </span>
            </div>
          </div>
          
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0" />
          ) : (
            <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
          )}
        </div>
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-border animate-scale-in">
          <div className="pt-3">
            <span className="text-2xs font-semibold text-muted-foreground uppercase">
              Supporting Evidence
            </span>
            <div className="mt-2 space-y-2">
              {supportingEvidence.map((ev) => (
                <div 
                  key={ev.id}
                  className="flex items-center gap-2 p-2 rounded-lg bg-background border border-border"
                >
                  <Link2 className="w-3 h-3 text-primary shrink-0" />
                  <span className="text-xs font-mono truncate">{ev.source}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function EvidenceClaimsTab() {
  const [expandedEvidence, setExpandedEvidence] = useState<Set<string>>(new Set());

  const toggleEvidence = (id: string) => {
    setExpandedEvidence((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleExport = (type: 'evidence' | 'claims' | 'report') => {
    const data = type === 'evidence' 
      ? mockEvidencePack.evidence 
      : type === 'claims' 
      ? mockEvidencePack.claims 
      : mockEvidencePack;
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${type}_${mockEvidencePack.pack_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-full">
      {/* Left Panel - Evidence Tree */}
      <div className="w-96 shrink-0 border-r border-border overflow-y-auto bg-card/30 p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Evidence Pack
          </h2>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={() => handleExport('evidence')}
          >
            <Download className="w-3 h-3 mr-1" />
            Export
          </Button>
        </div>

        <div className="space-y-2">
          {mockEvidence.map((evidence) => (
            <EvidenceItem
              key={evidence.id}
              evidence={evidence}
              isExpanded={expandedEvidence.has(evidence.id)}
              onToggle={() => toggleEvidence(evidence.id)}
            />
          ))}
        </div>
      </div>

      {/* Main Panel - Claims Ledger */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Claims Ledger
          </h2>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs"
              onClick={() => handleExport('claims')}
            >
              <Download className="w-3 h-3 mr-1" />
              Claims JSON
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs border-primary/30 text-primary hover:bg-primary/10"
              onClick={() => handleExport('report')}
            >
              <Download className="w-3 h-3 mr-1" />
              Full Report
            </Button>
          </div>
        </div>

        <div className="space-y-3">
          {mockClaims.map((claim) => (
            <ClaimRow 
              key={claim.claim_id} 
              claim={claim} 
              evidence={mockEvidence}
            />
          ))}
        </div>

        {/* Report Preview */}
        {mockEvidencePack.report && (
          <div className="mt-6 p-4 glass-card">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
              Report Preview
            </h3>
            <div className="prose prose-sm prose-invert max-w-none">
              <pre className="text-xs text-foreground/80 whitespace-pre-wrap font-sans">
                {mockEvidencePack.report}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
