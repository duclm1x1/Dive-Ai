import { useState, useEffect, useRef } from 'react';
import { 
  Brain, 
  Clock, 
  ChevronDown, 
  ChevronRight, 
  CheckCircle2, 
  Circle,
  Wrench,
  FileEdit,
  Package,
  Loader2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

interface ThinkingTask {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'done';
}

interface ThinkingEdit {
  id: string;
  type: 'edited' | 'created' | 'installed';
  name: string;
}

interface ThinkingBlock {
  id: string;
  content: string;
  timestamp: number;
  tools?: string[];
  tasks?: ThinkingTask[];
  edits?: ThinkingEdit[];
}

// Mock thinking stream data
const mockThinkingBlocks: ThinkingBlock[] = [
  {
    id: 'think_1',
    content: "I'll analyze the codebase to understand the current authentication implementation. Let me first explore the auth directory structure.",
    timestamp: Date.now() - 12000,
    tools: ['file_read', 'grep', 'semantic_search'],
  },
  {
    id: 'think_2',
    content: "Now I have a complete picture of the auth flow. The JWT validation occurs in middleware before reaching route handlers. Let me trace the token lifecycle.",
    timestamp: Date.now() - 8000,
    tasks: [
      { id: 't1', title: 'Analyze JWT middleware', status: 'done' },
      { id: 't2', title: 'Trace token validation flow', status: 'in_progress' },
      { id: 't3', title: 'Document security patterns', status: 'pending' },
    ],
  },
  {
    id: 'think_3',
    content: "Found the core authentication patterns. The handler uses RS256 algorithm for token signing. Now mapping evidence to claims.",
    timestamp: Date.now() - 3000,
    edits: [
      { id: 'e1', type: 'edited', name: 'src/auth/handler.ts' },
      { id: 'e2', type: 'created', name: 'src/auth/types.ts' },
      { id: 'e3', type: 'installed', name: 'jsonwebtoken@9.0.0' },
    ],
  },
];

interface ThinkingPanelProps {
  isLive?: boolean;
}

export function ThinkingPanel({ isLive = true }: ThinkingPanelProps) {
  const [blocks, setBlocks] = useState<ThinkingBlock[]>([]);
  const [currentText, setCurrentText] = useState('');
  const [thinkingDuration, setThinkingDuration] = useState(0);
  const [isThinking, setIsThinking] = useState(true);
  const [expandedTools, setExpandedTools] = useState(false);
  const [expandedEdits, setExpandedEdits] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const blockIndexRef = useRef(0);
  const charIndexRef = useRef(0);

  // Simulate thinking duration counter
  useEffect(() => {
    if (!isLive || !isThinking) return;
    
    const interval = setInterval(() => {
      setThinkingDuration(prev => prev + 1);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isLive, isThinking]);

  // Simulate streaming thinking text
  useEffect(() => {
    if (!isLive) {
      setBlocks(mockThinkingBlocks);
      setIsThinking(false);
      return;
    }

    const streamInterval = setInterval(() => {
      if (blockIndexRef.current >= mockThinkingBlocks.length) {
        setIsThinking(false);
        clearInterval(streamInterval);
        return;
      }

      const currentBlock = mockThinkingBlocks[blockIndexRef.current];
      const text = currentBlock.content;

      if (charIndexRef.current < text.length) {
        setCurrentText(text.slice(0, charIndexRef.current + 1));
        charIndexRef.current++;
      } else {
        // Complete current block and move to next
        setBlocks(prev => [...prev, currentBlock]);
        setCurrentText('');
        blockIndexRef.current++;
        charIndexRef.current = 0;
      }
    }, 30);

    return () => clearInterval(streamInterval);
  }, [isLive]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [blocks, currentText]);

  const allTools = blocks.flatMap(b => b.tools || []);
  const allEdits = blocks.flatMap(b => b.edits || []);
  const currentTasks = blocks.find(b => b.tasks)?.tasks || [];

  return (
    <div className="flex flex-col h-full bg-card/30 border-t border-border">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-center gap-3">
          <div className={cn(
            "p-2 rounded-lg",
            isThinking ? "bg-primary/20" : "bg-success/20"
          )}>
            {isThinking ? (
              <Brain className="w-4 h-4 text-primary animate-pulse" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-success" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              {isThinking ? 'Thinking' : 'Thought'} 
              <span className="text-muted-foreground">for {thinkingDuration}s</span>
            </h3>
          </div>
        </div>
        
        {isThinking && (
          <div className="flex items-center gap-2 text-2xs text-primary">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Processing...</span>
          </div>
        )}
      </div>

      {/* Thinking Content */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {/* Completed blocks */}
        {blocks.map((block, index) => (
          <div key={block.id} className="animate-fade-in">
            {/* Thinking text */}
            <p className="text-sm text-foreground/90 leading-relaxed">
              {block.content}
            </p>

            {/* Tools used */}
            {block.tools && block.tools.length > 0 && (
              <Collapsible open={expandedTools} onOpenChange={setExpandedTools}>
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-2 h-7 text-2xs text-muted-foreground hover:text-foreground gap-2"
                  >
                    <Wrench className="w-3 h-3" />
                    {block.tools.length} tools used
                    <span className="text-primary ml-2">Show all</span>
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-2 pl-4 space-y-1">
                  {block.tools.map((tool, i) => (
                    <div key={i} className="flex items-center gap-2 text-2xs text-muted-foreground">
                      <Circle className="w-1.5 h-1.5 fill-current" />
                      <span className="font-mono">{tool}</span>
                    </div>
                  ))}
                </CollapsibleContent>
              </Collapsible>
            )}

            {/* Tasks */}
            {block.tasks && block.tasks.length > 0 && (
              <div className="mt-3 p-3 rounded-lg bg-background border border-border">
                <span className="text-2xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Tasks
                </span>
                <div className="mt-2 space-y-2">
                  {block.tasks.map((task) => (
                    <div key={task.id} className="flex items-center gap-2">
                      {task.status === 'done' ? (
                        <CheckCircle2 className="w-4 h-4 text-success" />
                      ) : task.status === 'in_progress' ? (
                        <Loader2 className="w-4 h-4 text-primary animate-spin" />
                      ) : (
                        <Circle className="w-4 h-4 text-muted-foreground" />
                      )}
                      <span className={cn(
                        "text-sm",
                        task.status === 'done' ? "text-foreground" : "text-muted-foreground"
                      )}>
                        {task.title}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* File edits */}
            {block.edits && block.edits.length > 0 && (
              <Collapsible open={expandedEdits} onOpenChange={setExpandedEdits}>
                <div className="mt-3 space-y-1">
                  {block.edits.slice(0, expandedEdits ? undefined : 3).map((edit) => (
                    <div 
                      key={edit.id}
                      className="flex items-center gap-2 text-sm text-muted-foreground"
                    >
                      {edit.type === 'installed' ? (
                        <Package className="w-4 h-4 text-accent" />
                      ) : (
                        <FileEdit className="w-4 h-4 text-primary" />
                      )}
                      <span className={cn(
                        edit.type === 'installed' ? "text-accent" : "text-primary"
                      )}>
                        {edit.type === 'installed' ? 'Installed' : 
                         edit.type === 'created' ? 'Created' : 'Edited'}
                      </span>
                      <span className="font-mono text-foreground/80 truncate">
                        {edit.name}
                      </span>
                    </div>
                  ))}
                  
                  {block.edits.length > 3 && (
                    <CollapsibleTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 text-2xs text-muted-foreground"
                      >
                        {expandedEdits ? 'Hide' : `+${block.edits.length - 3} more`}
                      </Button>
                    </CollapsibleTrigger>
                  )}
                </div>
                <CollapsibleContent />
              </Collapsible>
            )}
          </div>
        ))}

        {/* Currently streaming text */}
        {isThinking && currentText && (
          <p className="text-sm text-foreground/90 leading-relaxed">
            {currentText}
            <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse" />
          </p>
        )}

        {/* Thinking indicator when no text yet */}
        {isThinking && !currentText && blocks.length === 0 && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="flex gap-1">
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span>Starting analysis...</span>
          </div>
        )}
      </div>
    </div>
  );
}
