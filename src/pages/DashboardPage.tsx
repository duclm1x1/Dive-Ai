import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Bot,
  Plus,
  ArrowRight,
  Activity,
  Zap,
  Clock,
  Terminal,
  Settings,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Key,
  Download,
  Code,
  Copy,
  ExternalLink,
  Monitor,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { useConversations, useCreateConversation } from '../hooks/useConversations';
import { useAgents } from '../hooks/useAgents';
import { useRealtimeConversations, useRealtimeAgents } from '../hooks/useRealtime';
import { formatRelativeTime, truncate } from '../lib/utils';
import {
  getLlmConfig,
  getLatencyInfo,
  getStoredModels,
  getProviderLabel,
  fetchModelsFromApi,
  setStoredModels,
  setLatencyInfo,
  type LlmConfig,
  type LatencyInfo,
  type ModelInfo,
} from '../lib/llmConfig';
import { Spinner } from '../components/ui/Spinner';

function MetricCard({ icon: Icon, label, value, sub, accentClass }: {
  icon: typeof Activity;
  label: string;
  value: string | number;
  sub?: string;
  accentClass: string;
}) {
  return (
    <div className="bg-surface-900 border border-surface-800 rounded-lg p-4 hover:border-surface-700 transition-all duration-200 group">
      <div className="flex items-center gap-2 mb-3">
        <div className={`h-7 w-7 rounded-md flex items-center justify-center ${accentClass}`}>
          <Icon size={14} className="text-white" />
        </div>
        <span className="text-[11px] text-surface-500 uppercase tracking-wider font-medium">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white font-mono">{value}</p>
      {sub && <p className="text-[11px] text-surface-500 mt-1">{sub}</p>}
    </div>
  );
}

function StatusDot({ status }: { status: string }) {
  const color = status === 'active' ? 'bg-emerald-400' : status === 'error' ? 'bg-rose-400' : 'bg-surface-500';
  return (
    <span className="relative flex h-2 w-2">
      {status === 'active' && (
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${color} opacity-50`} />
      )}
      <span className={`relative inline-flex rounded-full h-2 w-2 ${color}`} />
    </span>
  );
}

function CliSetupCard() {
  const [copied, setCopied] = useState(false);

  const copyCommand = (command: string) => {
    navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-surface-800">
        <div className="flex items-center gap-2">
          <Terminal size={14} className="text-cyan-400" />
          <h2 className="text-sm font-semibold text-white">CLI Access</h2>
        </div>
        <a
          href="https://docs.dive.ai/cli"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[11px] text-surface-500 hover:text-surface-300 transition-colors flex items-center gap-1"
        >
          <span>Docs</span>
          <ExternalLink size={10} />
        </a>
      </div>

      <div className="p-4 space-y-3">
        <div>
          <p className="text-xs text-surface-400 mb-2">Install via npm</p>
          <div className="relative group">
            <pre className="bg-surface-950 border border-surface-800 rounded-lg px-3 py-2.5 text-xs font-mono text-surface-300 overflow-x-auto">
              npm install -g @dive/cli
            </pre>
            <button
              onClick={() => copyCommand('npm install -g @dive/cli')}
              className="absolute top-2 right-2 p-1.5 rounded bg-surface-800 hover:bg-surface-700 opacity-0 group-hover:opacity-100 transition-all"
            >
              {copied ? <CheckCircle2 size={12} className="text-emerald-400" /> : <Copy size={12} className="text-surface-400" />}
            </button>
          </div>
        </div>

        <div>
          <p className="text-xs text-surface-400 mb-2">Connect to your workspace</p>
          <div className="relative group">
            <pre className="bg-surface-950 border border-surface-800 rounded-lg px-3 py-2.5 text-xs font-mono text-surface-300 overflow-x-auto">
              dive login
            </pre>
            <button
              onClick={() => copyCommand('dive login')}
              className="absolute top-2 right-2 p-1.5 rounded bg-surface-800 hover:bg-surface-700 opacity-0 group-hover:opacity-100 transition-all"
            >
              {copied ? <CheckCircle2 size={12} className="text-emerald-400" /> : <Copy size={12} className="text-surface-400" />}
            </button>
          </div>
        </div>

        <div className="pt-2 border-t border-surface-800/50">
          <p className="text-[10px] text-surface-500 mb-2">Common commands:</p>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <code className="text-surface-400 font-mono">dive chat</code>
              <span className="text-surface-600">Start chat session</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <code className="text-surface-400 font-mono">dive agent list</code>
              <span className="text-surface-600">List all agents</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <code className="text-surface-400 font-mono">dive deploy</code>
              <span className="text-surface-600">Deploy agent</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DesktopAppCard() {
  return (
    <div className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-surface-800">
        <div className="flex items-center gap-2">
          <Monitor size={14} className="text-brand-400" />
          <h2 className="text-sm font-semibold text-white">Desktop App</h2>
        </div>
        <span className="text-[10px] bg-emerald-600/20 text-emerald-400 px-2 py-0.5 rounded-full font-medium">
          Beta
        </span>
      </div>

      <div className="p-4 space-y-3">
        <p className="text-xs text-surface-400">
          Get the native desktop experience with offline support and system integrations.
        </p>

        <div className="grid grid-cols-3 gap-2">
          <a
            href="https://dive.ai/download/mac"
            className="flex flex-col items-center gap-1.5 px-3 py-3 rounded-lg border border-surface-700 hover:border-surface-600 bg-surface-900/50 hover:bg-surface-800/50 transition-all group"
          >
            <Download size={16} className="text-surface-500 group-hover:text-surface-300 transition-colors" />
            <span className="text-[10px] text-surface-400 group-hover:text-surface-300 transition-colors">macOS</span>
          </a>
          <a
            href="https://dive.ai/download/windows"
            className="flex flex-col items-center gap-1.5 px-3 py-3 rounded-lg border border-surface-700 hover:border-surface-600 bg-surface-900/50 hover:bg-surface-800/50 transition-all group"
          >
            <Download size={16} className="text-surface-500 group-hover:text-surface-300 transition-colors" />
            <span className="text-[10px] text-surface-400 group-hover:text-surface-300 transition-colors">Windows</span>
          </a>
          <a
            href="https://dive.ai/download/linux"
            className="flex flex-col items-center gap-1.5 px-3 py-3 rounded-lg border border-surface-700 hover:border-surface-600 bg-surface-900/50 hover:bg-surface-800/50 transition-all group"
          >
            <Download size={16} className="text-surface-500 group-hover:text-surface-300 transition-colors" />
            <span className="text-[10px] text-surface-400 group-hover:text-surface-300 transition-colors">Linux</span>
          </a>
        </div>

        <div className="pt-2 border-t border-surface-800/50">
          <div className="space-y-1.5">
            <div className="flex items-start gap-2">
              <Zap size={12} className="text-brand-400 mt-0.5 flex-shrink-0" />
              <p className="text-[11px] text-surface-500">Native performance with system tray access</p>
            </div>
            <div className="flex items-start gap-2">
              <Code size={12} className="text-cyan-400 mt-0.5 flex-shrink-0" />
              <p className="text-[11px] text-surface-500">Code editor integration and shortcuts</p>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 size={12} className="text-emerald-400 mt-0.5 flex-shrink-0" />
              <p className="text-[11px] text-surface-500">Auto-updates and offline mode</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LlmStatusCard() {
  const navigate = useNavigate();
  const [config, setConfig] = useState<LlmConfig>(getLlmConfig);
  const [latency, setLatency] = useState<LatencyInfo | null>(getLatencyInfo);
  const [models, setModels] = useState<ModelInfo[]>(getStoredModels);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; latency?: number } | null>(null);

  useEffect(() => {
    const handleConfigChange = (e: Event) => {
      const customEvent = e as CustomEvent<LlmConfig>;
      if (customEvent.detail) setConfig(customEvent.detail);
    };
    const handleLatencyChange = (e: Event) => {
      const customEvent = e as CustomEvent<LatencyInfo>;
      if (customEvent.detail) setLatency(customEvent.detail);
    };
    const handleModelsChange = (e: Event) => {
      const customEvent = e as CustomEvent<ModelInfo[]>;
      if (customEvent.detail) setModels(customEvent.detail);
    };

    window.addEventListener('llm-config-changed', handleConfigChange);
    window.addEventListener('llm-latency-changed', handleLatencyChange);
    window.addEventListener('llm-models-changed', handleModelsChange);
    return () => {
      window.removeEventListener('llm-config-changed', handleConfigChange);
      window.removeEventListener('llm-latency-changed', handleLatencyChange);
      window.removeEventListener('llm-models-changed', handleModelsChange);
    };
  }, []);

  const handleTest = async () => {
    if (!config.apiKey || !config.baseUrl) return;
    setTesting(true);
    setTestResult(null);

    try {
      const { models: fetchedModels, latency: responseLatency } = await fetchModelsFromApi(config.baseUrl, config.apiKey);
      if (fetchedModels.length > 0) {
        const modelsWithProvider = fetchedModels.map(m => ({ ...m, provider: config.provider }));
        setModels(modelsWithProvider);
        setStoredModels(modelsWithProvider);

        const latencyInfo: LatencyInfo = {
          latency: responseLatency,
          timestamp: Date.now(),
          provider: config.provider,
        };
        setLatency(latencyInfo);
        setLatencyInfo(latencyInfo);
        setTestResult({ ok: true, latency: responseLatency });
      } else {
        setTestResult({ ok: false });
      }
    } catch {
      setTestResult({ ok: false });
    }
    setTesting(false);
  };

  const isConfigured = config.apiKey && config.baseUrl;
  const providerLabel = getProviderLabel(config.provider);
  const currentModel = models.find(m => m.id === config.model);

  return (
    <div className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-surface-800">
        <div className="flex items-center gap-2">
          <Key size={14} className="text-brand-400" />
          <h2 className="text-sm font-semibold text-white">LLM Status</h2>
        </div>
        <button
          onClick={() => navigate('/settings')}
          className="text-[11px] text-surface-500 hover:text-surface-300 transition-colors flex items-center gap-1"
        >
          <Settings size={10} />
          Configure
        </button>
      </div>

      <div className="p-4 space-y-3">
        {isConfigured ? (
          <>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <StatusDot status={testResult?.ok !== false ? 'active' : 'error'} />
                <span className="text-xs text-surface-300">
                  {currentModel?.label || config.model}
                </span>
              </div>
              <span className="text-[10px] text-surface-500">{providerLabel}</span>
            </div>

            <div className="flex items-center justify-between py-2 px-3 bg-surface-800/50 rounded-lg">
              <div>
                <p className="text-[10px] text-surface-500 uppercase tracking-wider mb-0.5">Latency</p>
                {latency ? (
                  <p className={`text-lg font-bold font-mono ${
                    latency.latency < 200 ? 'text-emerald-400' : latency.latency < 500 ? 'text-amber-400' : 'text-rose-400'
                  }`}>
                    {latency.latency}ms
                  </p>
                ) : (
                  <p className="text-sm text-surface-500">-</p>
                )}
              </div>
              <div className="text-right">
                <p className="text-[10px] text-surface-500 uppercase tracking-wider mb-0.5">Models</p>
                <p className="text-lg font-bold font-mono text-surface-300">{models.length}</p>
              </div>
            </div>

            {testResult && (
              <div className={`flex items-center gap-2 text-[11px] ${testResult.ok ? 'text-emerald-400' : 'text-rose-400'}`}>
                {testResult.ok ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                {testResult.ok ? `Connected - ${testResult.latency}ms` : 'Connection failed'}
              </div>
            )}

            <button
              onClick={handleTest}
              disabled={testing}
              className="w-full flex items-center justify-center gap-2 text-xs font-medium px-3 py-2 rounded-lg border border-surface-700 text-surface-300 hover:text-white hover:border-surface-600 transition-all disabled:opacity-50"
            >
              {testing ? <Spinner size="sm" /> : <RefreshCw size={12} />}
              Test Connection
            </button>
          </>
        ) : (
          <div className="text-center py-4">
            <Zap size={24} className="text-surface-600 mx-auto mb-2" />
            <p className="text-xs text-surface-400 mb-3">No API configured</p>
            <button
              onClick={() => navigate('/settings')}
              className="text-xs text-brand-400 hover:text-brand-300 font-medium transition-colors"
            >
              Setup your LLM provider
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { isGuest } = useAuth();
  const { currentWorkspace } = useWorkspace();
  const { data: conversations } = useConversations(isGuest ? undefined : currentWorkspace?.id);
  const { data: agents } = useAgents(isGuest ? undefined : currentWorkspace?.id);
  const createConversation = useCreateConversation();
  const navigate = useNavigate();

  useRealtimeConversations(isGuest ? undefined : currentWorkspace?.id);
  useRealtimeAgents(isGuest ? undefined : currentWorkspace?.id);

  const [latency] = useState<LatencyInfo | null>(getLatencyInfo);
  const activeAgents = (agents ?? []).filter((a) => a.status === 'active').length;
  const recentChats = (conversations ?? []).slice(0, 6);

  const handleNewChat = async () => {
    if (isGuest) {
      navigate('/chat');
      return;
    }
    if (!currentWorkspace) return;
    const conv = await createConversation.mutateAsync({ workspaceId: currentWorkspace.id });
    navigate(`/chat/${conv.id}`);
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 max-w-6xl mx-auto animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-white">{currentWorkspace?.name ?? 'Dashboard'}</h1>
            <p className="text-xs text-surface-500 mt-0.5 font-mono">System overview and activity monitor</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-900 border border-surface-800 text-[11px]">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-emerald-400">System Online</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <MetricCard
            icon={MessageSquare}
            label="Conversations"
            value={(conversations ?? []).length}
            sub="Total threads"
            accentClass="bg-brand-600"
          />
          <MetricCard
            icon={Bot}
            label="Active Agents"
            value={activeAgents}
            sub={`${(agents ?? []).length} configured`}
            accentClass="bg-emerald-600"
          />
          <MetricCard
            icon={Activity}
            label="API Latency"
            value={latency ? `${latency.latency}ms` : '-'}
            sub={latency ? getProviderLabel(latency.provider) : 'Not tested'}
            accentClass={latency ? (latency.latency < 200 ? 'bg-emerald-600' : latency.latency < 500 ? 'bg-amber-600' : 'bg-rose-600') : 'bg-surface-600'}
          />
          <MetricCard
            icon={Zap}
            label="Models"
            value={getStoredModels().length}
            sub="Available"
            accentClass="bg-cyan-600"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <CliSetupCard />
          <DesktopAppCard />
          <LlmStatusCard />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-surface-800">
                <div className="flex items-center gap-2">
                  <Clock size={14} className="text-surface-500" />
                  <h2 className="text-sm font-semibold text-white">Recent Activity</h2>
                  <span className="text-[10px] bg-surface-800 text-surface-400 px-1.5 py-0.5 rounded font-mono">
                    {recentChats.length}
                  </span>
                </div>
                <button
                  onClick={handleNewChat}
                  className="flex items-center gap-1.5 text-[11px] text-brand-400 hover:text-brand-300 transition-colors font-medium"
                >
                  <Plus size={12} />
                  New Chat
                </button>
              </div>

              {recentChats.length === 0 ? (
                <div className="py-12 text-center">
                  <Terminal size={28} className="text-surface-700 mx-auto mb-3" />
                  <p className="text-surface-500 text-xs mb-2">No conversations yet</p>
                  <button
                    onClick={handleNewChat}
                    className="text-brand-400 text-xs hover:text-brand-300 transition-colors font-medium"
                  >
                    Start your first chat
                  </button>
                </div>
              ) : (
                <div className="divide-y divide-surface-800/50">
                  {recentChats.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => navigate(`/chat/${c.id}`)}
                      className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-surface-800/50 transition-colors group"
                    >
                      <div className="flex items-center gap-3">
                        <MessageSquare size={14} className="text-surface-600" />
                        <div className="text-left">
                          <span className="text-xs text-surface-200 group-hover:text-white transition-colors block">
                            {truncate(c.title, 45)}
                          </span>
                          <span className="text-[10px] text-surface-600 font-mono">{c.model || 'gpt-4o-mini'}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-surface-600 font-mono">{formatRelativeTime(c.updated_at)}</span>
                        <ArrowRight size={12} className="text-surface-700 opacity-0 group-hover:opacity-100 transition-all" />
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-surface-800">
                <div className="flex items-center gap-2">
                  <Bot size={14} className="text-surface-500" />
                  <h2 className="text-sm font-semibold text-white">Agents</h2>
                </div>
                <button
                  onClick={() => navigate('/agents')}
                  className="text-[11px] text-surface-500 hover:text-surface-300 transition-colors"
                >
                  View all
                </button>
              </div>

              {(agents ?? []).length === 0 ? (
                <div className="py-8 text-center">
                  <Bot size={24} className="text-surface-700 mx-auto mb-2" />
                  <p className="text-surface-500 text-xs mb-2">No agents configured</p>
                  <button
                    onClick={() => navigate('/agents')}
                    className="text-brand-400 text-xs hover:text-brand-300 transition-colors font-medium"
                  >
                    Create an agent
                  </button>
                </div>
              ) : (
                <div className="divide-y divide-surface-800/50">
                  {(agents ?? []).slice(0, 4).map((a) => (
                    <div key={a.id} className="flex items-center gap-3 px-4 py-2.5">
                      <StatusDot status={a.status} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-surface-200 truncate">{a.name}</p>
                        <p className="text-[10px] text-surface-600 font-mono">{a.model}</p>
                      </div>
                      <span className="text-[10px] text-surface-600 capitalize">{a.status}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
