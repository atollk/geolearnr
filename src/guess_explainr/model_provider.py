import enum

import niquests
import pydantic_ai
import pydantic_ai.models.anthropic
import pydantic_ai.models.google
import pydantic_ai.models.openai
import pydantic_ai.providers.anthropic
import pydantic_ai.providers.google
import pydantic_ai.providers.openai


class ModelProvider(enum.Enum):
    OpenAI = "openai"
    Anthropic = "anthropic"
    Google = "google"

    def to_pydantic(
        self, model_name: str, api_key: str
    ) -> tuple[pydantic_ai.providers.Provider, pydantic_ai.models.Model]:
        match self:
            case ModelProvider.OpenAI:
                provider = pydantic_ai.providers.openai.OpenAIProvider(api_key=api_key)
                model = pydantic_ai.models.openai.OpenAIResponsesModel(
                    provider=provider, model_name=model_name
                )
            case ModelProvider.Anthropic:
                provider = pydantic_ai.providers.anthropic.AnthropicProvider(api_key=api_key)
                model = pydantic_ai.models.anthropic.AnthropicModel(
                    provider=provider, model_name=model_name
                )
            case ModelProvider.Google:
                provider = pydantic_ai.providers.google.GoogleProvider(api_key=api_key)
                model = pydantic_ai.models.google.GoogleModel(
                    provider=provider, model_name=model_name
                )
        return provider, model

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
