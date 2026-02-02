import { useState, useEffect, useCallback } from 'react';
import { 
  Server, 
  Cpu, 
  Sparkles, 
  Database, 
  Download,
  Lock,
  Info,
  Eye,
  EyeOff,
  ExternalLink,
  Check,
  Loader2,
  RefreshCw,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { mockRuntimeConfig } from '@/data/mockData';
import { LLM_PROVIDERS, DEFAULT_LLM_CONFIG, type LLMConfig, type LLMModel } from '@/data/llmProviders';

const STORAGE_KEY = 'dive_coder_llm_config';

type ConnectionStatus = 'idle' | 'loading' | 'success' | 'error';

export function SettingsTab() {
  const config = mockRuntimeConfig;
  const [showApiKey, setShowApiKey] = useState(false);
  const [llmConfig, setLlmConfig] = useState<LLMConfig>(DEFAULT_LLM_CONFIG);
  const [saved, setSaved] = useState(false);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('idle');
  const [connectionMessage, setConnectionMessage] = useState('');
  const [isLoadingModels, setIsLoadingModels] = useState(false);

  // Load config from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setLlmConfig(parsed);
      } catch (e) {
        console.error('Failed to parse LLM config:', e);
      }
    }
  }, []);

  const selectedProvider = LLM_PROVIDERS.find(p => p.id === llmConfig.providerId) || LLM_PROVIDERS[0];
  
  const getBaseUrl = useCallback(() => {
    if (selectedProvider.isCustom) {
      return llmConfig.customBaseUrl || '';
    }
    return selectedProvider.baseUrl;
  }, [selectedProvider, llmConfig.customBaseUrl]);

  // Fetch models from API
  const fetchModels = useCallback(async () => {
    const baseUrl = getBaseUrl();
    const apiKey = llmConfig.apiKey;

    if (!baseUrl || !apiKey) {
      setConnectionStatus('error');
      setConnectionMessage('Base URL and API Key are required');
      return;
    }

    setIsLoadingModels(true);
    setConnectionStatus('loading');
    setConnectionMessage('Connecting...');

    try {
      // Try OpenAI-compatible endpoint
      const modelsUrl = baseUrl.endsWith('/v1') 
        ? `${baseUrl}/models` 
        : `${baseUrl}/v1/models`;
      
      const response = await fetch(modelsUrl, {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Parse OpenAI-compatible response
      const fetchedModels: LLMModel[] = (data.data || []).map((m: { id: string; name?: string }) => ({
        id: m.id,
        name: m.name || m.id,
      }));

      setModels(fetchedModels);
      setConnectionStatus('success');
      setConnectionMessage(`Connected! ${fetchedModels.length} models available`);
      
      // Auto-select first model if none selected
      if (fetchedModels.length > 0 && !llmConfig.modelId) {
        setLlmConfig(prev => ({ ...prev, modelId: fetchedModels[0].id }));
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
      setConnectionStatus('error');
      setConnectionMessage(error instanceof Error ? error.message : 'Connection failed');
      setModels([]);
    } finally {
      setIsLoadingModels(false);
    }
  }, [getBaseUrl, llmConfig.apiKey, llmConfig.modelId]);

  // Auto-fetch models when API key changes and we have base URL
  useEffect(() => {
    if (llmConfig.apiKey && getBaseUrl()) {
      const timer = setTimeout(() => {
        fetchModels();
      }, 500); // Debounce
      return () => clearTimeout(timer);
    }
  }, [llmConfig.apiKey, getBaseUrl, fetchModels]);

  const handleProviderChange = (providerId: string) => {
    setLlmConfig(prev => ({
      ...prev,
      providerId,
      modelId: '',
    }));
    setModels([]);
    setConnectionStatus('idle');
    setConnectionMessage('');
    setSaved(false);
  };

  const handleModelChange = (modelId: string) => {
    setLlmConfig(prev => ({ ...prev, modelId }));
    setSaved(false);
  };

  const handleApiKeyChange = (apiKey: string) => {
    setLlmConfig(prev => ({ ...prev, apiKey }));
    setSaved(false);
  };

  const handleCustomBaseUrlChange = (customBaseUrl: string) => {
    setLlmConfig(prev => ({ ...prev, customBaseUrl }));
    setModels([]);
    setConnectionStatus('idle');
    setSaved(false);
  };

  const handleSave = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(llmConfig));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleExportLogs = () => {
    const logs = [
      { timestamp: Date.now(), level: 'info', message: 'Runtime initialized' },
      { timestamp: Date.now(), level: 'debug', message: 'RAG index loaded' },
    ];
    const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'dive_coder_logs.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <Server className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="text-lg font-semibold">Runtime Configuration</h1>
          <p className="text-sm text-muted-foreground">Configure LLM providers and view settings</p>
        </div>
      </div>

      {/* LLM Configuration - Editable */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-5 h-5 text-accent" />
          <h2 className="text-sm font-semibold">LLM Configuration</h2>
        </div>
        
        <div className="space-y-4">
          {/* Provider Selection */}
          <div className="space-y-2">
            <Label className="text-sm text-muted-foreground">
              API Provider
            </Label>
            <Select value={llmConfig.providerId} onValueChange={handleProviderChange}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent className="bg-background border-border">
                {LLM_PROVIDERS.map((provider) => (
                  <SelectItem key={provider.id} value={provider.id}>
                    {provider.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {!selectedProvider.isCustom && (
              <div className="text-2xs text-muted-foreground flex items-center gap-1">
                Base URL: <code className="text-primary/80">{selectedProvider.baseUrl}</code>
                {selectedProvider.guideUrl && (
                  <a 
                    href={selectedProvider.guideUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="ml-2 text-primary hover:text-primary/80 inline-flex items-center gap-1"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Guide
                  </a>
                )}
              </div>
            )}
          </div>

          {/* Custom Base URL (only for custom provider) */}
          {selectedProvider.isCustom && (
            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">
                Base URL
              </Label>
              <Input
                type="url"
                value={llmConfig.customBaseUrl || ''}
                onChange={(e) => handleCustomBaseUrlChange(e.target.value)}
                placeholder="https://api.example.com/v1"
                className="bg-background border-border font-mono text-sm"
              />
              <p className="text-2xs text-muted-foreground">
                OpenAI-compatible API endpoint (e.g., https://api.openai.com/v1)
              </p>
            </div>
          )}

          {/* API Key */}
          <div className="space-y-2">
            <Label className="text-sm text-muted-foreground">
              API Key
            </Label>
            <div className="relative">
              <Input
                type={showApiKey ? 'text' : 'password'}
                value={llmConfig.apiKey}
                onChange={(e) => handleApiKeyChange(e.target.value)}
                placeholder="sk-..."
                className="bg-background border-border pr-10 font-mono text-sm"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Connection Status */}
          {connectionStatus !== 'idle' && (
            <div className={`flex items-center gap-2 p-2 rounded text-sm ${
              connectionStatus === 'loading' ? 'bg-muted/30 text-muted-foreground' :
              connectionStatus === 'success' ? 'bg-status-completed/10 text-status-completed' :
              'bg-status-failed/10 text-status-failed'
            }`}>
              {connectionStatus === 'loading' && <Loader2 className="w-4 h-4 animate-spin" />}
              {connectionStatus === 'success' && <CheckCircle2 className="w-4 h-4" />}
              {connectionStatus === 'error' && <AlertCircle className="w-4 h-4" />}
              <span className="text-2xs">{connectionMessage}</span>
            </div>
          )}

          {/* Model Selection */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-sm text-muted-foreground">
                Model
              </Label>
              <Button
                variant="ghost"
                size="sm"
                onClick={fetchModels}
                disabled={isLoadingModels || !llmConfig.apiKey || !getBaseUrl()}
                className="h-6 px-2 text-2xs"
              >
                {isLoadingModels ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <RefreshCw className="w-3 h-3" />
                )}
                <span className="ml-1">Refresh</span>
              </Button>
            </div>
            <Select 
              value={llmConfig.modelId} 
              onValueChange={handleModelChange}
              disabled={models.length === 0}
            >
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder={models.length === 0 ? "Enter API key to load models" : "Select model"} />
              </SelectTrigger>
              <SelectContent className="bg-background border-border max-h-60">
                {models.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {model.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {models.length === 0 && llmConfig.apiKey && connectionStatus !== 'loading' && (
              <p className="text-2xs text-muted-foreground">
                Click refresh or enter valid API key to fetch available models
              </p>
            )}
          </div>

          {/* Save Button */}
          <div className="flex justify-end pt-2">
            <Button
              onClick={handleSave}
              size="sm"
              disabled={!llmConfig.modelId}
              className={saved ? 'bg-status-completed hover:bg-status-completed/90' : ''}
            >
              {saved ? (
                <>
                  <Check className="w-4 h-4 mr-1" />
                  Saved
                </>
              ) : (
                'Save Configuration'
              )}
            </Button>
          </div>
        </div>
        
        <div className="flex items-start gap-2 mt-4 p-2 rounded bg-muted/30">
          <Info className="w-3 h-3 text-muted-foreground mt-0.5 shrink-0" />
          <p className="text-2xs text-muted-foreground">
            Your API key is stored locally. Models are fetched from the provider's /v1/models endpoint.
          </p>
        </div>
      </div>

      {/* Transport */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-3 mb-4">
          <Cpu className="w-5 h-5 text-primary" />
          <h2 className="text-sm font-semibold">Transport</h2>
        </div>
        
        <div className="flex items-center justify-between p-3 rounded-lg bg-background border border-border">
          <div>
            <div className="text-sm font-medium">Mode</div>
            <div className="text-2xs text-muted-foreground">
              Communication protocol with Antigravity host
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Lock className="w-3 h-3 text-muted-foreground" />
            <span className="text-sm font-mono text-primary">{config.transport}</span>
          </div>
        </div>
        
        <div className="flex items-start gap-2 mt-3 p-2 rounded bg-muted/30">
          <Info className="w-3 h-3 text-muted-foreground mt-0.5 shrink-0" />
          <p className="text-2xs text-muted-foreground">
            Transport is locked to stdio. UI communicates via HTTP for observability only.
          </p>
        </div>
      </div>

      {/* RAG Settings */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-3 mb-4">
          <Database className="w-5 h-5 text-info" />
          <h2 className="text-sm font-semibold">RAG Configuration</h2>
        </div>
        
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 rounded-lg bg-background border border-border">
            <div className="text-2xs text-muted-foreground mb-1">Max Context</div>
            <div className="text-lg font-bold text-gradient-cyan">
              {(config.rag.max_context_chars / 1000).toFixed(0)}k
            </div>
            <div className="text-2xs text-muted-foreground">chars</div>
          </div>
          
          <div className="p-3 rounded-lg bg-background border border-border">
            <div className="text-2xs text-muted-foreground mb-1">Chunk Size</div>
            <div className="text-lg font-bold text-foreground">
              {config.rag.chunk_size}
            </div>
            <div className="text-2xs text-muted-foreground">chars</div>
          </div>
          
          <div className="p-3 rounded-lg bg-background border border-border">
            <div className="text-2xs text-muted-foreground mb-1">Overlap</div>
            <div className="text-lg font-bold text-foreground">
              {config.rag.overlap}
            </div>
            <div className="text-2xs text-muted-foreground">chars</div>
          </div>
        </div>
      </div>

      {/* Advanced - Collapsed placeholder */}
      <details className="glass-card">
        <summary className="p-4 cursor-pointer text-sm font-semibold text-muted-foreground hover:text-foreground transition-colors">
          Advanced Settings
        </summary>
        <div className="px-4 pb-4">
          <div className="p-3 rounded-lg bg-muted/30 text-center">
            <p className="text-2xs text-muted-foreground">
              ANN tuning, custom retrievers, and experimental features coming soon.
            </p>
          </div>
        </div>
      </details>

      {/* Logs Export */}
      <div className="glass-card p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold">Logs</h2>
            <p className="text-2xs text-muted-foreground mt-1">
              Export runtime logs for debugging
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="border-primary/30 text-primary hover:bg-primary/10"
            onClick={handleExportLogs}
          >
            <Download className="w-4 h-4 mr-2" />
            Export Logs
          </Button>
        </div>
      </div>
    </div>
  );
}
