# Dive Engine LLM Client - Complete Guide

## Overview

The Dive Engine LLM Client provides comprehensive integration with multiple LLM providers, supporting all latest models including GPT-5.2 Pro, Claude 4.5 Opus/Sonnet, Codex, Gemini, and O-series reasoning models.

## Features

✅ **16+ Models Supported:**
- GPT-5 Series: gpt-5.2-pro, gpt-5.2
- GPT-4 Series: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
- Claude 4.5 Series: claude-opus-4.5, claude-sonnet-4.5, claude-3-opus, claude-3-sonnet
- Gemini Series: gemini-2.5-flash, gemini-2.0-flash
- Codex Series: codex-plus, codex
- O-Series: o1, o1-mini, o3-mini

✅ **Multi-Provider Support:**
- V98API (primary, priority 10)
- AICoding API (fallback, priority 5)
- Automatic failover when provider fails

✅ **Advanced Features:**
- Streaming responses
- Token tracking and cost management
- Model registry with capability filtering
- Automatic model selection by tier
- Async/await support

## Quick Start

### Basic Usage

```python
from dive_engine.llm import create_llm_client

# Create client
client = create_llm_client()

# Simple call
response = client.call(
    prompt="Explain quantum computing in simple terms",
    system="You are a helpful teacher",
    tier="tier_fast",
)

print(response)
```

### Async Usage

```python
import asyncio
from dive_engine.llm import create_llm_client

async def main():
    client = create_llm_client()
    
    response = await client.call_async(
        prompt="Write a Python function to sort a list",
        tier="tier_code",
    )
    
    print(response)

asyncio.run(main())
```

### Streaming

```python
import asyncio
from dive_engine.llm import create_llm_client

async def stream_example():
    client = create_llm_client()
    
    async for chunk in client.stream(
        prompt="Tell me a story about AI",
        tier="tier_think",
    ):
        print(chunk, end="", flush=True)

asyncio.run(stream_example())
```

## Model Registry

### List All Models

```python
from dive_engine.llm import ModelRegistry

registry = ModelRegistry()

# List all models
all_models = registry.list_models()
print(f"Total models: {len(all_models)}")

# List reasoning models
reasoning_models = registry.list_models(capability="reasoning")
print(f"Reasoning models: {reasoning_models}")

# List coding models
coding_models = registry.list_models(capability="coding")
print(f"Coding models: {coding_models}")
```

### Get Model Info

```python
from dive_engine.llm import ModelRegistry

registry = ModelRegistry()

# Get info about a specific model
info = registry.get_model_info("gpt-5.2-pro")
print(f"Model: {info['tier']}")
print(f"Capabilities: {info['capabilities']}")
```

### Model Selection by Tier

```python
from dive_engine.llm import ModelRegistry

registry = ModelRegistry()

# Get best model for a tier
model = registry.get_model_for_tier("tier_reasoning")
print(f"Best reasoning model: {model}")  # gpt-5.2

model = registry.get_model_for_tier("tier_extended_thinking")
print(f"Best extended thinking model: {model}")  # claude-opus-4.5
```

## Tiers and Models

| Tier | Model | Use Case |
|------|-------|----------|
| `tier_fast` | gpt-4.1-mini | Simple tasks, quick responses |
| `tier_think` | gpt-4.1 | General reasoning, analysis |
| `tier_code` | codex | Code generation, debugging |
| `tier_reasoning` | gpt-5.2 | Complex reasoning, thinking |
| `tier_extended_thinking` | claude-opus-4.5 | Deep analysis, extended reasoning |
| `tier_monitor` | gpt-4.1-mini | Quality monitoring, validation |

## Model Capabilities

### Reasoning Models
- gpt-5.2-pro, gpt-5.2
- claude-opus-4.5, claude-sonnet-4.5, claude-3-opus
- o1, o1-mini, o3-mini

### Coding Models
- gpt-5.2-pro, gpt-4.1
- claude-sonnet-4.5
- codex-plus, codex

### Thinking Models (Extended Reasoning)
- gpt-5.2-pro, gpt-5.2
- claude-opus-4.5
- o1, o1-mini, o3-mini

### Fast Models
- gpt-4.1-mini, gpt-4.1-nano
- gemini-2.5-flash, gemini-2.0-flash
- o1-mini, o3-mini

## Advanced Usage

### Custom API Keys

```python
from dive_engine.llm import create_llm_client

client = create_llm_client(
    v98api_key="your-v98-key",
    aicoding_key="your-aicoding-key",
)
```

### Specify Model Directly

```python
client = create_llm_client()

# Use specific model
response = client.call(
    prompt="Analyze this code for security issues",
    model="claude-opus-4.5",
    max_tokens=10000,
)
```

### Temperature Control

```python
client = create_llm_client()

# Creative writing (high temperature)
response = client.call(
    prompt="Write a creative story",
    tier="tier_think",
    temperature=0.9,
)

# Precise reasoning (low temperature)
response = client.call(
    prompt="Solve this math problem",
    tier="tier_reasoning",
    temperature=0.1,
)
```

### Usage Statistics

```python
client = create_llm_client()

# Make some calls
client.call("Test 1", tier="tier_fast")
client.call("Test 2", tier="tier_think")

# Get stats
stats = client.get_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total calls: {stats['call_count']}")
print(f"Providers: {stats['providers']}")
print(f"Available models: {stats['available_models']}")
```

## Provider Configuration

### Default Providers

**V98API** (Priority 10):
- Base URL: https://v98store.com/v1
- Models: All 16+ models
- Features: Full support for all tiers

**AICoding API** (Priority 5):
- Base URL: https://aicoding.io.vn/v1
- Models: GPT-4 series, Codex
- Features: Fallback provider

### Failover Mechanism

The client automatically tries providers in priority order:

1. Try V98API (priority 10)
2. If fails, try AICoding API (priority 5)
3. If all fail, raise error

```python
# Failover happens automatically
client = create_llm_client()

# This will try V98API first, then AICoding if it fails
response = client.call("Test prompt", tier="tier_fast")
```

## Error Handling

```python
from dive_engine.llm import create_llm_client

client = create_llm_client()

try:
    response = client.call(
        prompt="Test prompt",
        tier="tier_fast",
    )
    print(response)

except RuntimeError as e:
    print(f"All providers failed: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

### Run LLM Client Tests

```bash
cd /path/to/dive_coder_v14/.shared/vibe-coder-v13
python3 dive_engine/llm/test_real_api.py
```

### Test Output

```
================================================================================
DIVE ENGINE LLM CLIENT - COMPREHENSIVE TEST SUITE
================================================================================

TEST 1: Model Registry
✓ Total models available: 16
✓ Reasoning models: 8
✓ Coding models: 5
✅ Model Registry Test PASSED

TEST 2: Simple Synchronous Call
✓ Response: Hello from Dive Engine!
✅ Simple Call Test PASSED

TEST 3: Asynchronous Call
✓ Response: 1 2 3 4 5
✅ Async Call Test PASSED

TEST 4: Streaming Response
✓ Streaming response: [haiku about coding]
✅ Streaming Test PASSED

TEST 5: Model Selection
✓ Testing gpt-4.1-mini, gpt-4.1, codex
✅ Model Selection Test PASSED

TEST 6: Reasoning Models
✓ Response: [step-by-step reasoning]
✅ Reasoning Models Test PASSED

TEST 7: Provider Failover
✓ Failover mechanism working correctly
✅ Failover Test PASSED

🎉 ALL TESTS PASSED! 🎉
```

## Integration with Dive Engine

### In Orchestrator

```python
from dive_engine import DiveEngineOrchestrator

orchestrator = DiveEngineOrchestrator()

result = orchestrator.run(
    prompt="Fix the bug in auth.py",
    mode="debug",
)

# LLM client is used internally for:
# - Routing decisions
# - Cognitive phase execution
# - Quality monitoring
# - Faithfulness checking
```

### In Custom Code

```python
from dive_engine.llm import create_llm_client

client = create_llm_client()

# Use for custom reasoning tasks
response = client.call(
    prompt="Analyze this security vulnerability",
    tier="tier_reasoning",
    max_tokens=5000,
)
```

## Best Practices

### 1. Choose the Right Tier

- Use `tier_fast` for simple, quick tasks
- Use `tier_think` for general reasoning
- Use `tier_code` for code-related tasks
- Use `tier_reasoning` for complex reasoning
- Use `tier_extended_thinking` for deep analysis

### 2. Set Appropriate Limits

```python
# For quick responses
client.call(prompt="...", tier="tier_fast", max_tokens=500)

# For detailed analysis
client.call(prompt="...", tier="tier_reasoning", max_tokens=10000)
```

### 3. Use Streaming for Long Responses

```python
# Better UX for long responses
async for chunk in client.stream(prompt="...", tier="tier_think"):
    print(chunk, end="", flush=True)
```

### 4. Monitor Token Usage

```python
# Check stats periodically
stats = client.get_stats()
if stats['total_tokens'] > 1000000:
    print("Warning: High token usage")
```

## Troubleshooting

### Issue: ImportError for openai package

**Solution:**
```bash
pip install openai
```

### Issue: All providers failed

**Possible causes:**
- Invalid API keys
- Network issues
- Provider downtime

**Solution:**
- Check API keys are correct
- Verify network connectivity
- Try again later

### Issue: Model not found

**Solution:**
- Check model ID is correct
- Use `ModelRegistry.list_models()` to see available models
- Ensure provider supports the model

## Roadmap

### Planned Features

- [ ] Automatic model refresh from providers
- [ ] Cost tracking and budgeting
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Metrics collection (Prometheus)
- [ ] Structured logging
- [ ] Model performance benchmarking

## Support

For issues or questions:
- Check the comprehensive review document
- Run the test suite to verify setup
- Review error messages for specific guidance

## License

Part of Dive Coder v14 - Dive Engine V2
