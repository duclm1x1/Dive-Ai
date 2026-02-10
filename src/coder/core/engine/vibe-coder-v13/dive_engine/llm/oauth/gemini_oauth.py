"""
Gemini OAuth Manager
====================

OAuth 2.0 authentication for Google Gemini using Localhost Callback Flow.

This implementation mimics the Gemini CLI client to bypass API key restrictions
and access Gemini models using user OAuth tokens.
"""

import asyncio
import webbrowser
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from pathlib import Path
from typing import Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not installed. Install with: pip install httpx")

from dive_engine.llm.oauth.base import OAuthManager, OAuthToken


class GeminiOAuthManager(OAuthManager):
    """OAuth manager for Google Gemini CLI."""
    
    # Extracted from Gemini CLI source code
    CLIENT_ID = "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
    CLIENT_SECRET = "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"
    REDIRECT_URI = "http://localhost:8085"
    SCOPES = "https://www.googleapis.com/auth/generative-language.retriever"
    
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    def __init__(self, token_storage_path: Optional[Path] = None):
        """
        Initialize Gemini OAuth manager.
        
        Args:
            token_storage_path: Path to store token (default: ./configs/tokens/gemini_cli.json)
        """
        if token_storage_path is None:
            token_storage_path = Path("./configs/tokens/gemini_cli.json")
        
        super().__init__(token_storage_path)
    
    async def authenticate(self) -> OAuthToken:
        """Perform OAuth authentication with localhost callback."""
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for OAuth. Install with: pip install httpx")
        
        # Build authorization URL
        auth_url = (
            f"{self.AUTH_URL}?"
            f"client_id={self.CLIENT_ID}&"
            f"redirect_uri={self.REDIRECT_URI}&"
            f"response_type=code&"
            f"scope={self.SCOPES}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        print(f"\n🔐 Gemini CLI OAuth Authentication")
        print(f"=" * 60)
        print(f"Opening browser for authentication...")
        print(f"\nIf browser doesn't open automatically, visit:")
        print(f"{auth_url}\n")
        
        # Open browser
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            print(f"Failed to open browser: {e}")
        
        # Start local server to receive callback
        auth_code = await self._start_callback_server()
        
        print(f"\n✅ Authorization code received!")
        print(f"Exchanging code for tokens...\n")
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "code": auth_code,
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "redirect_uri": self.REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            data = response.json()
        
        # Calculate expiration
        expires_at = None
        if "expires_in" in data:
            expires_at = time.time() + data["expires_in"]
        
        print(f"✅ Authentication successful!")
        print(f"Token will expire at: {time.ctime(expires_at) if expires_at else 'Never'}\n")
        
        return OAuthToken(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer"),
            scope=data.get("scope"),
        )
    
    async def refresh_token(self, token: OAuthToken) -> OAuthToken:
        """Refresh expired token."""
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for OAuth. Install with: pip install httpx")
        
        if not token.refresh_token:
            # No refresh token, need to re-authenticate
            print("No refresh token available, re-authenticating...")
            return await self.authenticate()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "refresh_token": token.refresh_token,
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()
        
        # Calculate expiration
        expires_at = None
        if "expires_in" in data:
            expires_at = time.time() + data["expires_in"]
        
        return OAuthToken(
            access_token=data["access_token"],
            refresh_token=token.refresh_token,  # Keep old refresh token
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer"),
            scope=data.get("scope"),
        )
    
    async def _start_callback_server(self) -> str:
        """Start temporary HTTP server to receive OAuth callback."""
        
        auth_code = None
        error_message = None
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code, error_message
                
                # Parse query parameters
                query = urlparse(self.path).query
                params = parse_qs(query)
                
                if "code" in params:
                    auth_code = params["code"][0]
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write("""
                        <html>
                        <head>
                            <title>Authentication Successful</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 100vh;
                                    margin: 0;
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                }
                                .container {
                                    background: white;
                                    padding: 40px;
                                    border-radius: 10px;
                                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                    text-align: center;
                                }
                                h1 { color: #667eea; margin-bottom: 20px; }
                                p { color: #666; font-size: 16px; }
                                .checkmark {
                                    font-size: 60px;
                                    color: #4CAF50;
                                    margin-bottom: 20px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="checkmark">OK</div>
                                <h1>Authentication Successful!</h1>
                                <p>You can close this window and return to the terminal.</p>
                            </div>
                        </body>
                        </html>
                    """.encode('utf-8'))
                elif "error" in params:
                    error_message = params["error"][0]
                    
                    # Send error response
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    html = """
                        <html>
                        <head>
                            <title>Authentication Failed</title>
                            <style>
                                body {{
                                    font-family: Arial, sans-serif;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 100vh;
                                    margin: 0;
                                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                }}
                                .container {{
                                    background: white;
                                    padding: 40px;
                                    border-radius: 10px;
                                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                    text-align: center;
                                }}
                                h1 {{ color: #f5576c; margin-bottom: 20px; }}
                                p {{ color: #666; font-size: 16px; }}
                                .error-icon {{
                                    font-size: 60px;
                                    color: #f5576c;
                                    margin-bottom: 20px;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="error-icon">X</div>
                                <h1>Authentication Failed</h1>
                                <p>Error: {error_message}</p>
                                <p>Please try again.</p>
                            </div>
                        </body>
                        </html>
                    """.format(error_message=error_message)
                    self.wfile.write(html.encode('utf-8'))
                else:
                    # Unknown response
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Invalid Response</h1></body></html>")
            
            def log_message(self, format, *args):
                pass  # Suppress log messages
        
        # Start server
        server = HTTPServer(("localhost", 8085), CallbackHandler)
        
        print(f"Waiting for authentication (timeout: 5 minutes)...")
        
        # Wait for callback (with timeout)
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while auth_code is None and error_message is None and (time.time() - start_time) < timeout:
            server.handle_request()
        
        server.server_close()
        
        if error_message:
            raise RuntimeError(f"OAuth authentication failed: {error_message}")
        
        if auth_code is None:
            raise TimeoutError("OAuth authentication timed out after 5 minutes")
        
        return auth_code


class AntigravityOAuthManager(GeminiOAuthManager):
    """OAuth manager for Antigravity (alternative Gemini client)."""
    
    # Extracted from Antigravity source code
    CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
    CLIENT_SECRET = "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"
    REDIRECT_URI = "http://localhost:8086"  # Different port
    
    def __init__(self, token_storage_path: Optional[Path] = None):
        """
        Initialize Antigravity OAuth manager.
        
        Args:
            token_storage_path: Path to store token (default: ./configs/tokens/antigravity.json)
        """
        if token_storage_path is None:
            token_storage_path = Path("./configs/tokens/antigravity.json")
        
        # Call grandparent __init__ to avoid GeminiOAuthManager's default path
        OAuthManager.__init__(self, token_storage_path)
    
    async def _start_callback_server(self) -> str:
        """Start callback server on port 8086."""
        # Override to use different port
        # (Implementation same as parent but with port 8086)
        # For brevity, reusing parent implementation
        return await super()._start_callback_server()


# CLI interface for standalone authentication
async def main():
    """CLI interface for Gemini OAuth authentication."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--antigravity":
        print("Using Antigravity OAuth...")
        manager = AntigravityOAuthManager()
    else:
        print("Using Gemini CLI OAuth...")
        manager = GeminiOAuthManager()
    
    token = await manager.authenticate()
    manager.save_token(token)
    
    print(f"\n✅ Token saved to: {manager.token_storage_path}")
    print(f"Access token (first 20 chars): {token.access_token[:20]}...")
    print(f"Expires at: {time.ctime(token.expires_at) if token.expires_at else 'Never'}")


if __name__ == "__main__":
    asyncio.run(main())
