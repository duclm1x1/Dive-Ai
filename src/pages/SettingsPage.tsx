import { useState, useEffect } from 'react';
import {
  Save,
  Users,
  Shield,
  Key,
  Server,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { Spinner } from '../components/ui/Spinner';
import { Avatar } from '../components/ui/Avatar';
import {
  getLlmConfig,
  setLlmConfig,
  getStoredModels,
  setStoredModels,
  fetchModelsFromApi,
  groupModelsByCategory,
  getLatencyInfo,
  setLatencyInfo,
  getProviderLabel,
  type ModelInfo,
  type LatencyInfo,
} from '../lib/llmConfig';
import type { WorkspaceMember } from '../types';

const PROVIDERS = [
  { id: 'openai', label: 'OpenAI', baseUrl: 'https://api.openai.com/v1' },
  { id: 'v98', label: 'V98 Store', baseUrl: 'https://v98store.com/v1' },
  { id: 'aicoding', label: 'AI Coding', baseUrl: 'https://aicoding.io.vn/v1' },
  { id: 'groq', label: 'Groq', baseUrl: 'https://api.groq.com/openai/v1' },
  { id: 'deepseek', label: 'DeepSeek', baseUrl: 'https://api.deepseek.com/v1' },
  { id: 'openrouter', label: 'OpenRouter', baseUrl: 'https://openrouter.ai/api/v1' },
  { id: 'together', label: 'Together AI', baseUrl: 'https://api.together.xyz/v1' },
  { id: 'custom', label: 'Custom', baseUrl: '' },
];

function LlmConfigSection() {
  const [config, setConfigState] = useState(getLlmConfig);
  const [models, setModels] = useState<ModelInfo[]>(getStoredModels);
  const [latency, setLatency] = useState<LatencyInfo | null>(getLatencyInfo);
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [fetchingModels, setFetchingModels] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string; latency?: number } | null>(null);

  const handleProviderChange = (providerId: string) => {
    const provider = PROVIDERS.find((p) => p.id === providerId) || PROVIDERS[0];
    const baseUrl = provider.baseUrl || '';
    setConfigState({ ...config, provider: providerId, baseUrl });
    setTestResult(null);
  };

  const handleFetchModels = async (): Promise<{ success: boolean; latency?: number }> => {
    if (!config.apiKey || !config.baseUrl) {
      setTestResult({ ok: false, message: 'API key and base URL required' });
      return { success: false };
    }

    setFetchingModels(true);
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

        if (!modelsWithProvider.find(m => m.id === config.model)) {
          setConfigState({ ...config, model: modelsWithProvider[0].id });
        }
        setTestResult({ ok: true, message: `Loaded ${modelsWithProvider.length} models`, latency: responseLatency });
        return { success: true, latency: responseLatency };
      } else {
        setTestResult({ ok: false, message: 'No models found' });
        return { success: false };
      }
    } catch (err) {
      setTestResult({ ok: false, message: err instanceof Error ? err.message : 'Failed to fetch models' });
      return { success: false };
    } finally {
      setFetchingModels(false);
    }
  };

  const handleSave = async () => {
    setLlmConfig(config);

    if (config.apiKey && config.baseUrl) {
      await handleFetchModels();
    }

    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const providerLabel = getProviderLabel(config.provider);

  const currentModelInfo = models.find(m => m.id === config.model);

  return (
    <section className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
      <div className="flex items-center gap-3 px-5 py-3.5 border-b border-surface-800">
        <Key size={16} className="text-brand-400" />
        <h2 className="text-sm font-semibold text-white">LLM Configuration</h2>
        <div className="flex items-center gap-2">
          <span className="text-[10px] bg-surface-800 text-surface-400 px-1.5 py-0.5 rounded font-mono">
            {currentModelInfo?.label || config.model}
          </span>
          <span className="text-[10px] text-surface-600">-</span>
          <span className="text-[10px] text-surface-500">{providerLabel}</span>
          {latency && (
            <>
              <span className="text-[10px] text-surface-600">-</span>
              <span className={`text-[10px] font-mono ${latency.latency < 200 ? 'text-emerald-400' : latency.latency < 500 ? 'text-amber-400' : 'text-rose-400'}`}>
                {latency.latency}ms
              </span>
            </>
          )}
        </div>
      </div>

      <div className="p-5 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">
              Provider
            </label>
            <select
              value={config.provider}
              onChange={(e) => handleProviderChange(e.target.value)}
              className="w-full bg-surface-800 border border-surface-700 text-surface-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-600 transition-colors"
            >
              {PROVIDERS.map((p) => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">
              Model
              {models.length > 0 && (
                <span className="text-surface-600 font-normal ml-1">({models.length} available)</span>
              )}
            </label>
            <div className="flex gap-2">
              {models.length > 0 ? (
                <select
                  value={config.model}
                  onChange={(e) => setConfigState({ ...config, model: e.target.value })}
                  className="flex-1 bg-surface-800 border border-surface-700 text-surface-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-600 transition-colors"
                >
                  {groupModelsByCategory(models).map((group) => (
                    <optgroup key={group.category} label={group.category}>
                      {group.models.map((m) => (
                        <option key={m.id} value={m.id}>{m.label}</option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={config.model}
                  onChange={(e) => setConfigState({ ...config, model: e.target.value })}
                  placeholder="Enter model name or fetch from API"
                  className="flex-1 bg-surface-800 border border-surface-700 text-surface-200 placeholder-surface-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-600 transition-colors font-mono"
                />
              )}
              <button
                onClick={handleFetchModels}
                disabled={fetchingModels || !config.apiKey || !config.baseUrl}
                title="Fetch available models from API"
                className="flex items-center justify-center w-9 h-9 rounded-lg border border-surface-700 text-surface-400 hover:text-surface-200 hover:border-surface-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {fetchingModels ? <Spinner size="sm" /> : <RefreshCw size={14} />}
              </button>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">
            API Key
          </label>
          <div className="relative">
            <input
              type={showKey ? 'text' : 'password'}
              value={config.apiKey}
              onChange={(e) => { setConfigState({ ...config, apiKey: e.target.value }); setTestResult(null); }}
              placeholder="sk-..."
              className="w-full bg-surface-800 border border-surface-700 text-surface-200 placeholder-surface-600 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:border-brand-600 transition-colors font-mono"
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-surface-500 hover:text-surface-300 transition-colors"
            >
              {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>
          <p className="text-[10px] text-surface-600 mt-1">
            Stored locally in your browser. Never sent to our servers.
          </p>
          {(config.provider === 'v98' || config.provider === 'aicoding') && (
            <div className="mt-2 text-[10px] text-surface-500">
              Get your API key at:{' '}
              {config.provider === 'v98' ? (
                <a href="https://v98store.com/" target="_blank" rel="noopener noreferrer" className="text-brand-400 hover:text-brand-300 underline">
                  v98store.com
                </a>
              ) : (
                <a href="https://docs.aicoding.io.vn/" target="_blank" rel="noopener noreferrer" className="text-brand-400 hover:text-brand-300 underline">
                  docs.aicoding.io.vn
                </a>
              )}
            </div>
          )}
        </div>

        <div>
          <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">
            Custom Base URL <span className="text-surface-600">(optional)</span>
          </label>
          <div className="flex items-center gap-2">
            <Server size={14} className="text-surface-600 flex-shrink-0" />
            <input
              type="text"
              value={config.baseUrl}
              onChange={(e) => setConfigState({ ...config, baseUrl: e.target.value })}
              placeholder="https://api.openai.com/v1"
              className="flex-1 bg-surface-800 border border-surface-700 text-surface-200 placeholder-surface-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-600 transition-colors font-mono"
            />
          </div>
        </div>

        {testResult && (
          <div className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs ${
            testResult.ok
              ? 'bg-emerald-600/10 border border-emerald-600/20 text-emerald-400'
              : 'bg-rose-600/10 border border-rose-600/20 text-rose-400'
          }`}>
            <div className="flex items-center gap-2">
              {testResult.ok ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
              {testResult.message}
            </div>
            {testResult.latency && (
              <span className={`font-mono font-semibold ${testResult.latency < 200 ? 'text-emerald-400' : testResult.latency < 500 ? 'text-amber-400' : 'text-rose-400'}`}>
                {testResult.latency}ms
              </span>
            )}
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2 pt-1">
          <button
            onClick={handleSave}
            disabled={fetchingModels}
            className="flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-all duration-200 disabled:opacity-70"
          >
            {fetchingModels ? <Spinner size="sm" /> : saved ? <CheckCircle2 size={14} /> : <Save size={14} />}
            {fetchingModels ? 'Testing...' : saved ? 'Saved' : 'Save & Test'}
          </button>
        </div>

        <div className="pt-2 border-t border-surface-800">
          <p className="text-[10px] text-surface-600 mb-2 uppercase tracking-wider">Quick Setup</p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setConfigState({
                provider: 'v98',
                model: 'gpt-4o-mini',
                apiKey: 'YOUR_V98_API_KEY_HERE',
                baseUrl: 'https://v98store.com/v1'
              })}
              className="text-[10px] px-2.5 py-1.5 rounded-md bg-surface-800 hover:bg-surface-700 text-surface-300 border border-surface-700 transition-colors"
            >
              Load V98 Demo
            </button>
            <button
              onClick={() => setConfigState({
                provider: 'aicoding',
                model: 'claude-sonnet-4-5-20250929',
                apiKey: 'YOUR_AICODING_API_KEY_HERECJCk',
                baseUrl: 'https://aicoding.io.vn/v1'
              })}
              className="text-[10px] px-2.5 py-1.5 rounded-md bg-surface-800 hover:bg-surface-700 text-surface-300 border border-surface-700 transition-colors"
            >
              Load AIcoding Demo
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

export function SettingsPage() {
  const { user, profile, refreshProfile, isGuest } = useAuth();
  const { currentWorkspace, refetch } = useWorkspace();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [fullName, setFullName] = useState('');
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [saving, setSaving] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (currentWorkspace) {
      setName(currentWorkspace.name);
      setDescription(currentWorkspace.description);
      if (!isGuest) fetchMembers();
    }
  }, [currentWorkspace, isGuest]);

  useEffect(() => {
    if (profile) setFullName(profile.full_name);
  }, [profile]);

  const fetchMembers = async () => {
    if (!currentWorkspace) return;
    const { data } = await supabase
      .from('workspace_members')
      .select('*, profiles(*)')
      .eq('workspace_id', currentWorkspace.id);
    setMembers((data ?? []) as WorkspaceMember[]);
  };

  const handleSaveWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentWorkspace) return;
    setSaving(true);
    setMessage('');
    const { error } = await supabase
      .from('workspaces')
      .update({ name, description })
      .eq('id', currentWorkspace.id);
    if (error) {
      setMessage(error.message);
    } else {
      setMessage('Workspace updated');
      await refetch();
    }
    setSaving(false);
    setTimeout(() => setMessage(''), 3000);
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setSavingProfile(true);
    await supabase.from('profiles').update({ full_name: fullName }).eq('id', user.id);
    await refreshProfile();
    setSavingProfile(false);
    setMessage('Profile updated');
    setTimeout(() => setMessage(''), 3000);
  };

  const isOwner = currentWorkspace?.owner_id === user?.id;

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 max-w-3xl mx-auto animate-fade-in space-y-4">
        <div className="mb-2">
          <h1 className="text-xl font-bold text-white">Settings</h1>
          <p className="text-xs text-surface-500 mt-0.5 font-mono">Configuration and preferences</p>
        </div>

        {message && (
          <div className="flex items-center gap-2 bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs px-3.5 py-2.5 rounded-lg animate-fade-in">
            <CheckCircle2 size={14} />
            {message}
          </div>
        )}

        <LlmConfigSection />

        {!isGuest && (
          <section className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
            <div className="flex items-center gap-3 px-5 py-3.5 border-b border-surface-800">
              <Shield size={16} className="text-brand-400" />
              <h2 className="text-sm font-semibold text-white">Profile</h2>
            </div>
            <form onSubmit={handleSaveProfile} className="p-5 space-y-4">
              <div>
                <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">Full name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full max-w-sm bg-surface-800 border border-surface-700 text-surface-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-600 transition-colors"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">Email</label>
                <input
                  type="email"
                  value={profile?.email ?? ''}
                  disabled
                  className="w-full max-w-sm bg-surface-800 border border-surface-700 text-surface-500 rounded-lg px-3 py-2 text-sm opacity-60"
                />
              </div>
              <button type="submit" disabled={savingProfile} className="flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-all duration-200 disabled:opacity-50">
                {savingProfile ? <Spinner size="sm" /> : <Save size={14} />}
                Save Profile
              </button>
            </form>
          </section>
        )}

        {!isGuest && currentWorkspace && (
          <>
            <section className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
              <div className="px-5 py-3.5 border-b border-surface-800">
                <h2 className="text-sm font-semibold text-white">Workspace</h2>
              </div>
              <form onSubmit={handleSaveWorkspace} className="p-5 space-y-4">
                <div>
                  <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full max-w-sm bg-surface-800 border border-surface-700 text-surface-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-600 transition-colors"
                    disabled={!isOwner}
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-surface-400 uppercase tracking-wider mb-1.5">Description</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full max-w-sm bg-surface-800 border border-surface-700 text-surface-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-600 transition-colors resize-none h-20"
                    disabled={!isOwner}
                  />
                </div>
                {isOwner && (
                  <button type="submit" disabled={saving} className="flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white transition-all duration-200 disabled:opacity-50">
                    {saving ? <Spinner size="sm" /> : <Save size={14} />}
                    Save Changes
                  </button>
                )}
              </form>
            </section>

            <section className="bg-surface-900 border border-surface-800 rounded-lg overflow-hidden">
              <div className="flex items-center gap-3 px-5 py-3.5 border-b border-surface-800">
                <Users size={16} className="text-brand-400" />
                <h2 className="text-sm font-semibold text-white">Members</h2>
                <span className="text-[10px] bg-surface-800 text-surface-400 px-1.5 py-0.5 rounded font-mono">
                  {members.length}
                </span>
              </div>
              <div className="divide-y divide-surface-800/50">
                {members.map((m) => (
                  <div key={m.id} className="flex items-center justify-between py-2.5 px-5 hover:bg-surface-800/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <Avatar name={m.profiles?.full_name || m.profiles?.email || '?'} size="sm" />
                      <div>
                        <p className="text-xs text-surface-200">{m.profiles?.full_name || 'Unknown'}</p>
                        <p className="text-[10px] text-surface-500">{m.profiles?.email}</p>
                      </div>
                    </div>
                    <span className="text-[10px] bg-surface-800 text-surface-400 px-2 py-0.5 rounded font-mono capitalize">
                      {m.role}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}
