"""
🤖 DISCORD BOT INTEGRATION
Report agent status and receive tasks via Discord
"""

import os
import sys
import json
import asyncio
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

# Discord.py will be imported if available
DISCORD_AVAILABLE = False
try:
    import discord
    from discord.ext import commands, tasks
    DISCORD_AVAILABLE = True
except ImportError:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


@dataclass
class BotConfig:
    """Discord bot configuration"""
    token: str
    command_prefix: str = "!"
    status_channel_id: Optional[int] = None
    task_channel_id: Optional[int] = None
    daily_report_hour: int = 8  # 8 AM
    enable_live_feed: bool = True


class DiveAIDiscordBot:
    """
    🤖 Discord Bot for Dive AI
    - Report agent status
    - Receive tasks via chat
    - Daily 24h plan notifications
    - Real-time agent activity feed
    """
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.coordinator = None
        self.memory = None
        self.running = False
        
        if not DISCORD_AVAILABLE:
            print("⚠️  Discord.py not installed. Run: pip install discord.py")
            return
        
        # Create bot
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(
            command_prefix=config.command_prefix,
            intents=intents,
            description="Dive AI Multi-Agent Coordinator"
        )
        
        self._setup_commands()
        self._setup_events()
    
    def _setup_commands(self):
        """Setup bot commands"""
        
        @self.bot.command(name="status")
        async def status(ctx):
            """Get coordinator status"""
            if self.coordinator:
                result = self.coordinator.execute({"action": "get_status"})
                embed = self._create_status_embed(result.data)
                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ Coordinator not initialized")
        
        @self.bot.command(name="agents")
        async def agents(ctx):
            """Get agent distribution"""
            if self.coordinator:
                result = self.coordinator.execute({"action": "spawn_agents"})
                embed = self._create_agents_embed(result.data)
                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ Coordinator not initialized")
        
        @self.bot.command(name="task")
        async def task(ctx, priority: int = 3, *, description: str):
            """Drop a task: !task 5 Create a REST API"""
            if self.coordinator:
                result = self.coordinator.execute({
                    "action": "autonomous_execute",
                    "task": description,
                    "priority": priority
                })
                embed = self._create_task_embed(description, priority, result.data)
                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ Coordinator not initialized")
        
        @self.bot.command(name="plan")
        async def plan(ctx):
            """Generate 24-hour plan"""
            if self.coordinator:
                result = self.coordinator.execute({"action": "generate_24h_plan"})
                embed = self._create_plan_embed(result.data)
                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ Coordinator not initialized")
        
        @self.bot.command(name="cost")
        async def cost(ctx):
            """Get cost summary"""
            if self.memory:
                stats = self.memory.get_dashboard_stats()
                embed = discord.Embed(
                    title="💰 Cost Summary",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Total Cost", value=f"${stats.get('total_cost', 0):.4f}", inline=True)
                embed.add_field(name="Total Tokens", value=f"{stats.get('total_tokens', 0):,}", inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("⚠️ Memory not initialized")
        
        @self.bot.command(name="help_dive")
        async def help_dive(ctx):
            """Show Dive AI commands"""
            embed = discord.Embed(
                title="🤖 Dive AI Commands",
                description="Multi-Agent Coordinator Bot",
                color=discord.Color.blue()
            )
            embed.add_field(name="!status", value="Get coordinator status", inline=False)
            embed.add_field(name="!agents", value="View 512 agent distribution", inline=False)
            embed.add_field(name="!task <priority> <description>", value="Drop a task (priority 1-5)", inline=False)
            embed.add_field(name="!plan", value="Generate 24-hour autonomous plan", inline=False)
            embed.add_field(name="!cost", value="View cost summary", inline=False)
            await ctx.send(embed=embed)
    
    def _setup_events(self):
        """Setup bot events"""
        
        @self.bot.event
        async def on_ready():
            print(f"✅ Discord Bot ready: {self.bot.user}")
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="512 Dive Coder AIs"
                )
            )
            
            # Start daily report task if configured
            if self.config.status_channel_id:
                self.daily_report.start()
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            
            # Process commands
            await self.bot.process_commands(message)
    
    @tasks.loop(hours=24)
    async def daily_report(self):
        """Send daily 24h plan report"""
        if self.config.status_channel_id:
            channel = self.bot.get_channel(self.config.status_channel_id)
            if channel and self.coordinator:
                result = self.coordinator.execute({"action": "generate_24h_plan"})
                embed = self._create_plan_embed(result.data)
                embed.title = "📅 Daily Autonomous Plan"
                await channel.send(embed=embed)
    
    def _create_status_embed(self, data: Dict) -> 'discord.Embed':
        """Create status embed"""
        embed = discord.Embed(
            title="🤖 Coordinator Status",
            color=discord.Color.green() if data.get("coordinator") == "online" else discord.Color.red()
        )
        embed.add_field(name="Status", value=data.get("coordinator", "unknown").upper(), inline=True)
        embed.add_field(name="Total Agents", value=str(data.get("total_agents", 0)), inline=True)
        embed.add_field(name="Idle", value=str(data.get("agents_idle", 0)), inline=True)
        embed.add_field(name="Busy", value=str(data.get("agents_busy", 0)), inline=True)
        embed.add_field(name="Tasks Pending", value=str(data.get("tasks_pending", 0)), inline=True)
        embed.add_field(name="Tasks Completed", value=str(data.get("tasks_completed", 0)), inline=True)
        embed.timestamp = datetime.now()
        return embed
    
    def _create_agents_embed(self, data: Dict) -> 'discord.Embed':
        """Create agents embed"""
        embed = discord.Embed(
            title="👥 Agent Distribution",
            description=f"Total: {data.get('total_agents', 0)} agents",
            color=discord.Color.blue()
        )
        if "distribution" in data:
            for role, count in data["distribution"].items():
                emoji = {"find": "🔍", "build": "🛠️", "track": "📊", "watch": "👁️", "create": "✍️"}.get(role, "🤖")
                embed.add_field(name=f"{emoji} {role.title()}", value=str(count), inline=True)
        embed.timestamp = datetime.now()
        return embed
    
    def _create_task_embed(self, description: str, priority: int, result: Dict) -> 'discord.Embed':
        """Create task embed"""
        embed = discord.Embed(
            title="🎯 Task Received",
            description=description[:200] + "..." if len(description) > 200 else description,
            color=discord.Color.orange()
        )
        embed.add_field(name="Priority", value=f"P{priority}", inline=True)
        embed.add_field(name="Mode", value=result.get("mode", "unknown"), inline=True)
        if "execution" in result:
            embed.add_field(name="Assigned Agents", value=str(result["execution"].get("assigned_agents", 0)), inline=True)
        embed.add_field(name="Status", value="✅ Executing autonomously", inline=False)
        embed.timestamp = datetime.now()
        return embed
    
    def _create_plan_embed(self, data: Dict) -> 'discord.Embed':
        """Create plan embed"""
        embed = discord.Embed(
            title="📅 24-Hour Plan",
            description=f"Date: {data.get('plan_date', 'Today')}",
            color=discord.Color.purple()
        )
        
        if "timeline" in data:
            for time_slot, details in list(data["timeline"].items())[:5]:  # First 5 slots
                if isinstance(details, dict):
                    embed.add_field(
                        name=f"⏰ {time_slot}",
                        value=f"{details.get('activity', 'Scheduled')}\n👥 {details.get('agents_allocated', 0)} agents",
                        inline=False
                    )
        
        if "expected_outcomes" in data:
            outcomes = data["expected_outcomes"][:3]  # First 3 outcomes
            embed.add_field(name="📋 Expected Outcomes", value="\n".join(f"✓ {o}" for o in outcomes), inline=False)
        
        embed.timestamp = datetime.now()
        return embed
    
    async def send_live_update(self, channel_id: int, agent_id: int, message: str):
        """Send live agent update"""
        if not DISCORD_AVAILABLE:
            return
        
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(f"🤖 **Agent-{agent_id:03d}**: {message}")
    
    def set_coordinator(self, coordinator):
        """Set coordinator reference"""
        self.coordinator = coordinator
    
    def set_memory(self, memory):
        """Set memory reference"""
        self.memory = memory
    
    def run(self):
        """Run the bot"""
        if not DISCORD_AVAILABLE:
            print("⚠️ Cannot run: Discord.py not installed")
            return
        
        self.running = True
        self.bot.run(self.config.token)
    
    def run_async(self):
        """Run bot in background thread"""
        if not DISCORD_AVAILABLE:
            print("⚠️ Cannot run: Discord.py not installed")
            return
        
        def runner():
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.run()
        
        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        return thread


# ═══════════════════════════════════════════════════════════════════════
# TELEGRAM BOT (Alternative)
# ═══════════════════════════════════════════════════════════════════════

TELEGRAM_AVAILABLE = False
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    pass


class DiveAITelegramBot:
    """
    📱 Telegram Bot for Dive AI
    Alternative to Discord for mobile-first users
    """
    
    def __init__(self, token: str):
        self.token = token
        self.coordinator = None
        self.memory = None
        
        if not TELEGRAM_AVAILABLE:
            print("⚠️ python-telegram-bot not installed. Run: pip install python-telegram-bot")
            return
        
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command handlers"""
        self.app.add_handler(CommandHandler("start", self._start))
        self.app.add_handler(CommandHandler("status", self._status))
        self.app.add_handler(CommandHandler("agents", self._agents))
        self.app.add_handler(CommandHandler("task", self._task))
        self.app.add_handler(CommandHandler("plan", self._plan))
    
    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        await update.message.reply_text(
            "🤖 *Dive AI Multi-Agent Coordinator*\n\n"
            "Commands:\n"
            "/status - Coordinator status\n"
            "/agents - Agent distribution\n"
            "/task <priority> <description> - Drop task\n"
            "/plan - Generate 24h plan",
            parse_mode="Markdown"
        )
    
    async def _status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status command"""
        if self.coordinator:
            result = self.coordinator.execute({"action": "get_status"})
            data = result.data
            msg = (
                f"🤖 *Coordinator Status*\n\n"
                f"Status: {data.get('coordinator', 'unknown').upper()}\n"
                f"Total Agents: {data.get('total_agents', 0)}\n"
                f"Idle: {data.get('agents_idle', 0)}\n"
                f"Busy: {data.get('agents_busy', 0)}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Coordinator not initialized")
    
    async def _agents(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Agents command"""
        if self.coordinator:
            result = self.coordinator.execute({"action": "spawn_agents"})
            data = result.data
            msg = f"👥 *Agent Distribution*\nTotal: {data.get('total_agents', 0)}\n\n"
            if "distribution" in data:
                for role, count in data["distribution"].items():
                    emoji = {"find": "🔍", "build": "🛠️", "track": "📊", "watch": "👁️", "create": "✍️"}.get(role, "🤖")
                    msg += f"{emoji} {role.title()}: {count}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Coordinator not initialized")
    
    async def _task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Task command"""
        if not context.args:
            await update.message.reply_text("Usage: /task <priority> <description>")
            return
        
        try:
            priority = int(context.args[0])
            description = " ".join(context.args[1:])
        except:
            priority = 3
            description = " ".join(context.args)
        
        if self.coordinator:
            result = self.coordinator.execute({
                "action": "autonomous_execute",
                "task": description,
                "priority": priority
            })
            msg = (
                f"🎯 *Task Received*\n\n"
                f"Priority: P{priority}\n"
                f"Description: {description[:100]}...\n\n"
                f"✅ Executing autonomously"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Coordinator not initialized")
    
    async def _plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Plan command"""
        if self.coordinator:
            result = self.coordinator.execute({"action": "generate_24h_plan"})
            data = result.data
            msg = f"📅 *24-Hour Plan*\nDate: {data.get('plan_date', 'Today')}\n\n"
            
            if "timeline" in data:
                for time_slot, details in list(data["timeline"].items())[:4]:
                    if isinstance(details, dict):
                        msg += f"⏰ {time_slot}\n   {details.get('activity', '')}\n"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Coordinator not initialized")
    
    def set_coordinator(self, coordinator):
        """Set coordinator reference"""
        self.coordinator = coordinator
    
    def set_memory(self, memory):
        """Set memory reference"""
        self.memory = memory
    
    def run(self):
        """Run the bot"""
        if not TELEGRAM_AVAILABLE:
            print("⚠️ Cannot run: python-telegram-bot not installed")
            return
        self.app.run_polling()


def create_discord_bot(token: str) -> DiveAIDiscordBot:
    """Create Discord bot"""
    config = BotConfig(token=token)
    return DiveAIDiscordBot(config)


def create_telegram_bot(token: str) -> DiveAITelegramBot:
    """Create Telegram bot"""
    return DiveAITelegramBot(token)


if __name__ == "__main__":
    print("🤖 Dive AI Chat Bot Module")
    print("\nAvailable:")
    print(f"   Discord.py: {'✅' if DISCORD_AVAILABLE else '❌ pip install discord.py'}")
    print(f"   Telegram: {'✅' if TELEGRAM_AVAILABLE else '❌ pip install python-telegram-bot'}")
    print("\nUsage:")
    print("   bot = create_discord_bot('YOUR_TOKEN')")
    print("   bot.set_coordinator(coordinator)")
    print("   bot.run()")
