from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime
import uuid

from src.core.config import config
from src.core.logging import logger
from src.core.client import OpenAIClient
from src.models.claude import ClaudeMessagesRequest, ClaudeTokenCountRequest
from src.conversion.request_converter import convert_claude_to_openai
from src.conversion.response_converter import (
    convert_openai_to_claude_response,
    convert_openai_streaming_to_claude_with_cancellation,
)
from src.core.model_manager import model_manager

router = APIRouter()

@router.post("/v1/messages")
async def create_message(request: ClaudeMessagesRequest, http_request: Request):
    try:
        logger.debug(
            f"Processing Claude request: model={request.model}, stream={request.stream}"
        )

        # Get model-specific configuration from the manager
        model_config = model_manager.get_model_config(request.model)
        
        # This is the actual model name to be passed to the provider
        openai_model_name = model_config["model_name"]

        # Dynamically create an OpenAI client for this specific request
        openai_client = OpenAIClient(
            api_key=model_config["api_key"],
            base_url=model_config["base_url"],
            timeout=config.request_timeout,
            api_version=model_config["api_version"],
        )

        # Generate a unique ID for this request for cancellation tracking
        request_id = str(uuid.uuid4())

        # Convert the incoming Claude-formatted request to the OpenAI format
        openai_request = convert_claude_to_openai(request, openai_model_name)

        # Before making the API call, check if the client has already disconnected
        if await http_request.is_disconnected():
            logger.warning(f"Client disconnected before processing request {request_id}")
            raise HTTPException(status_code=499, detail="Client disconnected")

        if request.stream:
            try:
                # For streaming responses, create an async generator
                openai_stream = openai_client.create_chat_completion_stream(
                    openai_request, request_id
                )
                # Stream the converted response back to the client
                return StreamingResponse(
                    convert_openai_streaming_to_claude_with_cancellation(
                        openai_stream,
                        request,
                        logger,
                        http_request,
                        openai_client,
                        request_id,
                    ),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "*",
                    },
                )
            except HTTPException as e:
                # Handle potential HTTP exceptions during streaming setup
                logger.error(f"Streaming error for request {request_id}: {e.detail}")
                error_message = OpenAIClient.classify_openai_error(e.detail)
                error_response = {
                    "type": "error",
                    "error": {"type": "api_error", "message": error_message},
                }
                # Return a JSON error response even for a streaming request
                return JSONResponse(status_code=e.status_code, content=error_response)
        else:
            # For non-streaming responses, make a single API call
            openai_response = await openai_client.create_chat_completion(
                openai_request, request_id
            )
            # Convert the OpenAI response back to the Claude format
            claude_response = convert_openai_to_claude_response(
                openai_response, request
            )
            return claude_response
            
    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        import traceback
        logger.error(f"""Unexpected error processing request: {e}
{traceback.format_exc()}""")
        # Classify the error to provide a more helpful message to the client
        error_message = OpenAIClient.classify_openai_error(str(e))
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/v1/messages/count_tokens")
async def count_tokens(request: ClaudeTokenCountRequest):
    try:
        total_chars = 0
        if request.system:
            if isinstance(request.system, str):
                total_chars += len(request.system)
            elif isinstance(request.system, list):
                for block in request.system:
                    if hasattr(block, "text"):
                        total_chars += len(block.text)
        for msg in request.messages:
            if msg.content is None:
                continue
            elif isinstance(msg.content, str):
                total_chars += len(msg.content)
            elif isinstance(msg.content, list):
                for block in msg.content:
                    if hasattr(block, "text") and block.text is not None:
                        total_chars += len(block.text)
        estimated_tokens = max(1, total_chars // 4)
        return {"input_tokens": estimated_tokens}
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "big_model_api_configured": bool(config.big_model_api_key),
        "small_model_api_configured": bool(config.small_model_api_key),
        "big_model_api_key_valid": config.validate_api_key(config.big_model_api_key),
        "small_model_api_key_valid": config.validate_api_key(config.small_model_api_key),
    }


@router.get("/test-connection")
async def test_connection():
    """Test API connectivity to configured providers."""
    results = {}
    
    # Test Big Model Connection
    try:
        big_model_client = OpenAIClient(
            api_key=config.big_model_api_key,
            base_url=config.big_model_base_url,
            timeout=10, # Shorter timeout for tests
            api_version=config.big_model_azure_api_version,
        )
        test_response = await big_model_client.create_chat_completion(
            {
                "model": config.big_model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5,
            }
        )
        results["big_model_connection"] = {
            "status": "success",
            "provider": config.big_model_provider,
            "model_used": config.big_model_name,
            "response_id": test_response.get("id", "unknown"),
        }
    except Exception as e:
        results["big_model_connection"] = {
            "status": "failed",
            "provider": config.big_model_provider,
            "model_used": config.big_model_name,
            "error": OpenAIClient.classify_openai_error(str(e)),
        }

    # Test Small Model Connection
    try:
        small_model_client = OpenAIClient(
            api_key=config.small_model_api_key,
            base_url=config.small_model_base_url,
            timeout=10, # Shorter timeout for tests
            api_version=config.small_model_azure_api_version,
        )
        test_response = await small_model_client.create_chat_completion(
            {
                "model": config.small_model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5,
            }
        )
        results["small_model_connection"] = {
            "status": "success",
            "provider": config.small_model_provider,
            "model_used": config.small_model_name,
            "response_id": test_response.get("id", "unknown"),
        }
    except Exception as e:
        results["small_model_connection"] = {
            "status": "failed",
            "provider": config.small_model_provider,
            "model_used": config.small_model_name,
            "error": OpenAIClient.classify_openai_error(str(e)),
        }

    return JSONResponse(content=results)


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Claude-to-OpenAI API Proxy v1.0.0",
        "status": "running",
        "config": {
            "max_tokens_limit": config.max_tokens_limit,
            "big_model": {
                "provider": config.big_model_provider,
                "name": config.big_model_name,
                "base_url": config.big_model_base_url,
                "api_key_configured": bool(config.big_model_api_key),
            },
            "small_model": {
                "provider": config.small_model_provider,
                "name": config.small_model_name,
                "base_url": config.small_model_base_url,
                "api_key_configured": bool(config.small_model_api_key),
            },
        },
        "endpoints": {
            "messages": "/v1/messages",
            "count_tokens": "/v1/messages/count_tokens",
            "health": "/health",
            "test_connection": "/test-connection",
        },
    }
