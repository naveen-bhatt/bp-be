"""OAuth state storage for managing PKCE flows."""

from typing import Optional, Dict
from datetime import datetime, timedelta, timezone
import asyncio
from threading import Lock

from app.providers.oauth.base import OAuthState
from app.core.logging import get_logger

logger = get_logger(__name__)


class OAuthStateStorage:
    """In-memory storage for OAuth states with TTL."""
    
    def __init__(self, ttl_minutes: int = 10):
        """
        Initialize OAuth state storage.
        
        Args:
            ttl_minutes: Time to live for stored states in minutes.
        """
        self._storage: Dict[str, tuple[OAuthState, datetime]] = {}
        self._lock = Lock()
        self.ttl_minutes = ttl_minutes
    
    def store_state(self, oauth_state: OAuthState) -> None:
        """
        Store OAuth state with expiration.
        
        Args:
            oauth_state: OAuth state to store.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.ttl_minutes)
        
        with self._lock:
            self._storage[oauth_state.state] = (oauth_state, expires_at)
            logger.info(f"Stored OAuth state: {oauth_state.state[:8]}... (expires: {expires_at})")
            logger.info(f"Total states in storage: {len(self._storage)}")
    
    def get_state(self, state: str) -> Optional[OAuthState]:
        """
        Retrieve and remove OAuth state.
        
        Args:
            state: State parameter to retrieve.
            
        Returns:
            Optional[OAuthState]: OAuth state if found and not expired, None otherwise.
        """
        with self._lock:
            logger.info(f"Looking for OAuth state: {state[:8]}...")
            logger.info(f"Available states: {list(self._storage.keys())[:5]}...")
            
            if state not in self._storage:
                logger.warning(f"OAuth state not found: {state[:8]}...")
                return None
            
            oauth_state, expires_at = self._storage.pop(state)
            
            # Check if expired
            if datetime.now(timezone.utc) > expires_at:
                logger.warning(f"OAuth state expired: {state[:8]}...")
                return None
            
            logger.info(f"Retrieved OAuth state: {state[:8]}... (expires: {expires_at})")
            return oauth_state
    
    def cleanup_expired(self) -> None:
        """Remove expired states from storage."""
        now = datetime.now(timezone.utc)
        expired_states = []
        
        with self._lock:
            for state, (_, expires_at) in self._storage.items():
                if now > expires_at:
                    expired_states.append(state)
            
            for state in expired_states:
                del self._storage[state]
        
        if expired_states:
            logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")
    
    def get_storage_stats(self) -> Dict[str, int]:
        """Get storage statistics."""
        with self._lock:
            total_states = len(self._storage)
            now = datetime.now(timezone.utc)
            expired_count = sum(1 for _, expires_at in self._storage.values() if now > expires_at)
            
        return {
            "total_states": total_states,
            "expired_states": expired_count,
            "active_states": total_states - expired_count
        }


# Global OAuth state storage instance
oauth_state_storage = OAuthStateStorage()


def get_oauth_storage() -> OAuthStateStorage:
    """Get the global OAuth state storage instance."""
    return oauth_state_storage
