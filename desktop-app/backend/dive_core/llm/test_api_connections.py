#!/usr/bin/env python3
"""
API Connection Test for Latest Models
Tests connections to V98, Aicoding, OpenAI, Anthropic, Google
"""

import asyncio
import os
from llm_client_three_mode import LLMClientThreeMode, LLMRequest, CommunicationMode

# API Configuration
API_CONFIGS = {
    "v98": {
        "base_url": "https://v98store.com/v1",
        "api_key": "YOUR_V98_API_KEY_HERE",
        "models": [
            "claude-opus-4.5",
            "claude-sonnet-4.5",
            "claude-haiku-4.6",
            "gemini-3.0-pro",
            "gemini-3.0-flash",
            "gpt-5.1",
            "gpt-5.1-turbo",
            "qwen-3.0",
            "qwen-3.0-turbo",
            "llama-4",
            "llama-4-turbo"
        ]
    },
    "aicoding": {
        "base_url": "https://aicoding.io.vn/v1",
        "api_key": "YOUR_AICODING_API_KEY_HERECJCk",
        "models": [
            "claude-opus-4.5",
            "claude-sonnet-4.5",
            "gemini-3.0-pro",
            "gpt-5.1"
        ]
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "models": [
            "gpt-5.1",
            "gpt-5.1-turbo",
            "gpt-5.0",
            "o1",
            "o1-mini"
        ]
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "models": [
            "claude-opus-4.5",
            "claude-sonnet-4.5",
            "claude-haiku-4.6"
        ]
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
        "models": [
            "gemini-3.0-pro",
            "gemini-3.0-flash",
            "gemini-3.0-ultra"
        ]
    }
}

async def test_connection(provider, config, model):
    """Test connection to a specific model"""
    print(f"\n{'='*60}")
    print(f"Testing: {provider} / {model}")
    print(f"{'='*60}")
    
    try:
        client = LLMClientThreeMode(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )
        
        request = LLMRequest(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'Connection successful!' in one sentence."}
            ],
            mode=CommunicationMode.HUMAN_AI,
            max_tokens=50,
            temperature=0.7
        )
        
        response = await client.chat_completion(request)
        
        print(f"✅ SUCCESS!")
        print(f"   Response: {response.content[:100]}")
        print(f"   Latency: {response.latency_ms:.2f}ms")
        print(f"   Tokens: {response.tokens_used}")
        
        await client.close()
        
        return {
            "provider": provider,
            "model": model,
            "status": "success",
            "latency_ms": response.latency_ms,
            'tokens': response.tokens_used
        }
        
    except Exception as e:
        print(f"❌ FAILED!")
        print(f"   Error: {str(e)[:200]}")
        
        return {
            "provider": provider,
            "model": model,
            "status": "failed",
            "error": str(e)[:200]
        }

async def test_all_connections():
    """Test all API connections"""
    print("\n" + "="*60)
    print("API CONNECTION TEST - LATEST MODELS")
    print("="*60)
    
    results = []
    
    for provider, config in API_CONFIGS.items():
        if not config["api_key"]:
            print(f"\n⚠️  Skipping {provider} (no API key)")
            continue
        
        print(f"\n{'='*60}")
        print(f"Provider: {provider.upper()}")
        print(f"Base URL: {config['base_url']}")
        print(f"Models: {len(config['models'])}")
        print(f"{'='*60}")
        
        for model in config["models"]:
            result = await test_connection(provider, config, model)
            results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(1)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    
    print(f"\nTotal tests: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        print(f"\n{'='*60}")
        print("SUCCESSFUL CONNECTIONS")
        print(f"{'='*60}")
        for r in successful:
            print(f"✅ {r['provider']:15} | {r['model']:30} | {r['latency_ms']:6.2f}ms | {r['tokens']:4} tokens")
    
    if failed:
        print(f"\n{'='*60}")
        print("FAILED CONNECTIONS")
        print(f"{'='*60}")
        for r in failed:
            print(f"❌ {r['provider']:15} | {r['model']:30}")
            print(f"   Error: {r['error']}")
    
    # Save results
    import json
    with open("/home/ubuntu/Dive-Ai/llm_client/connection_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Results saved to: connection_test_results.json")
    print(f"{'='*60}\n")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_connections())
