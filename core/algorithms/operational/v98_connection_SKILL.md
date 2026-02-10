---
name: V98 Connection Algorithm
description: Comprehensive connection to V98Store API supporting 475+ models with health checks and OpenAI-compatible endpoints
tags: [connection, api, v98, all-models, openai-compatible]
---

# V98 Connection Algorithm

Comprehensive connection algorithm for V98Store API providing access to 475+ AI models across multiple providers.

## Overview

The V98 Connection Algorithm provides a unified interface to connect to V98Store's API gateway, supporting Claude, GPT, Gemini, GLM, O-series, and Codex models through OpenAI-compatible endpoints.

## Features

- ✅ **475+ Models**: Auto-discovery and categorization
- ✅ **Model Categories**: Claude (21), GPT (100), Gemini (31), GLM (16), O-series (23), Codex (1)
- ✅ **Health Monitoring**: Real-time API health checks
- ✅ **OpenAI Compatible**: Standard chat completions endpoint
- ✅ **Model Filtering**: Search and filter by model name patterns

## API Configuration

```python
Base URL: https://v98store.com/v1
API Key: Environment variable V98_API_KEY or passed as parameter

Headers:
{
    "Authorization": "Bearer {api_key}",
    "Content-Type": "application/json"
}
```

## Supported Actions

### 1. Connect
Test connection and discover available models.

```python
result = v98_algo.execute({"action": "connect"})
# Returns: 475 models with categorization
```

### 2. List Models
List all models with optional filtering.

```python
result = v98_algo.execute({
    "action": "list_models",
    "filter_by": "claude"  # Optional filter
})
# Returns: Filtered model list
```

### 3. Chat
Send OpenAI-compatible chat completion requests.

```python
result = v98_algo.execute({
    "action": "chat",
    "model": "claude-opus-4-6",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Your prompt here"}
    ],
    "temperature": 0.7,
    "max_tokens": 2000
})
```

### 4. Health
Check API health and response times.

```python
result = v98_algo.execute({"action": "health"})
# Returns: Health status and response time
```

## Usage Examples

### Basic Connection

```python
from core.algorithms.algorithm_manager import AlgorithmManager

manager = AlgorithmManager(auto_scan=True)
v98 = manager.get_algorithm("V98Connection")

# Test connection
result = v98.execute({"action": "connect"})
print(f"Total models: {result.data['total_models']}")
print(f"Categories: {result.data['categories']}")
```

### List Specific Models

```python
# Find all Codex models
result = v98.execute({
    "action": "list_models",
    "filter_by": "codex"
})

print(f"Codex models: {result.data['models']}")
```

### Chat Completion

```python
# Use GPT-5.1-Codex for code generation
result = v98.execute({
    "action": "chat",
    "model": "gpt-5.1-codex",
    "messages": [
        {"role": "user", "content": "Write a binary search function in Python"}
    ],
    "temperature": 0.3,
    "max_tokens": 1000
})

print(result.data['response'])
```

## Model Categories

| Category | Count | Key Models |
|----------|-------|------------|
| Claude | 21 | claude-opus-4-6, claude-sonnet-3-5 |
| GPT | 100 | gpt-4o, gpt-5.1-codex |
| Gemini | 31 | gemini-pro, gemini-1.5-pro |
| GLM | 16 | glm-4.6, glm-4.6v |
| O-series | 23 | o1-preview, o3-mini |
| Codex | 1 | gpt-5.1-codex |

## Best Practices

1. **Use Environment Variables**: Store API key in `V98_API_KEY`
2. **Cache Model Lists**: Call `connect` once and cache results
3. **Monitor Health**: Periodic health checks for production systems
4. **Rate Limiting**: Implement token bucket for high-volume usage
5. **Error Handling**: Always check `result.status` before using data

## Error Handling

```python
result = v98.execute({"action": "chat", "model": "gpt-4o", ...})

if result.status == "success":
    print(result.data['response'])
elif result.status == "error":
    print(f"Error: {result.error}")
```

## Performance

- **Connection Test**: ~884ms average
- **Model Discovery**: ~1s for 475 models
- **Chat Response**: 2-10s depending on model and tokens
- **Health Check**: <1s

## Integration

### 3-AI Orchestrator

```python
# Used by ThreeAIOrchestrator for:
# - claude-opus-4-6 (Primary Lead)
# - gpt-5.1-codex (Code Reviewer)
# - glm-4.6v (Consultant)
```

### Workflow Integration

```python
# Add to algorithm chain
workflow = [
    "V98Connection",
    "CodeGenerator",
    "TestWriter"
]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection timeout | Check network, verify API key |
| 401 Unauthorized | Validate V98_API_KEY environment variable |
| Model not found | Run `list_models` to see available options |
| Rate limit hit | Implement exponential backoff |

## Related Algorithms

- **AICodingConnection**: Alternative API with Anthropic format
- **ThreeAIOrchestrator**: Multi-model orchestration
- **SmartModelRouter**: Intelligent model selection

## File Location

`D:\Antigravity\Dive AI\core\algorithms\operational\v98_connection.py`

## Version

v2.0 - Enhanced with full model support and categorization
