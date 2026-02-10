"""
Streaming Support - SSE streaming for V98 responses

Enables real-time token-by-token response streaming
for better UX in chat interfaces.
"""

import asyncio
import json
import time
import os
from typing import AsyncGenerator, Dict, Any, List
import aiohttp

from .connections import V98Model, CLAUDE_OPUS_46_THINKING, CLAUDE_SONNET_45


class V98StreamClient:
    """Async streaming client for V98"""
    
    BASE_URL = "https://v98store.com/v1"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("V98_API_KEY", "")
    
    async def stream_chat(self,
                          messages: List[Dict],
                          model: V98Model = None,
                          **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream chat completion
        
        Yields chunks of content as they arrive.
        """
        model = model or CLAUDE_OPUS_46_THINKING
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", model.max_tokens),
            "temperature": kwargs.get("temperature", model.temperature),
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error = await response.text()
                    yield f"Error: {error}"
                    return
                
                async for line in response.content:
                    line = line.decode().strip()
                    
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        data = line[6:]
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue


async def stream_response(
    prompt: str,
    system: str = None,
    model: V98Model = None,
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    Quick streaming helper
    
    Usage:
        async for chunk in stream_response("Hello"):
            print(chunk, end="", flush=True)
    """
    client = V98StreamClient()
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    async for chunk in client.stream_chat(messages, model=model, **kwargs):
        yield chunk


# FastAPI SSE endpoint helper
def create_sse_response(content_generator):
    """
    Create SSE response for FastAPI
    
    Usage:
        @app.get("/stream")
        async def stream():
            async def generate():
                async for chunk in stream_response("Hello"):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(generate(), media_type="text/event-stream")
    """
    async def generate():
        async for chunk in content_generator:
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return generate()


class StreamBuffer:
    """Buffer for collecting streamed content"""
    
    def __init__(self):
        self.chunks: List[str] = []
        self.start_time: float = 0
        self.first_token_time: float = 0
        self.end_time: float = 0
    
    def start(self):
        """Mark stream start"""
        self.start_time = time.time()
        self.chunks = []
    
    def add(self, chunk: str):
        """Add chunk to buffer"""
        if not self.first_token_time and chunk:
            self.first_token_time = time.time()
        self.chunks.append(chunk)
    
    def end(self):
        """Mark stream end"""
        self.end_time = time.time()
    
    @property
    def content(self) -> str:
        """Get full content"""
        return "".join(self.chunks)
    
    @property
    def ttft_ms(self) -> float:
        """Time to first token in ms"""
        if self.first_token_time and self.start_time:
            return (self.first_token_time - self.start_time) * 1000
        return 0
    
    @property
    def total_time_ms(self) -> float:
        """Total streaming time in ms"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0
    
    @property
    def stats(self) -> Dict:
        """Get streaming stats"""
        return {
            "chunks": len(self.chunks),
            "chars": len(self.content),
            "ttft_ms": self.ttft_ms,
            "total_ms": self.total_time_ms
        }
