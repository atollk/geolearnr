import urllib.parse

from litestar import post
from litestar.exceptions import HTTPException

from guess_explainr.models import CompareRequest


@post("/compare")
async def compare(data: CompareRequest) -> dict:
    if not data.compare_countries:
        raise HTTPException(status_code=400, detail="Select at least one country")
    countries_param = urllib.parse.quote(",".join(data.compare_countries))
    questions_param = urllib.parse.quote(data.questions or "")
    stream_url = f"/api/analysis-stream?countries={countries_param}&questions={questions_param}"
    return {"stream_url": stream_url, "context": ", ".join(data.compare_countries)}
