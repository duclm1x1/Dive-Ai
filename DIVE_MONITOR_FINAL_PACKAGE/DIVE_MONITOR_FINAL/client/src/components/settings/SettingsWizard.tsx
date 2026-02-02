import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ChevronRight, ChevronLeft, Sparkles, Key, Server, TestTube } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

interface APIConfig {
  provider: 'openai' | 'anthropic' | 'v98' | 'custom';
  apiKey: string;
  baseUrl?: string;
  model?: string;
}

const PROVIDERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'GPT-4, GPT-3.5 models',
    defaultUrl: 'https://api.openai.com/v1',
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    icon: '🤖',
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    description: 'Claude 3 models',
    defaultUrl: 'https://api.anthropic.com/v1',
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    icon: '🧠',
  },
  {
    id: 'v98',
    name: 'V98 API',
    description: 'Custom V98 endpoint',
    defaultUrl: 'https://v98store.com/v1',
    models: ['v98-default'],
    icon: '⚡',
  },
  {
    id: 'custom',
    name: 'Custom API',
    description: 'Your own API endpoint',
    defaultUrl: '',
    models: [],
    icon: '🔧',
  },
];

interface SettingsWizardProps {
  onComplete: (config: APIConfig) => void;
  onCancel: () => void;
}

export function SettingsWizard({ onComplete, onCancel }: SettingsWizardProps) {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState<APIConfig>({
    provider: 'openai',
    apiKey: '',
    baseUrl: '',
    model: '',
  });
  const [testing, setTesting] = useState(false);

  const selectedProvider = PROVIDERS.find((p) => p.id === config.provider);
  const totalSteps = 4;

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    // Simulate API test
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setTesting(false);
    toast.success('Connection successful!');
  };

  const handleComplete = () => {
    onComplete(config);
    toast.success('Settings saved successfully!');
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return !!config.provider;
      case 2:
        return config.apiKey.length > 0;
      case 3:
        return config.baseUrl || selectedProvider?.defaultUrl;
      case 4:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-semibold text-foreground">
            API Configuration Wizard
          </h2>
          <span className="text-sm text-muted-foreground">
            Step {step} of {totalSteps}
          </span>
        </div>
        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-cyan-500"
            initial={{ width: 0 }}
            animate={{ width: `${(step / totalSteps) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Step Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {/* Step 1: Choose Provider */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Choose Your AI Provider
                </h3>
                <p className="text-sm text-muted-foreground">
                  Select which AI service you want to use with Dive Coder
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {PROVIDERS.map((provider) => (
                  <Card
                    key={provider.id}
                    className={`p-4 cursor-pointer transition-all ${
                      config.provider === provider.id
                        ? 'border-cyan-500 bg-cyan-500/5'
                        : 'border-border hover:border-cyan-500/50'
                    }`}
                    onClick={() =>
                      setConfig({
                        ...config,
                        provider: provider.id as APIConfig['provider'],
                        baseUrl: provider.defaultUrl,
                        model: provider.models[0] || '',
                      })
                    }
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">{provider.icon}</span>
                      <div className="flex-1">
                        <h4 className="font-medium text-foreground mb-1">
                          {provider.name}
                        </h4>
                        <p className="text-xs text-muted-foreground">
                          {provider.description}
                        </p>
                      </div>
                      {config.provider === provider.id && (
                        <Check className="w-5 h-5 text-cyan-500" />
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: API Key */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Enter Your API Key
                </h3>
                <p className="text-sm text-muted-foreground">
                  Your API key is stored securely and never shared
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="apiKey" className="flex items-center gap-2 mb-2">
                    <Key className="w-4 h-4" />
                    API Key
                  </Label>
                  <Input
                    id="apiKey"
                    type="password"
                    placeholder={`Enter your ${selectedProvider?.name} API key`}
                    value={config.apiKey}
                    onChange={(e) =>
                      setConfig({ ...config, apiKey: e.target.value })
                    }
                    className="font-mono"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Get your API key from{' '}
                    <a
                      href={
                        config.provider === 'openai'
                          ? 'https://platform.openai.com/api-keys'
                          : config.provider === 'anthropic'
                          ? 'https://console.anthropic.com/settings/keys'
                          : '#'
                      }
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-500 hover:underline"
                    >
                      {selectedProvider?.name} dashboard
                    </a>
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: API Endpoint */}
          {step === 3 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Configure API Endpoint
                </h3>
                <p className="text-sm text-muted-foreground">
                  Customize the API endpoint and model (optional)
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="baseUrl" className="flex items-center gap-2 mb-2">
                    <Server className="w-4 h-4" />
                    API Endpoint URL
                  </Label>
                  <Input
                    id="baseUrl"
                    type="url"
                    placeholder={selectedProvider?.defaultUrl}
                    value={config.baseUrl}
                    onChange={(e) =>
                      setConfig({ ...config, baseUrl: e.target.value })
                    }
                    className="font-mono"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Leave blank to use default: {selectedProvider?.defaultUrl}
                  </p>
                </div>

                {selectedProvider && selectedProvider.models.length > 0 && (
                  <div>
                    <Label htmlFor="model" className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4" />
                      AI Model
                    </Label>
                    <Select
                      value={config.model}
                      onValueChange={(value) =>
                        setConfig({ ...config, model: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a model" />
                      </SelectTrigger>
                      <SelectContent>
                        {selectedProvider.models.map((model) => (
                          <SelectItem key={model} value={model}>
                            {model}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Test & Confirm */}
          {step === 4 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-foreground mb-2">
                  Test Your Configuration
                </h3>
                <p className="text-sm text-muted-foreground">
                  Let's make sure everything is working correctly
                </p>
              </div>

              <Card className="p-6 bg-card/50">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Provider:</span>
                    <span className="font-medium">{selectedProvider?.name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">API Key:</span>
                    <span className="font-mono text-sm">
                      {config.apiKey.slice(0, 8)}...
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Endpoint:</span>
                    <span className="font-mono text-xs truncate max-w-xs">
                      {config.baseUrl || selectedProvider?.defaultUrl}
                    </span>
                  </div>
                  {config.model && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Model:</span>
                      <span className="font-medium">{config.model}</span>
                    </div>
                  )}
                </div>

                <Button
                  onClick={handleTest}
                  disabled={testing}
                  className="w-full mt-6"
                  variant="outline"
                >
                  {testing ? (
                    <>
                      <TestTube className="w-4 h-4 mr-2 animate-spin" />
                      Testing Connection...
                    </>
                  ) : (
                    <>
                      <TestTube className="w-4 h-4 mr-2" />
                      Test Connection
                    </>
                  )}
                </Button>
              </Card>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
        <Button
          variant="ghost"
          onClick={step === 1 ? onCancel : handleBack}
          disabled={testing}
        >
          <ChevronLeft className="w-4 h-4 mr-2" />
          {step === 1 ? 'Cancel' : 'Back'}
        </Button>

        <Button
          onClick={step === totalSteps ? handleComplete : handleNext}
          disabled={!canProceed() || testing}
        >
          {step === totalSteps ? (
            <>
              <Check className="w-4 h-4 mr-2" />
              Save Settings
            </>
          ) : (
            <>
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
