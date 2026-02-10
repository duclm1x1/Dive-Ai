"""
Discord Channel - Bot integration

Uses discord.py to handle messages.
"""

import asyncio
from typing import Optional
import os

try:
    import discord
    from discord.ext import commands
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

from ..llm.connections import get_manager


class DiscordChannel:
    """
    Discord bot channel
    
    Commands:
    - !ask [message] - Ask Claude
    - !model - Show model info
    - !help - Show help
    """
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("DISCORD_BOT_TOKEN", "")
        self.manager = get_manager()
        self.bot = None
    
    def is_available(self) -> bool:
        """Check availability"""
        return AVAILABLE and bool(self.token)
    
    def setup_bot(self):
        """Setup Discord bot"""
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        @self.bot.event
        async def on_ready():
            print(f"Discord bot ready: {self.bot.user}")
        
        @self.bot.command(name='ask')
        async def ask(ctx, *, message: str):
            """Ask Claude"""
            async with ctx.typing():
                response = self.manager.chat(message)
                
                if response.success:
                    # Split long responses
                    content = response.content
                    if len(content) > 2000:
                        chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
                        for chunk in chunks:
                            await ctx.send(chunk)
                    else:
                        await ctx.send(content)
                else:
                    await ctx.send(f"Error: {response.error}")
        
        @self.bot.command(name='model')
        async def model(ctx):
            """Show model info"""
            status = self.manager.status()
            await ctx.send(
                f"🦞 **Dive AI V29.4**\n"
                f"Primary: {status.get('primary', 'Unknown')}\n"
                f"Models: {status.get('models', 0)}"
            )
    
    def start(self):
        """Start bot"""
        if not self.is_available():
            print("Discord not available")
            return
        
        self.setup_bot()
        self.bot.run(self.token)
    
    def stop(self):
        """Stop bot"""
        if self.bot:
            asyncio.create_task(self.bot.close())


# Singleton
_channel = None

def get_discord_channel() -> DiscordChannel:
    """Get Discord channel"""
    global _channel
    if _channel is None:
        _channel = DiscordChannel()
    return _channel
