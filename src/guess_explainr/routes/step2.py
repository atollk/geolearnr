import asyncio

from litestar import post
from litestar.response import Template

from guess_explainr.models import ProcessUrlRequest

_MOCK_COUNTRIES = [
    "Germany",
    "France",
    "Netherlands",
    "Poland",
    "Austria",
    "Switzerland",
    "Belgium",
    "Denmark",
]


@post("/process-url")
async def process_url(data: ProcessUrlRequest) -> Template:
    await asyncio.sleep(2.5)
    return Template(
        template_name="partials/step3_content.html",
        context={
            "country": "Germany",
            "available_countries": _MOCK_COUNTRIES,
        },
    )
