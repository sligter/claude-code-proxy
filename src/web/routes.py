from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
from datetime import timedelta
from typing import Dict, Any

from src.web.auth import (
    authenticate_user, create_access_token, 
    get_current_active_user, User, Token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.web.env_manager import env_manager, EnvConfig

# Create templates directory if it doesn't exist
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)

# Setup templates
templates = Jinja2Templates(directory=str(templates_dir))

# Create router
router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    # Return the admin page without server-side auth check
    # Authentication will be handled by JavaScript on the client side
    return templates.TemplateResponse("admin.html", {"request": request})

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/config", response_model=EnvConfig)
async def get_config(current_user: User = Depends(get_current_active_user)):
    return env_manager.get_current_config()

@router.post("/api/config")
async def update_config(config: Dict[str, Any], current_user: User = Depends(get_current_active_user)):
    success = env_manager.update_config(config)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update configuration"
        )
    return {
        "status": "success",
        "message": "Configuration updated and reloaded successfully! Changes are now active.",
        "updated_keys": list(config.keys())
    }

@router.get("/api/config/status")
async def get_config_status(current_user: User = Depends(get_current_active_user)):
    """Get current active configuration status"""
    from src.core.config import config
    return {
        "status": "active",
        "current_config": {
            "big_model_provider": config.big_model_provider,
            "big_model_name": config.big_model_name,
            "big_model_base_url": config.big_model_base_url,
            "small_model_provider": config.small_model_provider,
            "small_model_name": config.small_model_name,
            "small_model_base_url": config.small_model_base_url,
            "max_tokens_limit": config.max_tokens_limit,
            "request_timeout": config.request_timeout,
        },
        "timestamp": env_manager.get_current_config().dict()
    }

@router.get("/api/models")
async def get_models(base_url: str, api_key: str, current_user: User = Depends(get_current_active_user)):
    """Get available models from the specified API endpoint"""
    import httpx

    try:
        # Ensure base_url ends with /v1
        if not base_url.endswith('/v1'):
            if base_url.endswith('/'):
                base_url = base_url + 'v1'
            else:
                base_url = base_url + '/v1'

        models_url = f"{base_url}/models"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(models_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                models = []

                # Extract model names from the response
                if "data" in data and isinstance(data["data"], list):
                    models = [model.get("id", "") for model in data["data"] if model.get("id")]
                elif "models" in data and isinstance(data["models"], list):
                    models = [model.get("id", "") for model in data["models"] if model.get("id")]
                else:
                    # Fallback: try to extract from any list in the response
                    for key, value in data.items():
                        if isinstance(value, list) and value:
                            models = [item.get("id", item) for item in value if item]
                            break

                return {"success": True, "models": models}
            else:
                return {"success": False, "error": f"API returned status {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/login")