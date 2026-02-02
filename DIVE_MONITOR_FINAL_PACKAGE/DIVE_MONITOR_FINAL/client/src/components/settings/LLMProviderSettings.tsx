import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Trash2, Plus, Check, X, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface LLMProvider {
  id: string;
  name: string;
  type: "v98api" | "aicoding" | "openai" | "anthropic" | "custom";
  baseUrl: string;
  apiKey: string;
  model: string;
  enabled: boolean;
  priority: number;
}

const PROVIDER_TEMPLATES = {
  v98api: {
    name: "V98 API",
    baseUrl: "https://v98store.com/v1",
    models: [
      "claude-opus-4-5-20251101",
      "claude-sonnet-4-5-20250929",
      "claude-haiku-4-5-20251001",
      "gpt-5.2-pro",
      "gpt-4.1",
      "gemini-2.5-flash"
    ],
  },
  aicoding: {
    name: "AI Coding",
    baseUrl: "https://aicoding.io.vn/v1",
    models: [
      "claude-opus-4-5-20251101",
      "claude-sonnet-4-5-20250929",
      "claude-haiku-4-5-20251001"
    ],
  },
  openai: {
    name: "OpenAI",
    baseUrl: "https://api.openai.com/v1",
    models: ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
  },
  anthropic: {
    name: "Anthropic",
    baseUrl: "https://api.anthropic.com/v1",
    models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
  },
  custom: {
    name: "Custom Provider",
    baseUrl: "",
    models: [],
  },
};

export function LLMProviderSettings() {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [testingProvider, setTestingProvider] = useState<string | null>(null);

  // Load providers from server on mount
  useEffect(() => {
    const loadProviders = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787'}/v1/providers`);
        if (response.ok) {
          const data = await response.json();
          if (data.providers && data.providers.length > 0) {
            setProviders(data.providers);
          } else {
            // Set default providers if none exist
            const defaultProviders = [
              {
                id: "1",
                name: "V98 API",
                type: "v98api" as const,
                baseUrl: "https://v98store.com/v1",
                apiKey: "sk-dBWRD0cFgIBLf36nPAeuMRNSeFvvLfDtYS1mbR3RIpVSoR7y",
                model: "claude-opus-4-5-20251101",
                enabled: true,
                priority: 1,
              },
              {
                id: "2",
                name: "AI Coding",
                type: "aicoding" as const,
                baseUrl: "https://aicoding.io.vn/v1",
                apiKey: "sk-dev-0kgTls1jmGOn3K4Fdl7Rdudkl7QSCJCk",
                model: "claude-opus-4-5-20251101",
                enabled: true,
                priority: 2,
              },
            ];
            setProviders(defaultProviders);
            // Save defaults to server
            await fetch(`${import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787'}/v1/providers`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ providers: defaultProviders }),
            });
          }
        }
      } catch (error) {
        console.error("Failed to load providers:", error);
        toast.error("Failed to load provider configuration");
      } finally {
        setIsLoading(false);
      }
    };
    loadProviders();
  }, []);

  const addProvider = () => {
    const newProvider: LLMProvider = {
      id: Date.now().toString(),
      name: "New Provider",
      type: "custom",
      baseUrl: "",
      apiKey: "",
      model: "",
      enabled: false,
      priority: providers.length + 1,
    };
    setProviders([...providers, newProvider]);
  };

  const updateProvider = (id: string, updates: Partial<LLMProvider>) => {
    setProviders(providers.map(p => p.id === id ? { ...p, ...updates } : p));
  };

  const deleteProvider = (id: string) => {
    setProviders(providers.filter(p => p.id !== id));
    toast.success("Provider deleted");
  };

  const testProvider = async (id: string) => {
    setTestingProvider(id);
    const provider = providers.find(p => p.id === id);
    
    if (!provider) {
      toast.error("Provider not found");
      setTestingProvider(null);
      return;
    }

    try {
      // Send test message to LLM
      const response = await fetch(`${provider.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          "Authorization": `Bearer ${provider.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: provider.model,
          messages: [
            {
              role: "user",
              content: "Hello from Dive Coder to LLM"
            }
          ],
          max_tokens: 100,
          temperature: 0.7
        })
      });

      if (response.ok) {
        const data = await response.json();
        const content = data.choices?.[0]?.message?.content || "No response";
        const tokens = data.usage?.total_tokens || 0;
        
        toast.success(
          <div className="space-y-1">
            <div className="font-semibold">✅ {provider.name} connected!</div>
            <div className="text-sm">Model: {provider.model}</div>
            <div className="text-sm">Response: {content}</div>
            <div className="text-xs text-muted-foreground">Tokens: {tokens}</div>
          </div>,
          { duration: 6000 }
        );
      } else {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.error?.message || response.statusText;
        toast.error(
          <div className="space-y-1">
            <div className="font-semibold">❌ Connection failed</div>
            <div className="text-sm">{provider.name}: {errorMsg}</div>
          </div>,
          { duration: 5000 }
        );
      }
    } catch (error) {
      toast.error(
        <div className="space-y-1">
          <div className="font-semibold">❌ Connection error</div>
          <div className="text-sm">{String(error)}</div>
        </div>,
        { duration: 5000 }
      );
    } finally {
      setTestingProvider(null);
    }
  };

  const saveProviders = async () => {
    try {
      // Save to monitor server
      const response = await fetch(`${import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787'}/v1/providers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ providers }),
      });

      if (response.ok) {
        toast.success("LLM providers saved successfully!");
        
        // Auto-test all enabled providers
        const enabledProviders = providers.filter(p => p.enabled);
        if (enabledProviders.length > 0) {
          toast.info(`Testing ${enabledProviders.length} enabled provider(s)...`);
          
          // Test each provider sequentially
          for (const provider of enabledProviders) {
            await testProvider(provider.id);
            // Small delay between tests
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      } else {
        toast.error("Failed to save providers");
      }
    } catch (error) {
      toast.error(`Save error: ${error}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-3 text-muted-foreground">Loading provider configuration...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">LLM Providers</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Configure AI providers for DiveCoder. Providers are tried in priority order with automatic fallback.
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={addProvider} variant="outline">
            <Plus className="w-4 h-4 mr-2" />
            Add Provider
          </Button>
          <Button onClick={saveProviders}>
            Save Configuration
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {providers.map((provider) => (
          <Card key={provider.id} className="border-border/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <CardTitle className="text-lg">{provider.name}</CardTitle>
                  <div className="flex items-center gap-2">
                    <Label htmlFor={`enabled-${provider.id}`} className="text-sm text-muted-foreground">
                      Enabled
                    </Label>
                    <Switch
                      id={`enabled-${provider.id}`}
                      checked={provider.enabled}
                      onCheckedChange={(checked) => updateProvider(provider.id, { enabled: checked })}
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => testProvider(provider.id)}
                    disabled={testingProvider === provider.id}
                  >
                    {testingProvider === provider.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Check className="w-4 h-4" />
                    )}
                    <span className="ml-2">Test</span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteProvider(provider.id)}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              </div>
              <CardDescription>Priority: {provider.priority}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor={`type-${provider.id}`}>Provider Type</Label>
                  <Select
                    value={provider.type}
                    onValueChange={(value: any) => {
                      const template = PROVIDER_TEMPLATES[value as keyof typeof PROVIDER_TEMPLATES];
                      updateProvider(provider.id, {
                        type: value,
                        name: template.name,
                        baseUrl: template.baseUrl,
                      });
                    }}
                  >
                    <SelectTrigger id={`type-${provider.id}`}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="v98api">V98 API</SelectItem>
                      <SelectItem value="aicoding">AI Coding</SelectItem>
                      <SelectItem value="openai">OpenAI</SelectItem>
                      <SelectItem value="anthropic">Anthropic</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`model-${provider.id}`}>Model</Label>
                  <Select
                    value={provider.model}
                    onValueChange={(value) => updateProvider(provider.id, { model: value })}
                  >
                    <SelectTrigger id={`model-${provider.id}`}>
                      <SelectValue placeholder="Select model" />
                    </SelectTrigger>
                    <SelectContent>
                      {PROVIDER_TEMPLATES[provider.type].models.map((model) => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`baseUrl-${provider.id}`}>Base URL</Label>
                <Input
                  id={`baseUrl-${provider.id}`}
                  value={provider.baseUrl}
                  onChange={(e) => updateProvider(provider.id, { baseUrl: e.target.value })}
                  placeholder="https://api.example.com/v1"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`apiKey-${provider.id}`}>API Key</Label>
                <Input
                  id={`apiKey-${provider.id}`}
                  type="password"
                  value={provider.apiKey}
                  onChange={(e) => updateProvider(provider.id, { apiKey: e.target.value })}
                  placeholder="sk-..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`priority-${provider.id}`}>Priority (lower = higher priority)</Label>
                <Input
                  id={`priority-${provider.id}`}
                  type="number"
                  value={provider.priority}
                  onChange={(e) => updateProvider(provider.id, { priority: parseInt(e.target.value) })}
                  min={1}
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {providers.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-muted-foreground mb-4">No LLM providers configured</p>
            <Button onClick={addProvider}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Provider
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
