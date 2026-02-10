"""
Dive AI - Desktop IDE Application
Native desktop application with integrated AI coding assistant

Based on UI-TARS V28.7 architecture
"""

import sys
import os
from pathlib import Path

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    print("Installing PyQt6...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6", "PyQt6-WebEngine"])
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWebEngineWidgets import QWebEngineView

import requests


class DiveAIDesktopIDE(QMainWindow):
    """Dive AI Desktop IDE - Native Application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dive AI Desktop IDE V29.4")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0e27;
            }
            QMenuBar {
                background-color: #0f1729;
                color: #e4e4e7;
                border-bottom: 1px solid #1e293b;
            }
            QMenuBar::item:selected {
                background-color: #1e293b;
            }
            QMenu {
                background-color: #0f1729;
                color: #e4e4e7;
                border: 1px solid #1e293b;
            }
            QMenu::item:selected {
                background-color: #1e293b;
            }
            QStatusBar {
                background-color: #0f1729;
                color: #64748b;
                border-top: 1px solid #1e293b;
            }
        """)
        
        # Create UI
        self.create_menu_bar()
        self.create_central_widget()
        self.create_status_bar()
        
        # Check Gateway connection
        self.check_gateway_connection()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('New File', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        chat_action = QAction('Chat Panel', self)
        chat_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(chat_action)
        
        editor_action = QAction('Code Editor', self)
        editor_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(editor_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_central_widget(self):
        """Create main content area"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #0a0e27;
                border: none;
            }
            QTabBar::tab {
                background-color: #0f1729;
                color: #64748b;
                padding: 10px 20px;
                border-right: 1px solid #1e293b;
            }
            QTabBar::tab:selected {
                background-color: #1e293b;
                color: #00d4ff;
            }
        """)
        
        # Web IDE tab (embed web interface)
        web_view = QWebEngineView()
        web_ide_path = Path(__file__).parent / "web_ide" / "index.html"
        
        if web_ide_path.exists():
            web_view.setUrl(QUrl.fromLocalFile(str(web_ide_path.absolute())))
        else:
            # Load from localhost if running
            web_view.setUrl(QUrl("http://localhost:1879"))
        
        self.tabs.addTab(web_view, "💬 AI Chat")
        
        # Code Editor tab
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e27;
                color: #e4e4e7;
                border: none;
                font-family: 'Consolas', 'JetBrains Mono', monospace;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.editor.setPlainText("# Welcome to Dive AI Desktop IDE\n\n# Your AI-powered coding assistant\n\nprint('Hello from Dive AI V29.4!')\n")
        
        self.tabs.addTab(self.editor, "📝 Code Editor")
        
        # Terminal tab
        self.terminal = QTextEdit()
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #000;
                color: #00ff00;
                border: none;
                font-family: 'Consolas', 'JetBrains Mono', monospace;
                font-size: 13px;
                padding: 20px;
            }
        """)
        self.terminal.setReadOnly(True)
        self.terminal.setPlainText("Dive AI Terminal V29.4\n\n")
        
        self.tabs.addTab(self.terminal, "⚡ Terminal")
        
        layout.addWidget(self.tabs)
    
    def create_status_bar(self):
        """Create status bar"""
        status = self.statusBar()
        
        # Gateway status
        self.gateway_status = QLabel("⚫ Gateway: Checking...")
        status.addPermanentWidget(self.gateway_status)
        
        # Version info
        version_label = QLabel("Dive AI V29.4")
        status.addPermanentWidget(version_label)
    
    def check_gateway_connection(self):
        """Check if Gateway is running"""
        try:
            response = requests.get('http://localhost:1879/health', timeout=2)
            if response.status_code == 200:
                self.gateway_status.setText("🟢 Gateway: Connected")
                self.gateway_status.setStyleSheet("color: #22c55e;")
            else:
                self.gateway_status.setText("🟡 Gateway: Unknown")
                self.gateway_status.setStyleSheet("color: #eab308;")
        except:
            self.gateway_status.setText("🔴 Gateway: Offline")
            self.gateway_status.setStyleSheet("color: #ef4444;")
            
            # Show connection dialog
            QTimer.singleShot(1000, self.show_connection_dialog)
    
    def show_connection_dialog(self):
        """Show connection help dialog"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Gateway Not Running")
        msg.setText("Dive AI Gateway is not running")
        msg.setInformativeText(
            "Start the Gateway Server to use AI features:\n\n"
            "python gateway/gateway_server.py\n\n"
            "The Web IDE will still work for code editing."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def new_file(self):
        """Create new file"""
        self.editor.clear()
        self.tabs.setCurrentIndex(1)
    
    def open_file(self):
        """Open file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Python Files (*.py);;All Files (*.*)"
        )
        
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
            self.tabs.setCurrentIndex(1)
    
    def save_file(self):
        """Save file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Python Files (*.py);;All Files (*.*)"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            
            self.statusBar().showMessage(f"Saved: {filename}", 3000)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Dive AI Desktop IDE",
            """<h2>Dive AI Desktop IDE V29.3</h2>
            <p>AI-Powered Coding Assistant</p>
            <p><b>Features:</b></p>
            <ul>
                <li>AI Chat Interface</li>
                <li>Code Editor with Syntax Highlighting</li>
                <li>Integrated Terminal</li>
                <li>50+ AI Algorithms</li>
                <li>Self-Evolving System</li>
            </ul>
            <p><b>Gateway:</b> http://localhost:1879</p>
            <p>Made with 🧬 by Dive AI Self-Evolving System</p>
            """
        )


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application details
    app.setApplicationName("Dive AI Desktop IDE")
    app.setOrganizationName("Dive AI")
    app.setApplicationVersion("29.4")
    
    # Create and show main window
    window = DiveAIDesktopIDE()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
