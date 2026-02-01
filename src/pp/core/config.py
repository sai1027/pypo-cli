"""Configuration management for Project Pilot."""

import os
from pathlib import Path
from typing import Any, Optional


class Config:
    """Configuration manager with environment variable support."""
    
    # Default configuration values
    DEFAULTS = {
        "editor": "notepad" if os.name == "nt" else "nano",
        "default_output_dir": ".",
    }
    
    # Environment variable prefix
    ENV_PREFIX = "PP_"
    
    def __init__(self, storage=None):
        """
        Initialize configuration.
        
        Args:
            storage: Storage instance for persistent config
        """
        self._storage = storage
        self._cache: Optional[dict] = None
    
    @property
    def storage(self):
        """Lazy load storage to avoid circular imports."""
        if self._storage is None:
            from pp.core.storage import storage as default_storage
            self._storage = default_storage
        return self._storage
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Priority: Environment variable > User config > Default
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        # Check environment variable first
        env_key = f"{self.ENV_PREFIX}{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        
        # Check user config
        user_config = self._get_user_config()
        if key in user_config:
            return user_config[key]
        
        # Check defaults
        if key in self.DEFAULTS:
            return self.DEFAULTS[key]
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value in user config.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        user_config = self._get_user_config()
        user_config[key] = value
        self.storage.save_config(user_config)
        self._cache = user_config
    
    def delete(self, key: str) -> bool:
        """
        Delete a configuration value.
        
        Args:
            key: Configuration key to delete
            
        Returns:
            True if deleted, False if not found
        """
        user_config = self._get_user_config()
        if key in user_config:
            del user_config[key]
            self.storage.save_config(user_config)
            self._cache = user_config
            return True
        return False
    
    def all(self) -> dict[str, Any]:
        """Get all configuration values (merged)."""
        result = self.DEFAULTS.copy()
        result.update(self._get_user_config())
        
        # Apply environment overrides
        for key in result.keys():
            env_key = f"{self.ENV_PREFIX}{key.upper()}"
            env_value = os.environ.get(env_key)
            if env_value is not None:
                result[key] = env_value
        
        return result
    
    def _get_user_config(self) -> dict:
        """Get user configuration (cached)."""
        if self._cache is None:
            self._cache = self.storage.get_config()
        return self._cache
    
    def get_storage_dir(self) -> Path:
        """Get the storage directory (supports env override)."""
        env_dir = os.environ.get(f"{self.ENV_PREFIX}STORAGE_DIR")
        if env_dir:
            return Path(env_dir)
        return self.storage.base_dir


# Global config instance
config = Config()
