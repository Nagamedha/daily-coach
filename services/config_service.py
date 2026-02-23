import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ConfigService:
    """Centralized configuration management service."""
    
    def __init__(self):
        """Initialize and validate configuration."""
        self._validate_config()
    
    def get_supabase_url(self) -> str:
        """Get Supabase URL from environment."""
        return os.getenv('SUPABASE_URL', '')
    
    def get_supabase_key(self) -> str:
        """Get Supabase API key from environment."""
        return os.getenv('SUPABASE_KEY', '')
    
    def get_claude_api_key(self) -> str:
        """Get Claude API key from environment."""
        return os.getenv('CLAUDE_API_KEY', '')
    
    def get_claude_model(self) -> str:
        """Get AI model name from environment."""
        model = os.getenv('CLAUDE_MODEL')
        if not model:
            raise ConfigurationError("Missing required environment variable: CLAUDE_MODEL")
        return model
    
    def get_port(self) -> int:
        """Get server port from environment with default."""
        return int(os.getenv('PORT', '5000'))
    
    def get_debug_mode(self) -> bool:
        """Get debug mode from environment with default."""
        return os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        required_vars = {
            'SUPABASE_URL': self.get_supabase_url(),
            'SUPABASE_KEY': self.get_supabase_key(),
            'CLAUDE_API_KEY': self.get_claude_api_key(),
            'CLAUDE_MODEL': os.getenv('CLAUDE_MODEL'),
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                raise ConfigurationError(f"Missing required environment variable: {var_name}")
        
        # Validate URL format for Supabase
        supabase_url = self.get_supabase_url()
        if not supabase_url.startswith('https://'):
            raise ConfigurationError("SUPABASE_URL must be a valid HTTPS URL")
    
    def validate_config(self) -> None:
        """Public method to validate configuration."""
        self._validate_config()
