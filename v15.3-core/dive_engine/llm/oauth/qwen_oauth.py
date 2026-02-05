"""
Qwen OAuth Manager
==================

OAuth 2.0 authentication for Alibaba Qwen using Device Authorization Flow.

This implementation mimics the Qwen client to access Qwen models
(including Qwen3 Coder Plus) for free using user OAuth tokens.
"""

import asyncio
import time
from pathlib import Path
from typing import Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not installed. Install with: pip install httpx")

from dive_engine.llm.oauth.base import OAuthManager, OAuthToken


class QwenOAuthManager(OAuthManager):
    """OAuth manager for Alibaba Qwen."""
    
    # Extracted from Qwen client source code
    CLIENT_ID = "f0304373b74a44d2b584a3fb70ca9e56"
    DEVICE_CODE_URL = "https://chat.qwen.ai/api/v1/oauth2/device/code"
    TOKEN_URL = "https://chat.qwen.ai/api/v1/oauth2/token"
    SCOPES = "openid profile"
    
    def __init__(self, token_storage_path: Optional[Path] = None):
        """
        Initialize Qwen OAuth manager.
        
        Args:
            token_storage_path: Path to store token (default: ./configs/tokens/qwen.json)
        """
        if token_storage_path is None:
            token_storage_path = Path("./configs/tokens/qwen.json")
        
        super().__init__(token_storage_path)
    
    async def authenticate(self) -> OAuthToken:
        """Perform device authorization flow."""
        
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for OAuth. Install with: pip install httpx")
        
        # Step 1: Request device code
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.DEVICE_CODE_URL,
                json={
                    "client_id": self.CLIENT_ID,
                    "scope": self.SCOPES,
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            device_data = response.json()
        
        verification_uri = device_data["verification_uri_complete"]
        device_code = device_data["device_code"]
        user_code = device_data.get("user_code", "")
        interval = device_data.get("interval", 5)
        expires_in = device_data.get("expires_in", 600)
        
        print(f"\n🔐 Qwen OAuth Authentication")
        print(f"=" * 60)
        print(f"\n📱 Please visit the following URL to authenticate:")
        print(f"\n   {verification_uri}\n")
        
        if user_code:
            print(f"User Code: {user_code}\n")
        
        print(f"Waiting for authentication (timeout: {expires_in // 60} minutes)...")
        print(f"Checking every {interval} seconds...\n")
        
        # Step 2: Poll for token
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
                        json={
                            "client_id": self.CLIENT_ID,
                            "device_code": device_code,
                            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        },
                        headers={"Content-Type": "application/json"},
                    )
                    
                    if response.status_code == 200:
                        # Success!
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
                            # Still waiting
                            print("⏳ Pending...")
                            continue
                        elif error == "slow_down":
                            # Increase interval
                            print("⏸️  Slowing down...")
                            interval += 5
                            continue
                        elif error == "expired_token":
                            print("❌ Expired!")
                            raise TimeoutError("Device code expired. Please try again.")
                        elif error == "access_denied":
                            print("❌ Denied!")
                            raise RuntimeError("User denied authorization")
                        else:
                            # Other error
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                json={
                    "client_id": self.CLIENT_ID,
                    "refresh_token": token.refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
        
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


# CLI interface for standalone authentication
async def main():
    """CLI interface for Qwen OAuth authentication."""
    manager = QwenOAuthManager()
    
    token = await manager.authenticate()
    manager.save_token(token)
    
    print(f"\n✅ Token saved to: {manager.token_storage_path}")
    print(f"Access token (first 20 chars): {token.access_token[:20]}...")
    print(f"Expires at: {time.ctime(token.expires_at) if token.expires_at else 'Never'}")


if __name__ == "__main__":
    asyncio.run(main())
