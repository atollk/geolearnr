from pydantic import BaseModel


class ConfigRequest(BaseModel):
    provider: str
    model: str
    api_key: str


class ProcessUrlRequest(BaseModel):
    url: str


class CompareRequest(BaseModel):
    country: str
    compare_countries: list[str]
    questions: str


class ChatRequest(BaseModel):
    message: str
    context: str
