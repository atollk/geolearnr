from litestar import get, post
from litestar.response import Template
from pydantic import BaseModel

from guess_explainr import state
from guess_explainr.model_provider import ModelProvider


@get("/models")
async def get_models(provider: str = "openai", api_key: str = "") -> Template:
    if not api_key:
        return Template(
            template_name="partials/models_options.html",
            context={"models": [], "placeholder": "Enter API key to load models…"},
        )
    try:
        models = await ModelProvider(provider).load_model_list(api_key)
    except Exception:
        return Template(
            template_name="partials/models_options.html",
            context={"models": [], "error": "Could not load models — check your API key"},
        )
    return Template(template_name="partials/models_options.html", context={"models": models})


@get("/config")
async def get_config() -> dict:
    return {"configured": state.get_config().ai_provider is not None}


class ConfigRequest(BaseModel):
    provider: str
    model: str
    api_key: str


@post("/config")
async def save_config(data: ConfigRequest) -> Template:
    with state.modify_config() as config:
        config.ai_provider = ModelProvider(data.provider)
        config.ai_model = data.model
        config.api_key = data.api_key
    return Template(template_name="partials/config_success.html", context={})
