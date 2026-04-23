import enum

import niquests
from litestar import get, post
from litestar.response import Template
from pydantic import BaseModel

from guess_explainr import state


class ModelProvider(enum.Enum):
    OpenAI = "openai"
    Anthropic = "anthropic"
    Google = "google"

    async def load_model_list(self, key: str) -> list[str]:
        async with niquests.AsyncSession() as s:
            match self:
                case ModelProvider.OpenAI:
                    r = await s.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {key}"},
                    )
                    r.raise_for_status()
                    _CHAT_PREFIXES = ("gpt-", "o1", "o3", "chatgpt-")
                    ids: list[str] = [
                        m["id"]
                        for m in r.json()["data"]
                        if any(m["id"].startswith(p) for p in _CHAT_PREFIXES)
                    ]
                    return sorted(ids)

                case ModelProvider.Anthropic:
                    r = await s.get(
                        "https://api.anthropic.com/v1/models",
                        headers={
                            "x-api-key": key,
                            "anthropic-version": "2023-06-01",
                        },
                    )
                    r.raise_for_status()
                    return [m["id"] for m in r.json()["data"]]

                case ModelProvider.Google:
                    r = await s.get(
                        "https://generativelanguage.googleapis.com/v1beta/models",
                        params={"key": key},
                    )
                    r.raise_for_status()
                    return [
                        m["name"].removeprefix("models/")
                        for m in r.json()["models"]
                        if "generateContent" in m.get("supportedGenerationMethods", [])
                    ]


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
    return {"configured": state.get_config() is not None}


class ConfigRequest(BaseModel):
    provider: str
    model: str
    api_key: str


@post("/config")
async def save_config(data: ConfigRequest) -> Template:
    with state.modify_config() as config:
        config.ai_provider = data.provider
        config.ai_model = data.model
    return Template(template_name="partials/config_success.html", context={})
