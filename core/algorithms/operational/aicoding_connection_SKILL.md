---
name: AICoding Connection Algorithm
description: Connect to AICoding.io.vn API with OpenAI and Anthropic format support
tags: [connection, api, aicoding, openai, anthropic, dual-format]
---

# AICoding Connection Algorithm

Dual-format connection algorithm for AICoding.io.vn API supporting both OpenAI-compatible and Anthropic-native message formats.

## Overview

The AICoding Connection Algorithm provides flexible access to AICoding.io.vn's Claude AI models through both OpenAI-compatible chat completions and Anthropic's native messages endpoint.

## Features

- ✅ **Dual Format Support**: OpenAI and Anthropic formats
- ✅ **Claude Models**: Sonnet 4.5, Opus 4.5, Haiku 4.5
- ✅ **GPT Models**: GPT-5.1, GPT-5.1-Codex, GPT-5.2, GPT-5.2-Codex
- ✅ **Other Models**: Gemini 3 Pro, GLM-4.6
- ✅ **Health Monitoring**: Real-time health checks (~317ms)

## API Configuration

```python
Base URL: https://aicoding.io.vn
API Key: Environment variable AICODING_API_KEY or passed as parameter

Headers:
{
    "Authorization": "Bearer {api_key}",
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01"  # For Anthropic endpoints
}
```

## Available Models

| Model | ID | Cost Multiplier |
|-------|-----|----------------|
| Claude Sonnet 4.5 | claude-sonnet-4-5-20250929 | 1x |
| Claude Opus 4.5 | claude-opus-4-5-20251001 | 1.5x |
| Claude Haiku 4.5 | claude-haiku-4-5-20251001 | 1x |
| Gemini 3 Pro | gemini-3-pro-preview | 1x |
| GPT-5.1 | gpt-5.1 | 1x |
| GPT-5.1-Codex | gpt-5.1-codex | 1x |
| GPT-5.2 | gpt-5.2 | 1x |
| GPT-5.2-Codex | gpt-5.2-codex | 1x |
| GLM-4.6 | glm-4.6 | 1x |

## Supported Actions

### 1. Connect
Test connection and discover models.

```python
result = aicoding.execute({"action": "connect"})
```

### 2. List Models
Get all available models.

```python
result = aicoding.execute({"action": "list_models"})
```

### 3. Chat (OpenAI Format)
Send OpenAI-compatible chat requests.

```python
result = aicoding.execute({
    "action": "chat",
    "model": "gpt-5.1-codex",
    "messages": [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Write a quicksort in Python"}
    ],
    "temperature": 0.3,
    "max_tokens": 1500
})
```

### 4. Messages (Anthropic Format)
Send Anthropic-native message requests.

```python
result = aicoding.execute({
    "action": "messages",
    "model": "claude-sonnet-4-5-20250929",
    "messages": [
        {"role": "user", "content": "Explain quantum computing"}
    ],
    "temperature": 0.7,
    "max_tokens": 2000
})
```

### 5. Health
Check API health.

```python
result = aicoding.execute({"action": "health"})
# Average: 317ms response time
```

## Usage Examples

### Basic Connection

```python
from core.algorithms.algorithm_manager import AlgorithmManager

manager = AlgorithmManager(auto_scan=True)
aicoding = manager.get_algorithm("AICodingConnection")

# Test connection
result = aicoding.execute({"action": "connect"})
print(f"Available models: {result.data['total_models']}")
```

### OpenAI Format (Standard)

```python
# Best for GPT models
result = aicoding.execute({
    "action": "chat",
    "model": "gpt-5.1-codex",
    "messages": [
        {"role": "user", "content": "Debug this code: ..."}
    ],
    "temperature": 0.3
})

print(result.data['response'])
print(f"Tokens used: {result.data['usage']['total_tokens']}")
```

### Anthropic Format (Native)

```python
# Best for Claude models (more efficient)
result = aicoding.execute({
    "action": "messages",
    "model": "claude-opus-4-5-20251001",
    "messages": [
        {"role": "user", "content": "Write a design doc for..."}
    ],
    "temperature": 0.7,
    "max_tokens": 4000
})

print(result.data['response'])
```

## Format Comparison

| Feature | OpenAI Format | Anthropic Format |
|---------|---------------|------------------|
| Endpoint | /v1/chat/completions | /v1/messages |
| Best For | GPT models | Claude models |
| System Message | In messages array | Separate field |
| Response Key | choices[0].message.content | content[0].text |
| Token Field | usage.total_tokens | usage.input_tokens + output_tokens |

## Best Practices

1. **Choose Right Format**:
   - Use `chat` for GPT models
   - Use `messages` for Claude models (native format, more efficient)

2. **Token Management**:
   - Claude Opus 4.5: multiply tokens by 1.5x
   - Monitor usage with `result.data['usage']`

3. **Temperature Settings**:
   - Code: 0.1-0.3
   - Creative writing: 0.7-0.9
   - General: 0.5-0.7

4. **Error Handling**:
```python
result = aicoding.execute({...})

if result.status == "success":
    # Process response
    response = result.data['response']
elif result.status == "error":
    # Handle error
    print(f"Error: {result.error}")
```

## Performance

- **Health Check**: ~317ms
- **Model Discovery**: <1s
- **Chat Response**: 2-15s (varies by model and tokens)
- **Reliability**: 99.9% uptime

## Integration Examples

### With 3-AI Orchestrator

```python
# Use AICoding for alternative Claude access
orchestrator_config = {
    "primary": {"provider": "aicoding", "model": "claude-opus-4-5-20251001"},
    "reviewer": {"provider": "v98", "model": "gpt-5.1-codex"},
    "consultant": {"provider": "aicoding", "model": "claude-sonnet-4-5-20250929"}
}
```

### Workflow Chain

```python
# Document generation workflow
workflow = [
    {"algorithm": "AICodingConnection", "action": "messages", "model": "claude-sonnet..."},
    {"algorithm": "CodeReviewer"},
    {"algorithm": "DocumentationGenerator"}
]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 500 Server Error | API temporarily unavailable, retry with backoff |
| Model not available | Check model list with `list_models` |
| Token limit exceeded | Reduce max_tokens or split request |
| Health check fails | Verify network connectivity |

## Cost Optimization

```python
# Use appropriate model for task
tasks = {
    "simple_qa": "claude-haiku-4-5-20251001",      # Cheapest
    "code_review": "gpt-5.1-codex",                # Best for code
    "complex_reasoning": "claude-opus-4-5-20251001"  # Most capable (1.5x cost)
}
```

## Related Algorithms

- **V98Connection**: Alternative API with 475+ models
- **ThreeAIOrchestrator**: Multi-model workflow
- **SmartModelRouter**: Automatic model selection

## File Location

`D:\Antigravity\Dive AI\core\algorithms\operational\aicoding_connection.py`

## Version

v1.0 - Initial release with dual-format support
