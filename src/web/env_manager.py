import os
from dotenv import load_dotenv, set_key, find_dotenv
from pydantic import BaseModel
from typing import Dict, Any

class EnvConfig(BaseModel):
    # Big model settings
    big_model_provider: str
    big_model_api_key: str
    big_model_base_url: str
    big_model_name: str
    big_model_azure_api_version: str = ""
    
    # Small model settings
    small_model_provider: str
    small_model_api_key: str
    small_model_base_url: str
    small_model_name: str
    small_model_azure_api_version: str = ""
    
    # Server settings
    host: str
    port: int
    log_level: str
    max_tokens_limit: int
    min_tokens_limit: int
    request_timeout: int
    max_retries: int
    
    # Admin settings
    admin_username: str = "admin"
    admin_password: str = "admin"

class EnvManager:
    def __init__(self):
        self.env_file = find_dotenv()
        if not self.env_file:
            self.env_file = ".env"
        load_dotenv(self.env_file)
    
    def get_current_config(self) -> EnvConfig:
        """Get current configuration from environment variables"""
        return EnvConfig(
            # Big model settings
            big_model_provider=os.environ.get("BIG_MODEL_PROVIDER", "openai"),
            big_model_api_key=os.environ.get("BIG_MODEL_API_KEY", ""),
            big_model_base_url=os.environ.get("BIG_MODEL_BASE_URL", "https://api.openai.com/v1"),
            big_model_name=os.environ.get("BIG_MODEL_NAME", "gpt-4o"),
            big_model_azure_api_version=os.environ.get("BIG_MODEL_AZURE_API_VERSION", ""),
            
            # Small model settings
            small_model_provider=os.environ.get("SMALL_MODEL_PROVIDER", "openai"),
            small_model_api_key=os.environ.get("SMALL_MODEL_API_KEY", ""),
            small_model_base_url=os.environ.get("SMALL_MODEL_BASE_URL", "https://api.openai.com/v1"),
            small_model_name=os.environ.get("SMALL_MODEL_NAME", "gpt-4o-mini"),
            small_model_azure_api_version=os.environ.get("SMALL_MODEL_AZURE_API_VERSION", ""),
            
            # Server settings
            host=os.environ.get("HOST", "0.0.0.0"),
            port=int(os.environ.get("PORT", "8082")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            max_tokens_limit=int(os.environ.get("MAX_TOKENS_LIMIT", "8196")),
            min_tokens_limit=int(os.environ.get("MIN_TOKENS_LIMIT", "100")),
            request_timeout=int(os.environ.get("REQUEST_TIMEOUT", "90")),
            max_retries=int(os.environ.get("MAX_RETRIES", "2")),
            
            # Admin settings
            admin_username=os.environ.get("ADMIN_USERNAME", "admin"),
            admin_password=os.environ.get("ADMIN_PASSWORD", "admin")
        )
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update configuration in .env file and reload environment"""
        try:
            # Update .env file
            for key, value in new_config.items():
                key = key.upper()
                set_key(self.env_file, key, str(value))
                # Also update current environment
                os.environ[key] = str(value)

            # Reload environment
            load_dotenv(self.env_file, override=True)

            # Trigger config reload in the main application
            self._reload_app_config()

            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False

    def _reload_app_config(self):
        """Reload the main application configuration"""
        try:
            # Import here to avoid circular imports
            from src.core.config import config
            config.reload()
        except Exception as e:
            print(f"Warning: Could not reload app config: {e}")

env_manager = EnvManager()