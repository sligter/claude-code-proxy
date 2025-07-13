# Claude Code Proxy

A proxy server that enables **Claude Code** to work with OpenAI-compatible API providers. Convert Claude API requests to OpenAI API calls, allowing you to use various LLM providers through the Claude Code CLI.

![Claude Code Proxy](demo.png)

## Features

- **Full Claude API Compatibility**: Complete `/v1/messages` endpoint support
- **Multi-Provider Routing**: Independently route "big" and "small" model requests to different providers (e.g., OpenAI, Azure, Ollama).
- **Flexible Model Mapping**: Configure distinct API keys, base URLs, and model names for each route.
- **Function Calling**: Complete tool use support with proper conversion
- **Streaming Responses**: Real-time SSE streaming support
- **Image Support**: Base64 encoded image input
- **Error Handling**: Comprehensive error handling and logging

## Quick Start

### 1. Install Dependencies

```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your API configuration
```

### docker
docker run --name cc-proxy -p 8082:8082 -v "${PWD}\.env:/app/.env" bradleylzh/cc-proxy:latest


### 3. Start Server

```bash
# Direct run
python start_proxy.py

# Or with UV
uv run claude-code-proxy
```

### 4. Use with Claude Code

```bash
ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN="some-api-key" claude
```

## Configuration

Configuration is managed via an `.env` file. Copy the example file and edit it to match your setup:

```bash
cp .env.example .env
# Edit .env and add your API configuration
```

### Environment Variables

The proxy supports separate configurations for a "big" model (used for complex tasks like `sonnet` or `opus` requests) and a "small" model (used for faster tasks like `haiku` requests).

#### Big Model Configuration:
- `BIG_MODEL_PROVIDER`: (Optional) The provider name (e.g., `openai`, `azure`, `ollama`). Defaults to `openai`.
- `BIG_MODEL_API_KEY`: Your API key for the big model provider.
- `BIG_MODEL_BASE_URL`: The base URL for the big model's API. Defaults to `https://api.openai.com/v1`.
- `BIG_MODEL_NAME`: The specific model name to use (e.g., `gpt-4o`).
- `BIG_MODEL_AZURE_API_VERSION`: (Optional) The API version, required for Azure OpenAI.

#### Small Model Configuration:
- `SMALL_MODEL_PROVIDER`: (Optional) The provider name. Defaults to `openai`.
- `SMALL_MODEL_API_KEY`: Your API key for the small model provider.
- `SMALL_MODEL_BASE_URL`: The base URL for the small model's API. Defaults to `https://api.openai.com/v1`.
- `SMALL_MODEL_NAME`: The specific model name to use (e.g., `gpt-4o-mini`).
- `SMALL_MODEL_AZURE_API_VERSION`: (Optional) The API version, required for Azure OpenAI.

**Note:** You can use the same provider and API key for both models, or configure them to use different providers entirely (e.g., OpenAI for the big model and a local Ollama instance for the small model).

#### Server Settings:
- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8082`)
- `LOG_LEVEL` - Logging level (default: `WARNING`)

#### Performance:
- `MAX_TOKENS_LIMIT` - Token limit (default: `4096`)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: `90`)

### Model Mapping

The proxy maps Claude model requests to your configured models:

| Claude Request                 | Mapped To     | Environment Variable   |
| ------------------------------ | ------------- | ---------------------- |
| Models with "haiku"            | Small Model   | `SMALL_MODEL_NAME`     |
| Models with "sonnet" or "opus" | Big Model     | `BIG_MODEL_NAME`      |

### Provider Examples

#### Example 1: Using OpenAI for Both Models

```bash
# Provider for both is openai (default)
BIG_MODEL_API_KEY="sk-your-openai-key"
BIG_MODEL_NAME="gpt-4o"

SMALL_MODEL_API_KEY="sk-your-openai-key" # Can be the same key
SMALL_MODEL_NAME="gpt-4o-mini"
```

#### Example 2: Azure OpenAI for Big, OpenAI for Small

```bash
# Big Model: Azure
BIG_MODEL_PROVIDER="azure"
BIG_MODEL_API_KEY="your-azure-key"
BIG_MODEL_BASE_URL="https://your-resource.openai.azure.com/"
BIG_MODEL_NAME="gpt-4"
BIG_MODEL_AZURE_API_VERSION="2024-02-01"

# Small Model: OpenAI
SMALL_MODEL_PROVIDER="openai"
SMALL_MODEL_API_KEY="sk-your-openai-key"
SMALL_MODEL_BASE_URL="https://api.openai.com/v1"
SMALL_MODEL_NAME="gpt-4o-mini"
```

#### Example 3: Local Models (Ollama)

```bash
# Big Model: Llama 3.1 70B via Ollama
BIG_MODEL_PROVIDER="ollama"
BIG_MODEL_API_KEY="dummy-key" # Required but can be dummy
BIG_MODEL_BASE_URL="http://localhost:11434/v1"
BIG_MODEL_NAME="llama3.1:70b"

# Small Model: Llama 3.1 8B via Ollama
SMALL_MODEL_PROVIDER="ollama"
SMALL_MODEL_API_KEY="dummy-key"
SMALL_MODEL_BASE_URL="http://localhost:11434/v1"
SMALL_MODEL_NAME="llama3.1:8b"
```

## Usage Examples

### Basic Chat

```python
import httpx

response = httpx.post(
    "http://localhost:8082/v1/messages",
    json={
        "model": "claude-3-5-sonnet-20241022",  # Maps to BIG_MODEL
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)
```

## Integration with Claude Code

This proxy is designed to work seamlessly with Claude Code CLI:

```bash
# Start the proxy
python start_proxy.py

# Use Claude Code with the proxy
ANTHROPIC_BASE_URL=http://localhost:8082 claude

# Or set permanently
export ANTHROPIC_BASE_URL=http://localhost:8082
claude
```

## Testing

Test the proxy functionality:

```bash
# Run comprehensive tests
python src/test_claude_to_openai.py
```

## Development

### Using UV

```bash
# Install dependencies
uv sync

# Run server
uv run claude-code-proxy

# Format code
uv run black src/
uv run isort src/

# Type checking
uv run mypy src/
```

### Project Structure

```
claude-code-proxy/
├── src/
│   ├── main.py  # Main server
│   ├── test_claude_to_openai.py    # Tests
│   └── [other modules...]
├── start_proxy.py                  # Startup script
├── .env.example                    # Config template
└── README.md                       # This file
```

## Performance

- **Async/await** for high concurrency
- **Connection pooling** for efficiency
- **Streaming support** for real-time responses
- **Configurable timeouts** and retries
- **Smart error handling** with detailed logging

## License

MIT License
