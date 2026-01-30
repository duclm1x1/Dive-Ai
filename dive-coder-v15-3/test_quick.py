"""Quick test to identify issues"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.shared/vibe-coder-v13'))

from dive_engine.llm.gateway import UnifiedLLMGateway

async def main():
    print("Quick Test 1: Basic completion")
    gateway = UnifiedLLMGateway()
    
    try:
        response = await gateway.chat_completion(
            messages=[{"role": "user", "content": "Say 'OK'"}],
            model="gpt-4.1-mini",
            max_tokens=10,
        )
        print(f"✅ Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\nQuick Test 2: Streaming")
    try:
        print("Response: ", end="", flush=True)
        async for chunk in gateway.chat_completion_stream(
            messages=[{"role": "user", "content": "Count 1, 2, 3"}],
            model="gpt-4.1-mini",
            max_tokens=20,
        ):
            if chunk["choices"][0]["delta"].get("content"):
                print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
        print("\n✅ Streaming works!")
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
    
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
