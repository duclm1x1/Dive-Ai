"""
Kiro OAuth Manager
==================

OAuth 2.0 authentication for Amazon Kiro (CodeWhisperer) to access Claude models for free.

Supports two authentication methods:
1. Social Auth (Localhost Callback Flow) - Using GitHub/Google
2. Builder ID (Device Authorization Flow) - Using AWS Builder ID

This allows free access to Claude Opus 4.5, Claude Sonnet 4.5, and other Claude models.
"""

import asyncio
import webbrowser
import time
import secrets
import hashlib
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, urlencode
from pathlib import Path
from typing import Optional, Literal

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not installed. Install with: pip install httpx")

from dive_engine.llm.oauth.base import OAuthManager, OAuthToken


class KiroSocialOAuthManager(OAuthManager):
    """OAuth manager for Kiro using Social Auth (GitHub/Google)."""
    
    # Kiro Social Auth endpoints
    AUTH_URL = "https://api.codewhisperer.aws.dev/oauth2/authorize"
    TOKEN_URL = "https://api.codewhisperer.aws.dev/oauth2/token"
    REDIRECT_URI = "http://localhost:8087"
    SCOPES = "codewhisperer:conversations codewhisperer:analysis"
    
    def __init__(self, token_storage_path: Optional[Path] = None):
        """
        Initialize Kiro Social OAuth manager.
        
        Args:
            token_storage_path: Path to store token (default: ./configs/tokens/kiro_social.json)
        """
        if token_storage_path is None:
            token_storage_path = Path("./configs/tokens/kiro_social.json")
        
        super().__init__(token_storage_path)
    
    def _generate_pkce_params(self):
        """Generate PKCE (Proof Key for Code Exchange) parameters."""
        # Generate code verifier
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    async def authenticate(self) -> OAuthToken:
        """Perform OAuth authentication with PKCE and localhost callback."""
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for OAuth. Install with: pip install httpx")
        
        # Generate PKCE parameters
        code_verifier, code_challenge = self._generate_pkce_params()
        state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": self.SCOPES,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": state,
        }
        
        auth_url = f"{self.AUTH_URL}?{urlencode(auth_params)}"
        
        print(f"\n🔐 Kiro Social OAuth Authentication")
        print(f"=" * 60)
        print(f"Opening browser for authentication...")
        print(f"\nYou'll be asked to sign in with GitHub or Google.")
        print(f"\nIf browser doesn't open automatically, visit:")
        print(f"{auth_url}\n")
        
        # Open browser
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            print(f"Failed to open browser: {e}")
        
        # Start local server to receive callback
        auth_code, returned_state = await self._start_callback_server()
        
        # Verify state
        if returned_state != state:
            raise RuntimeError("State mismatch - possible CSRF attack")
        
        print(f"\n✅ Authorization code received!")
        print(f"Exchanging code for tokens...\n")
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "code": auth_code,
                    "redirect_uri": self.REDIRECT_URI,
                    "grant_type": "authorization_code",
                    "code_verifier": code_verifier,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
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
            print("No refresh token available, re-authenticating...")
            return await self.authenticate()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "refresh_token": token.refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()
        
        expires_at = None
        if "expires_in" in data:
            expires_at = time.time() + data["expires_in"]
        
        return OAuthToken(
            access_token=data["access_token"],
            refresh_token=token.refresh_token,
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer"),
            scope=data.get("scope"),
        )
    
    async def _start_callback_server(self) -> tuple[str, str]:
        """Start temporary HTTP server to receive OAuth callback."""
        
        auth_code = None
        state = None
        error_message = None
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code, state, error_message
                
                # Parse query parameters
                query = urlparse(self.path).query
                params = parse_qs(query)
                
                if "code" in params:
                    auth_code = params["code"][0]
                    state = params.get("state", [None])[0]
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"""
                        <html>
                        <head>
                            <title>Kiro Authentication Successful</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 100vh;
                                    margin: 0;
                                    background: linear-gradient(135deg, #FF9A56 0%, #FF6A88 100%);
                                }
                                .container {
                                    background: white;
                                    padding: 40px;
                                    border-radius: 10px;
                                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                    text-align: center;
                                }
                                h1 { color: #FF6A88; margin-bottom: 20px; }
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
                                <h1>Kiro Authentication Successful!</h1>
                                <p>You now have access to Claude models for free.</p>
                                <p>You can close this window and return to the terminal.</p>
                            </div>
                        </body>
                        </html>
                    """)
                elif "error" in params:
                    error_message = params["error"][0]
                    
                    # Send error response
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"""
                        <html>
                        <head><title>Authentication Failed</title></head>
                        <body>
                            <h1>Authentication Failed</h1>
                            <p>Error: {error_message}</p>
                        </body>
                        </html>
                    """.encode())
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Invalid Response</h1></body></html>")
            
            def log_message(self, format, *args):
                pass
        
        # Start server
        server = HTTPServer(("localhost", 8087), CallbackHandler)
        
        print(f"Waiting for authentication (timeout: 5 minutes)...")
        
        # Wait for callback
        timeout = 300
        start_time = time.time()
        
        while auth_code is None and error_message is None and (time.time() - start_time) < timeout:
            server.handle_request()
        
        server.server_close()
        
        if error_message:
            raise RuntimeError(f"OAuth authentication failed: {error_message}")
        
        if auth_code is None:
            raise TimeoutError("OAuth authentication timed out after 5 minutes")
        
        return auth_code, state


class KiroBuilderIDOAuthManager(OAuthManager):
    """OAuth manager for Kiro using AWS Builder ID (Device Authorization Flow)."""
    
    # AWS Builder ID endpoints
    REGISTER_CLIENT_URL = "https://oidc.us-east-1.amazonaws.com/register"
    DEVICE_CODE_URL = "https://oidc.us-east-1.amazonaws.com/device_authorization"
    TOKEN_URL = "https://oidc.us-east-1.amazonaws.com/token"
    SCOPES = "codewhisperer:conversations codewhisperer:analysis"
    
    def __init__(self, token_storage_path: Optional[Path] = None):
        """
        Initialize Kiro Builder ID OAuth manager.
        
        Args:
            token_storage_path: Path to store token (default: ./configs/tokens/kiro_builder_id.json)
        """
        if token_storage_path is None:
            token_storage_path = Path("./configs/tokens/kiro_builder_id.json")
        
        super().__init__(token_storage_path)
        self.client_id = None
        self.client_secret = None
    
    async def _register_client(self):
        """Register a dynamic client with AWS Builder ID."""
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for OAuth. Install with: pip install httpx")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.REGISTER_CLIENT_URL,
                json={
                    "client_name": "Dive Engine LLM Client",
                    "grant_types": ["urn:ietf:params:oauth:grant-type:device_code", "refresh_token"],
                    "scopes": self.SCOPES.split(),
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
        
        self.client_id = data["client_id"]
        self.client_secret = data["client_secret"]
        
        print(f"✅ Client registered successfully")
        print(f"Client ID: {self.client_id[:20]}...\n")
    
    async def authenticate(self) -> OAuthToken:
        """Perform device authorization flow with AWS Builder ID."""
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for OAuth. Install with: pip install httpx")
        
        # Register client first
        await self._register_client()
        
        # Request device code
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.DEVICE_CODE_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": self.SCOPES,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            device_data = response.json()
        
        verification_uri = device_data["verification_uri_complete"]
        device_code = device_data["device_code"]
        interval = device_data.get("interval", 5)
        expires_in = device_data.get("expires_in", 600)
        
        print(f"\n🔐 Kiro Builder ID OAuth Authentication")
        print(f"=" * 60)
        print(f"\n📱 Please visit the following URL to authenticate:")
        print(f"\n   {verification_uri}\n")
        print(f"Waiting for authentication (timeout: {expires_in // 60} minutes)...")
        print(f"Checking every {interval} seconds...\n")
        
        # Poll for token
        start_time = time.time()
        attempt = 0
        
        while (time.time() - start_time) < expires_in:
            attempt += 1
            await asyncio.sleep(interval)
            
            print(f"Attempt {attempt}: Checking authentication status...", end=" ")
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.TOKEN_URL,
                        data={
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "device_code": device_code,
                            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        },
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        expires_at = None
                        if "expires_in" in data:
                            expires_at = time.time() + data["expires_in"]
                        
                        print("✅ Success!\n")
                        print(f"✅ Authentication successful!")
                        print(f"Token will expire at: {time.ctime(expires_at) if expires_at else 'Never'}\n")
                        
                        return OAuthToken(
                            access_token=data["access_token"],
                            refresh_token=data.get("refresh_token"),
                            expires_at=expires_at,
                            token_type=data.get("token_type", "Bearer"),
                            scope=data.get("scope"),
                        )
                    
                    elif response.status_code == 400:
                        error_data = response.json()
                        error = error_data.get("error", "")
                        
                        if error == "authorization_pending":
                            print("⏳ Pending...")
                            continue
                        elif error == "slow_down":
                            print("⏸️  Slowing down...")
                            interval += 5
                            continue
                        else:
                            print(f"❌ Error: {error}")
                            raise RuntimeError(f"OAuth error: {error}")
                    else:
                        print(f"❌ HTTP {response.status_code}")
                        continue
            
            except httpx.HTTPError as e:
                print(f"❌ Network error: {e}")
                continue
        
        raise TimeoutError(f"Device authorization timed out after {expires_in // 60} minutes")
    
    async def refresh_token(self, token: OAuthToken) -> OAuthToken:
        """Refresh expired token."""
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for OAuth. Install with: pip install httpx")
        
        if not token.refresh_token:
            print("No refresh token available, re-authenticating...")
            return await self.authenticate()
        
        # Need to register client again for refresh
        await self._register_client()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": token.refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()
        
        expires_at = None
        if "expires_in" in data:
            expires_at = time.time() + data["expires_in"]
        
        return OAuthToken(
            access_token=data["access_token"],
            refresh_token=token.refresh_token,
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer"),
            scope=data.get("scope"),
        )


# CLI interface for standalone authentication
async def main():
    """CLI interface for Kiro OAuth authentication."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--builder-id":
        print("Using Kiro Builder ID OAuth...")
        manager = KiroBuilderIDOAuthManager()
    else:
        print("Using Kiro Social OAuth...")
        manager = KiroSocialOAuthManager()
    
    token = await manager.authenticate()
    manager.save_token(token)
    
    print(f"\n✅ Token saved to: {manager.token_storage_path}")
    print(f"Access token (first 20 chars): {token.access_token[:20]}...")
    print(f"Expires at: {time.ctime(token.expires_at) if token.expires_at else 'Never'}")
    print(f"\n🎉 You now have FREE access to Claude Opus 4.5 and other Claude models!")


if __name__ == "__main__":
    asyncio.run(main())
