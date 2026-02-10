"""
OAuth Manager Base Classes
===========================

Base classes for OAuth 2.0 authentication flows.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import json
import time
from pathlib import Path


@dataclass
class OAuthToken:
    """OAuth token with metadata."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None
    
    def is_expired(self, buffer_seconds: int = 300) -> bool:
        """
        Check if token is expired.
        
        Args:
            buffer_seconds: Consider token expired this many seconds before actual expiry
        """
        if not self.expires_at:
            return False
        return time.time() >= (self.expires_at - buffer_seconds)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "token_type": self.token_type,
            "scope": self.scope,
        }
    
    @staticmethod
    def from_dict(d: dict) -> "OAuthToken":
        """Create from dictionary."""
        return OAuthToken(
            access_token=d["access_token"],
            refresh_token=d.get("refresh_token"),
            expires_at=d.get("expires_at"),
            token_type=d.get("token_type", "Bearer"),
            scope=d.get("scope"),
        )


class OAuthManager(ABC):
    """Base class for OAuth managers."""
    
    def __init__(self, token_storage_path: Path):
        """
        Initialize OAuth manager.
        
        Args:
            token_storage_path: Path to store token JSON file
        """
        self.token_storage_path = token_storage_path
        self.token_storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    async def authenticate(self) -> OAuthToken:
        """
        Perform OAuth authentication flow.
        
        Returns:
            OAuthToken with access and refresh tokens
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, token: OAuthToken) -> OAuthToken:
        """
        Refresh an expired token.
        
        Args:
            token: Expired token with refresh_token
            
        Returns:
            New OAuthToken with refreshed access token
        """
        pass
    
    async def get_valid_token(self) -> OAuthToken:
        """
        Get a valid token, refreshing if necessary.
        
        Returns:
            Valid OAuthToken
        """
        token = self.load_token()
        
        if token is None:
            # No token, need to authenticate
            print(f"No token found, starting authentication...")
            token = await self.authenticate()
            self.save_token(token)
            return token
        
        if token.is_expired():
            # Token expired, refresh it
            print(f"Token expired, refreshing...")
            try:
                token = await self.refresh_token(token)
                self.save_token(token)
            except Exception as e:
                print(f"Token refresh failed: {e}")
                print(f"Re-authenticating...")
                token = await self.authenticate()
                self.save_token(token)
        
        return token
    
    def save_token(self, token: OAuthToken):
        """
        Save token to storage.
        
        Args:
            token: Token to save
        """
        with open(self.token_storage_path, 'w') as f:
            json.dump(token.to_dict(), f, indent=2)
        
        # Set restrictive permissions
        self.token_storage_path.chmod(0o600)
    
    def load_token(self) -> Optional[OAuthToken]:
        """
        Load token from storage.
        
        Returns:
            OAuthToken if exists, None otherwise
        """
        if not self.token_storage_path.exists():
            return None
        
        try:
            with open(self.token_storage_path, 'r') as f:
                data = json.load(f)
            return OAuthToken.from_dict(data)
        except Exception as e:
            print(f"Failed to load token: {e}")
            return None
    
    def clear_token(self):
        """Clear stored token."""
        if self.token_storage_path.exists():
            self.token_storage_path.unlink()
