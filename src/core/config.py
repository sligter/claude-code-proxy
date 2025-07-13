import os
import sys

# Configuration
class Config:
    def __init__(self):
        self._load_config()

    def _load_config(self):
        """Load configuration from environment variables"""
        # Provider for the BIG model
        self.big_model_provider = os.environ.get("BIG_MODEL_PROVIDER", "openai")
        self.big_model_api_key = os.environ.get("BIG_MODEL_API_KEY", os.environ.get("OPENAI_API_KEY"))
        self.big_model_base_url = os.environ.get("BIG_MODEL_BASE_URL", os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
        self.big_model_name = os.environ.get("BIG_MODEL_NAME", os.environ.get("BIG_MODEL", "gpt-4o"))
        self.big_model_azure_api_version = os.environ.get("BIG_MODEL_AZURE_API_VERSION", os.environ.get("AZURE_API_VERSION"))

        # Provider for the SMALL model
        self.small_model_provider = os.environ.get("SMALL_MODEL_PROVIDER", "openai")
        self.small_model_api_key = os.environ.get("SMALL_MODEL_API_KEY", os.environ.get("OPENAI_API_KEY"))
        self.small_model_base_url = os.environ.get("SMALL_MODEL_BASE_URL", os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
        self.small_model_name = os.environ.get("SMALL_MODEL_NAME", os.environ.get("SMALL_MODEL", "gpt-4o-mini"))
        self.small_model_azure_api_version = os.environ.get("SMALL_MODEL_AZURE_API_VERSION", os.environ.get("AZURE_API_VERSION"))

        if not self.big_model_api_key or not self.small_model_api_key:
            raise ValueError("API key not found for one or more models in environment variables")

        self.host = os.environ.get("HOST", "0.0.0.0")
        self.port = int(os.environ.get("PORT", "8082"))
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.max_tokens_limit = int(os.environ.get("MAX_TOKENS_LIMIT", "8196"))
        self.min_tokens_limit = int(os.environ.get("MIN_TOKENS_LIMIT", "100"))

        # Connection settings
        self.request_timeout = int(os.environ.get("REQUEST_TIMEOUT", "90"))
        self.max_retries = int(os.environ.get("MAX_RETRIES", "2"))

    def reload(self):
        """Reload configuration from environment variables"""
        print("🔄 Reloading configuration...")
        self._load_config()
        print("✅ Configuration reloaded successfully")
        
    def validate_api_key(self, key):
        """Basic API key validation. Just checks for presence."""
        return bool(key)

try:
    config = Config()
    print(f"\005 Configuration loaded: BIG_MODEL_PROVIDER='{config.big_model_provider}', SMALL_MODEL_PROVIDER='{config.small_model_provider}'")
except Exception as e:
    print(f"=4 Configuration Error: {e}")
    sys.exit(1)
