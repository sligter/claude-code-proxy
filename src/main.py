from fastapi import FastAPI
from src.api.endpoints import router as api_router
import uvicorn
import sys
from src.core.config import config

app = FastAPI(title="Claude-to-OpenAI API Proxy", version="1.0.0")

app.include_router(api_router)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Claude-to-OpenAI API Proxy v1.0.0")
        print("")
        print("Usage: python src/main.py")
        print("")
        print("Environment variables are configured in the .env file.")
        print("See .env for a full list of configurable options including:")
        print("  - BIG_MODEL_PROVIDER, BIG_MODEL_API_KEY, BIG_MODEL_BASE_URL, BIG_MODEL_NAME")
        print("  - SMALL_MODEL_PROVIDER, SMALL_MODEL_API_KEY, SMALL_MODEL_BASE_URL, SMALL_MODEL_NAME")
        print("  - HOST, PORT, LOG_LEVEL, etc.")
        print("")
        sys.exit(0)

    # Configuration summary
    print("🚀 Claude-to-OpenAI API Proxy v1.0.0")
    print(f"✅ Configuration loaded successfully")
    print( "   --- Big Model ---")
    print(f"   Provider: {config.big_model_provider}")
    print(f"   Base URL: {config.big_model_base_url}")
    print(f"   Model Name: {config.big_model_name}")
    print( "   --- Small Model ---")
    print(f"   Provider: {config.small_model_provider}")
    print(f"   Base URL: {config.small_model_base_url}")
    print(f"   Model Name: {config.small_model_name}")
    print( "   --- Server & Performance ---")
    print(f"   Max Tokens Limit: {config.max_tokens_limit}")
    print(f"   Request Timeout: {config.request_timeout}s")
    print(f"   Server: {config.host}:{config.port}")
    print("")

    # Parse log level - extract just the first word to handle comments
    log_level = config.log_level.split()[0].lower()
    
    # Validate and set default if invalid
    valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
    if log_level not in valid_levels:
        log_level = 'info'

    # Start server
    uvicorn.run(
        "src.main:app",
        host=config.host,
        port=config.port,
        log_level=log_level,
        reload=False,
    )


if __name__ == "__main__":
    main()
