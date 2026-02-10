"""
Telegram Channel - Bot integration

Uses python-telegram-bot to receive and respond to messages.
"""

import asyncio
from typing import Optional, Callable
from dataclasses import dataclass
import os

# Telegram bot (optional dependency)
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

from ..llm.connections import get_manager


@dataclass
class TelegramConfig:
    """Telegram bot config"""
    token: str
    allowed_users: list = None  # Only respond to these user IDs


class TelegramChannel:
    """
    Telegram bot channel
    
    Commands:
    - /start - Initialize
    - /help - Show help
    - /model - Show current model
    
    All other messages sent to Claude.
    """
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.manager = get_manager()
        self.app = None
    
    def is_available(self) -> bool:
        """Check availability"""
        return AVAILABLE and bool(self.token)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start"""
        await update.message.reply_text(
            "🦞 Dive AI V29.4\n\n"
            "Send me any message and I'll respond using Claude.\n"
            "Commands: /help, /model"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help"""
        await update.message.reply_text(
            "Commands:\n"
            "/start - Initialize\n"
            "/help - Show this help\n"
            "/model - Show current model\n\n"
            "Send any text message to chat with Claude."
        )
    
    async def model_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /model"""
        status = self.manager.status()
        await update.message.reply_text(
            f"Primary: {status.get('primary', 'Unknown')}\n"
            f"Models: {status.get('models', 0)}\n"
            f"Available: {status.get('available', False)}"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text message"""
        user_message = update.message.text
        
        # Generate response
        response = self.manager.chat(user_message)
        
        if response.success:
            await update.message.reply_text(response.content)
        else:
            await update.message.reply_text(f"Error: {response.error}")
    
    def start(self):
        """Start bot"""
        if not self.is_available():
            print("Telegram not available - check token and dependencies")
            return
        
        self.app = Application.builder().token(self.token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("model", self.model_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("Starting Telegram bot...")
        self.app.run_polling()
    
    def stop(self):
        """Stop bot"""
        if self.app:
            self.app.stop()


# Singleton
_channel = None

def get_telegram_channel() -> TelegramChannel:
    """Get Telegram channel"""
    global _channel
    if _channel is None:
        _channel = TelegramChannel()
    return _channel
