import asyncio
import uuid
from collections.abc import AsyncGenerator

from litestar import get
from litestar.exceptions import HTTPException
from litestar.response import ServerSentEvent
from litestar.types import SSEData


@get("/chat")
async def chat(message: str, context: str = "") -> ServerSentEvent:
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    async def _token_stream() -> AsyncGenerator[SSEData, None]:
        mock = (
            f"This is a mock response to: {message!r}. "
            "Real answers will come from the configured LLM. "
            "The context was: " + (context or "(none)") + "."
        )
        for word in mock.split():
            await asyncio.sleep(0.08)
            yield {"data": f"<span>{word} </span>", "event": "token"}
        yield {"data": "<span></span>", "event": "done"}

    return ServerSentEvent(_token_stream())


@get("/new-chat-id")
async def new_chat_id() -> dict:
    return {"id": str(uuid.uuid4())}
