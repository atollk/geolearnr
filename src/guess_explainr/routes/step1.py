from litestar import get, post
from pydantic import BaseModel

from guess_explainr import state
from guess_explainr.model_provider import ModelProvider


@get("/models")
async def get_models(provider: str = "openai", api_key: str = "") -> dict:
    if not api_key:
        return {"models": [], "placeholder": "Enter API key to load models…"}
    try:
        models = await ModelProvider(provider).load_model_list(api_key)
    except Exception:
        return {"models": [], "error": "Could not load models — check your API key"}
    return {"models": models}


@get("/config")
async def get_config() -> dict:
    return {"configured": state.get_config().ai_provider is not None}


class ConfigRequest(BaseModel):
    provider: str
    model: str
    api_key: str
    maps_api_key: str = ""


@post("/config")
async def save_config(data: ConfigRequest) -> dict:
    with state.modify_config() as config:
        config.ai_provider = ModelProvider(data.provider)
        config.ai_model = data.model
        config.api_key = data.api_key
        config.maps_api_key = data.maps_api_key or None
    return {"success": True}
