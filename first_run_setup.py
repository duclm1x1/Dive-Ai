"""
Dive AI - First Run Setup Wizard
Guides user through initial configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path


class SetupWizard:
    """First-run setup wizard for Dive AI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dive AI Setup Wizard")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # Configuration storage
        self.config = {
            'v98_api_key': '',
            'aicoding_api_key': '',
            'discord_path': '',
            'telegram_path': '',
            'zalo_path': ''
        }
        
        self.current_page = 0
        self.pages = [
            self.create_welcome_page,
            self.create_api_page,
            self.create_channels_page,
            self.create_complete_page
        ]
        
        # Style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10))
        
        self.show_page(0)
    
    def show_page(self, page_num):
        """Show specific page"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show page
        if 0 <= page_num < len(self.pages):
            self.current_page = page_num
            self.pages[page_num]()
    
    def create_welcome_page(self):
        """Welcome page"""
        frame = ttk.Frame(self.root, padding=40)
        frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(
            frame,
            text="🦞 Welcome to Dive AI V29.3!",
            style='Title.TLabel'
        ).pack(pady=20)
        
        # Description
        desc = """
Dive AI is a complete agentic AI system with:

✅ AI-Powered Algorithm Selection
✅ Self-Evolving Algorithms  
✅ Desktop Channels (Discord, Telegram, Zalo)
✅ 50+ Built-in Algorithms
✅ Powered by Claude 4.6 Thinking

This wizard will help you configure Dive AI.
        """
        ttk.Label(
            frame,
            text=desc,
            justify='left',
            style='Subtitle.TLabel'
        ).pack(pady=20)
        
        # Next button
        ttk.Button(
            frame,
            text="Next →",
            command=lambda: self.show_page(1),
            width=15
        ).pack(pady=20)
    
    def create_api_page(self):
        """API keys configuration"""
        frame = ttk.Frame(self.root, padding=40)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="API Configuration", style='Title.TLabel').pack(pady=10)
        ttk.Label(
            frame,
            text="Enter your LLM API keys (optional, can be added later)",
            style='Subtitle.TLabel'
        ).pack(pady=5)
        
        # V98 API Key
        ttk.Label(frame, text="V98 API Key:").pack(pady=(20, 5))
        v98_entry = ttk.Entry(frame, width=60)
        v98_entry.insert(0, self.config['v98_api_key'])
        v98_entry.pack(pady=5)
        
        # AICoding API Key
        ttk.Label(frame, text="AICoding API Key:").pack(pady=(20, 5))
        aicoding_entry = ttk.Entry(frame, width=60)
        aicoding_entry.insert(0, self.config['aicoding_api_key'])
        aicoding_entry.pack(pady=5)
        
        # Help text
        ttk.Label(
            frame,
            text="💡 You can skip this and add keys later in Settings",
            foreground='gray'
        ).pack(pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=30)
        
        def save_and_next():
            self.config['v98_api_key'] = v98_entry.get()
            self.config['aicoding_api_key'] = aicoding_entry.get()
            self.show_page(2)
        
        ttk.Button(btn_frame, text="← Back", command=lambda: self.show_page(0), width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Next →", command=save_and_next, width=15).pack(side='left', padx=5)
    
    def create_channels_page(self):
        """Desktop channels configuration"""
        frame = ttk.Frame(self.root, padding=40)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Desktop Channels", style='Title.TLabel').pack(pady=10)
        ttk.Label(
            frame,
            text="Configure desktop messaging apps (optional)",
            style='Subtitle.TLabel'
        ).pack(pady=5)
        
        # Discord
        discord_frame = ttk.Frame(frame)
        discord_frame.pack(fill='x', pady=10)
        ttk.Label(discord_frame, text="Discord:").pack(side='left')
        discord_entry = ttk.Entry(discord_frame, width=40)
        discord_entry.insert(0, self.config['discord_path'])
        discord_entry.pack(side='left', padx=5)
        
        def browse_discord():
            path = filedialog.askopenfilename(
                title="Select Discord.exe",
                filetypes=[("Executable", "*.exe")]
            )
            if path:
                discord_entry.delete(0, tk.END)
                discord_entry.insert(0, path)
        
        ttk.Button(discord_frame, text="Browse", command=browse_discord).pack(side='left')
        
        # Telegram
        telegram_frame = ttk.Frame(frame)
        telegram_frame.pack(fill='x', pady=10)
        ttk.Label(telegram_frame, text="Telegram:").pack(side='left')
        telegram_entry = ttk.Entry(telegram_frame, width=40)
        telegram_entry.insert(0, self.config['telegram_path'])
        telegram_entry.pack(side='left', padx=5)
        
        def browse_telegram():
            path = filedialog.askopenfilename(
                title="Select Telegram.exe",
                filetypes=[("Executable", "*.exe")]
            )
            if path:
                telegram_entry.delete(0, tk.END)
                telegram_entry.insert(0, path)
        
        ttk.Button(telegram_frame, text="Browse", command=browse_telegram).pack(side='left')
        
        # Zalo
        zalo_frame = ttk.Frame(frame)
        zalo_frame.pack(fill='x', pady=10)
        ttk.Label(zalo_frame, text="Zalo:").pack(side='left')
        zalo_entry = ttk.Entry(zalo_frame, width=40)
        zalo_entry.insert(0, self.config['zalo_path'])
        zalo_entry.pack(side='left', padx=5)
        
        def browse_zalo():
            path = filedialog.askopenfilename(
                title="Select Zalo.exe",
                filetypes=[("Executable", "*.exe")]
            )
            if path:
                zalo_entry.delete(0, tk.END)
                zalo_entry.insert(0, path)
        
        ttk.Button(zalo_frame, text="Browse", command=browse_zalo).pack(side='left')
        
        # Help
        ttk.Label(
            frame,
            text="💡 Leave blank to use auto-detection",
            foreground='gray'
        ).pack(pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=30)
        
        def save_and_finish():
            self.config['discord_path'] = discord_entry.get()
            self.config['telegram_path'] = telegram_entry.get()
            self.config['zalo_path'] = zalo_entry.get()
            self.save_configuration()
            self.show_page(3)
        
        ttk.Button(btn_frame, text="← Back", command=lambda: self.show_page(1), width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Finish →", command=save_and_finish, width=15).pack(side='left', padx=5)
    
    def create_complete_page(self):
        """Setup complete page"""
        frame = ttk.Frame(self.root, padding=40)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="✅ Setup Complete!", style='Title.TLabel').pack(pady=20)
        
        message = """
Dive AI is now configured and ready to use!

The system tray icon has been started.
Right-click the tray icon to:
  • Start/Stop Gateway
  • Check Status
  • Open Web UI
  • Configure Settings

Gateway will be available at:
  http://localhost:1879

Enjoy using Dive AI V29.3! 🚀
        """
        
        ttk.Label(
            frame,
            text=message,
            justify='left',
            style='Subtitle.TLabel'
        ).pack(pady=20)
        
        ttk.Button(
            frame,
            text="Close",
            command=self.root.quit,
            width=15
        ).pack(pady=20)
    
    def save_configuration(self):
        """Save configuration to .env file"""
        env_path = Path(__file__).parent / ".env"
        
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"# Dive AI Configuration\n")
                f.write(f"# Generated by Setup Wizard\n\n")
                
                f.write(f"# LLM API Keys\n")
                f.write(f"V98_API_KEY={self.config['v98_api_key']}\n")
                f.write(f"AICODING_API_KEY={self.config['aicoding_api_key']}\n\n")
                
                f.write(f"# Desktop Channels\n")
                f.write(f"DISCORD_PATH={self.config['discord_path']}\n")
                f.write(f"TELEGRAM_PATH={self.config['telegram_path']}\n")
                f.write(f"ZALO_PATH={self.config['zalo_path']}\n")
            
            print(f"✅ Configuration saved to {env_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def run(self):
        """Run the setup wizard"""
        self.root.mainloop()


if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()
