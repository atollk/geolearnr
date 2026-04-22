from pydantic import BaseModel


class ProcessUrlRequest(BaseModel):
    url: str


class CompareRequest(BaseModel):
    country: str
    compare_countries: list[str]
    questions: str


class ChatRequest(BaseModel):
    message: str
    context: str
