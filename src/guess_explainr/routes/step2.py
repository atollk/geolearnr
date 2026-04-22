import glob
import re
import urllib.parse

from litestar import post
from litestar.response import Template

from guess_explainr.models import ProcessUrlRequest


def _load_country_list() -> list[str]:
    plonkit_path = "src/guess_explainr/static/files/plonkit"
    pdf_files = glob.glob("*.pdf", root_dir=plonkit_path)
    return [file.replace(".pdf", "") for file in pdf_files]


COUNTRIES = _load_country_list()


@post("/process-url")
async def process_url(data: ProcessUrlRequest) -> Template:
    print(data)
    countries = sorted([country.replace("-", " ").title() for country in COUNTRIES])
    return Template(
        template_name="partials/step3_content.html",
        context={
            "country": "",
            "available_countries": countries,
        },
    )


def extract_panorama_id(url: str) -> str:
    """Extract the Street View panorama ID from a Google Maps URL."""
    url_decoded = urllib.parse.unquote(url)
    match = re.search("panoid=([^!]+)[&$]", url_decoded)
    if match:
        return match.group(1)
    match = re.search(r"!1s([^!]+)!", url)
    if match:
        return match.group(1)
    return ""


# https://www.google.com/maps/@38.0691925,22.2390295,3a,90y,302.4h,92.61t/data=!3m7!1e1!3m5!1sC7dD4mGuuHHm6SjUq80gtw!2e0!6shttps:%2F%2Fstreetviewpixels-pa.googleapis.com%2Fv1%2Fthumbnail%3Fcb_client%3Dmaps_sv.tactile%26w%3D900%26h%3D600%26pitch%3D-2.612560000000002%26panoid%3DC7dD4mGuuHHm6SjUq80gtw%26yaw%3D302.40146!7i16384!8i8192?entry=ttu&g_ep=EgoyMDI2MDEwNC4wIKXMDSoASAFQAw%3D%3D
