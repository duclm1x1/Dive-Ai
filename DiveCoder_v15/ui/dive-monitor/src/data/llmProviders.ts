// LLM Provider Configuration

export interface LLMProvider {
  id: string;
  name: string;
  baseUrl: string;
  guideUrl?: string;
  isCustom?: boolean;
}

export interface LLMModel {
  id: string;
  name: string;
  description?: string;
}

export const LLM_PROVIDERS: LLMProvider[] = [
  {
    id: 'v98store',
    name: 'V98 API',
    baseUrl: 'https://v98store.com/v1',
    guideUrl: 'https://v98store.com/guide/claude-code',
  },
  {
    id: 'aicoding',
    name: 'AI Coding',
    baseUrl: 'https://aicoding.io.vn',
  },
  {
    id: 'custom',
    name: 'Custom Provider',
    baseUrl: '',
    isCustom: true,
  },
];

export interface LLMConfig {
  providerId: string;
  modelId: string;
  apiKey: string;
  customBaseUrl?: string;
}

export const DEFAULT_LLM_CONFIG: LLMConfig = {
  providerId: 'v98store',
  modelId: '',
  apiKey: '',
  customBaseUrl: '',
};
