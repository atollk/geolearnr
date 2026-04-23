from litestar import post
from litestar.exceptions import HTTPException
from litestar.response import Template

from guess_explainr import state
from guess_explainr.ai import run_analysis
from guess_explainr.models import CompareRequest


@post("/compare")
async def compare(data: CompareRequest) -> Template:
    try:
        analysis = await run_analysis(data.compare_countries, data.questions)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    context_text = f"{', '.join(data.compare_countries)}"
    return Template(
        template_name="partials/step4_content.html",
        context={"analysis": analysis, "context": context_text},
    )


def _load_location_panorama() -> bytes:
    panorama_id = state.in_memory_state.panorama_id
    assert panorama_id is not None
    # TODO
    return b""
