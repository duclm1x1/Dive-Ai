import { useState } from 'react';
import { Bot, Plus, Power, PowerOff, Trash2, Cpu } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { useAgents, useUpdateAgent, useDeleteAgent } from '../hooks/useAgents';
import { useRealtimeAgents } from '../hooks/useRealtime';
import { CreateAgentModal } from '../components/agents/CreateAgentModal';
import { EmptyState } from '../components/ui/EmptyState';
import { cn, formatRelativeTime } from '../lib/utils';

export function AgentsPage() {
  const { isGuest } = useAuth();
  const { currentWorkspace } = useWorkspace();
  const { data: agents, isLoading } = useAgents(isGuest ? undefined : currentWorkspace?.id);
  const updateAgent = useUpdateAgent();
  const deleteAgent = useDeleteAgent();
  const [showCreate, setShowCreate] = useState(false);

  useRealtimeAgents(isGuest ? undefined : currentWorkspace?.id);

  const handleToggle = (agent: { id: string; status: string }) => {
    if (!currentWorkspace) return;
    updateAgent.mutate({
      id: agent.id,
      status: agent.status === 'active' ? 'inactive' : 'active',
      workspaceId: currentWorkspace.id,
    });
  };

  const handleDelete = (agentId: string) => {
    if (!currentWorkspace) return;
    deleteAgent.mutate({ id: agentId, workspaceId: currentWorkspace.id });
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 max-w-5xl mx-auto animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-white">Agents</h1>
            <p className="text-xs text-surface-500 mt-0.5 font-mono">Configure and manage AI agents</p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-all duration-200 active:scale-[0.98]"
          >
            <Plus size={14} />
            New Agent
          </button>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-surface-900 border border-surface-800 rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-surface-800 rounded w-1/3 mb-3" />
                <div className="h-3 bg-surface-800 rounded w-2/3 mb-4" />
                <div className="h-3 bg-surface-800 rounded w-1/4" />
              </div>
            ))}
          </div>
        ) : (agents ?? []).length === 0 ? (
          <EmptyState
            icon={Bot}
            title="No agents yet"
            description="Create AI agents to automate tasks, answer questions, and assist your team."
            action={
              <button
                onClick={() => setShowCreate(true)}
                className="flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-all duration-200"
              >
                <Plus size={14} />
                Create First Agent
              </button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(agents ?? []).map((agent) => (
              <div key={agent.id} className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden hover:border-surface-700 transition-all duration-200 group">
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-9 w-9 rounded-lg flex items-center justify-center',
                        agent.status === 'active'
                          ? 'bg-emerald-600/15 border border-emerald-600/25'
                          : 'bg-surface-800 border border-surface-700'
                      )}>
                        <Cpu size={16} className={agent.status === 'active' ? 'text-emerald-400' : 'text-surface-500'} />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-white">{agent.name}</h3>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="relative flex h-1.5 w-1.5">
                            {agent.status === 'active' && (
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-50" />
                            )}
                            <span className={cn(
                              'relative inline-flex rounded-full h-1.5 w-1.5',
                              agent.status === 'active' ? 'bg-emerald-400' :
                              agent.status === 'error' ? 'bg-rose-400' : 'bg-surface-500'
                            )} />
                          </span>
                          <span className="text-[10px] text-surface-500 capitalize">{agent.status}</span>
                          <span className="text-[10px] text-surface-600 font-mono">{agent.model}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {agent.description && (
                    <p className="text-xs text-surface-400 mb-3 line-clamp-2 ml-12">{agent.description}</p>
                  )}
                </div>

                <div className="flex items-center justify-between px-4 py-2.5 border-t border-surface-800 bg-surface-900/50">
                  <span className="text-[10px] text-surface-600 font-mono">{formatRelativeTime(agent.updated_at)}</span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleToggle(agent)}
                      className={cn(
                        'p-1.5 rounded-md transition-colors',
                        agent.status === 'active'
                          ? 'text-emerald-400 hover:bg-emerald-500/10'
                          : 'text-surface-500 hover:bg-surface-800'
                      )}
                      title={agent.status === 'active' ? 'Deactivate' : 'Activate'}
                    >
                      {agent.status === 'active' ? <Power size={14} /> : <PowerOff size={14} />}
                    </button>
                    <button
                      onClick={() => handleDelete(agent.id)}
                      className="p-1.5 rounded-md text-surface-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <CreateAgentModal open={showCreate} onClose={() => setShowCreate(false)} />
      </div>
    </div>
  );
}
