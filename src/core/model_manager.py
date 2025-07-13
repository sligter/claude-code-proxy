from src.core.config import config

class ModelManager:
    def __init__(self, config):
        self.config = config
    
    def get_model_config(self, claude_model: str) -> dict:
        """Map Claude model names to the corresponding provider configuration."""
        # If it's already an OpenAI model, assume it maps to the BIG model provider for now.
        # This is a fallback and could be improved.
        if claude_model.startswith("gpt-") or claude_model.startswith("o1-"):
             return {
                "model_name": claude_model, # return the original model name
                "api_key": self.config.big_model_api_key,
                "base_url": self.config.big_model_base_url,
                "api_version": self.config.big_model_azure_api_version
            }

        model_lower = claude_model.lower()
        if 'haiku' in model_lower:
            return {
                "model_name": self.config.small_model_name,
                "api_key": self.config.small_model_api_key,
                "base_url": self.config.small_model_base_url,
                "api_version": self.config.small_model_azure_api_version
            }
        # Default to big model for sonnet, opus, or unknown models
        else:
            return {
                "model_name": self.config.big_model_name,
                "api_key": self.config.big_model_api_key,
                "base_url": self.config.big_model_base_url,
                "api_version": self.config.big_model_azure_api_version
            }

model_manager = ModelManager(config)