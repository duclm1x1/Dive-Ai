"""
Dive AI Desktop - System Tray Application
Simple, lightweight system tray for controlling Dive AI
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pystray", "Pillow"])
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw, ImageFont

import requests


class DiveAITray:
    """System tray application for Dive AI"""
    
    def __init__(self):
        self.gateway_process = None
        self.icon = None
        self.app_dir = Path(__file__).parent
        
    def create_icon_image(self):
        """Create icon for system tray"""
        # Create 64x64 icon
        size = 64
        image = Image.new('RGB', (size, size), color='#1a1a2e')
        draw = ImageDraw.Draw(image)
        
        # Draw gradient background
        for i in range(size):
            color = (26 + i, 26 + i, 46 + i * 3)
            draw.rectangle([(0, i), (size, i+1)], fill=color)
        
        # Draw "DA" text
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        draw.text((8, 15), "DA", fill='#00CED1', font=font)
        
        return image
    
    def is_gateway_running(self):
        """Check if Gateway is running"""
        try:
            response = requests.get('http://localhost:1879/health', timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def start_gateway(self, icon=None, item=None):
        """Start Gateway Server"""
        if self.gateway_process or self.is_gateway_running():
            if self.icon:
                self.icon.notify("Already Running", "Dive AI Gateway is already running")
            return
        
        try:
            # Start gateway in subprocess
            gateway_script = self.app_dir / "gateway" / "gateway_server.py"
            
            self.gateway_process = subprocess.Popen(
                [sys.executable, str(gateway_script)],
                cwd=str(self.app_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # Wait a bit and check
            time.sleep(2)
            
            if self.is_gateway_running():
                if self.icon:
                    self.icon.notify("Started", "🚀 Dive AI Gateway is running on port 1879")
            else:
                if self.icon:
                    self.icon.notify("Start Failed", "Failed to start Gateway. Check logs.")
                    
        except Exception as e:
            if self.icon:
                self.icon.notify("Error", f"Failed to start: {str(e)}")
    
    def stop_gateway(self, icon=None, item=None):
        """Stop Gateway Server"""
        try:
            if self.gateway_process:
                self.gateway_process.terminate()
                self.gateway_process.wait(timeout=5)
                self.gateway_process = None
            
            if self.icon:
                self.icon.notify("Stopped", "Dive AI Gateway has been stopped")
                
        except Exception as e:
            if self.icon:
                self.icon.notify("Error", f"Failed to stop: {str(e)}")
    
    def check_status(self, icon=None, item=None):
        """Check and display status"""
        if self.is_gateway_running():
            try:
                response = requests.get('http://localhost:1879/statistics', timeout=2)
                stats = response.json()
                
                msg = f"""✅ Gateway Running
                
Total Requests: {stats.get('gateway', {}).get('total_requests', 0)}
Success Rate: {stats.get('gateway', {}).get('success_rate', 0)*100:.1f}%
Active Sessions: {stats.get('gateway', {}).get('active_sessions', 0)}
"""
                if self.icon:
                    self.icon.notify("Status", msg)
            except:
                if self.icon:
                    self.icon.notify("Status", "✅ Gateway running (stats unavailable)")
        else:
            if self.icon:
                self.icon.notify("Status", "❌ Gateway not running")
    
    def open_web_ui(self, icon=None, item=None):
        """Open web UI in browser"""
        import webbrowser
        webbrowser.open('http://localhost:1879/docs')
    
    def open_settings(self, icon=None, item=None):
        """Open settings file"""
        env_file = self.app_dir / ".env"
        if env_file.exists():
            os.startfile(str(env_file))
        else:
            if self.icon:
                self.icon.notify("Settings", ".env file not found")
    
    def open_folder(self, icon=None, item=None):
        """Open installation folder"""
        os.startfile(str(self.app_dir))
    
    def quit_app(self, icon=None, item=None):
        """Quit application"""
        self.stop_gateway()
        if self.icon:
            self.icon.stop()
    
    def run(self):
        """Run system tray application"""
        
        # Create menu
        menu = Menu(
            MenuItem("🚀 Start Gateway", self.start_gateway, default=True),
            MenuItem("⏹️ Stop Gateway", self.stop_gateway),
            MenuItem("📊 Check Status", self.check_status),
            Menu.SEPARATOR,
            MenuItem("🌐 Open Web UI", self.open_web_ui),
            MenuItem("⚙️ Settings", self.open_settings),
            MenuItem("📁 Open Folder", self.open_folder),
            Menu.SEPARATOR,
            MenuItem("❌ Quit", self.quit_app)
        )
        
        # Create icon
        self.icon = Icon(
            "DiveAI",
            self.create_icon_image(),
            "Dive AI V29.3",
            menu
        )
        
        # Auto-start gateway after 2 seconds
        threading.Timer(2.0, self.start_gateway).start()
        
        # Run
        print("Dive AI System Tray started")
        print("Right-click the tray icon for options")
        self.icon.run()


if __name__ == "__main__":
    app = DiveAITray()
    app.run()
