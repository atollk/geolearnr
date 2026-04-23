import dataclasses
import pathlib
from collections.abc import AsyncGenerator

from pydantic_ai import Agent, BinaryContent, RunContext

from guess_explainr import state


@dataclasses.dataclass(frozen=True)
class AgentDependency:
    compare_country_ids: list[str]
    user_questions: str


def _make_agent() -> Agent[AgentDependency]:
    state_config = state.get_config()
    prompt = (
        "You are an experienced teacher of the game GeoGuessr.\n"
        "You will be provided an image of a Google Street View location and a task to explain to "
        "the user,so that they can learn to become better at the game from it.\n"
        "\n"
        "You will also be provided with a set of relevant guides.\n"
        "These explain clues that might be used by players of the game to "
        "distinguish locations from another.\n"
        "Base all your analysis and explanations on content provided by these guides.\n",
        "Output your response in plain text or Markdown formatting.",
    )

    assert state_config.ai_provider is not None
    _, model = state_config.ai_provider.to_pydantic(
        model_name=state_config.ai_model or "", api_key=state_config.api_key or ""
    )

    agent = Agent(
        model,
        deps_type=AgentDependency,
        instructions=prompt,
    )

    @agent.instructions
    def task(ctx: RunContext[AgentDependency]) -> str:
        return (
            f"You will be given guides for the following countries: "
            f"{ctx.deps.compare_country_ids}. "
            f"Only consider these as options for where the location might be. "
            f"The user also asked: {ctx.deps.user_questions}"
        )

    return agent


def _load_plonkit_guide(country_id: str) -> BinaryContent:
    dir = pathlib.Path("src/guess_explainr/static/files/plonkit")
    filename = dir / f"{country_id}.pdf"
    return BinaryContent(data=filename.read_bytes(), media_type="application/pdf")


def _load_panorama_image() -> BinaryContent:
    image_bytes = state.in_memory_state.panorama_image_bytes
    if not image_bytes:
        raise ValueError("Panorama image not available in state")
    return BinaryContent(data=image_bytes, media_type="image/jpeg")


async def run_analysis(
    compare_country_ids: list[str],
    user_questions: str,
) -> str:
    agent = _make_agent()
    guides = [_load_plonkit_guide(country_id) for country_id in compare_country_ids]
    image_prompt = [
        "This is the Street View panorama image that you are supposed to analyze:",
        _load_panorama_image(),
    ]

    response = await agent.run(
        user_prompt=image_prompt + guides,
        deps=AgentDependency(
            compare_country_ids=compare_country_ids, user_questions=user_questions
        ),
    )

    return response.response.text or "<no response>"


async def stream_analysis(
    compare_country_ids: list[str],
    user_questions: str,
) -> AsyncGenerator[str, None]:
    agent = _make_agent()
    guides = [_load_plonkit_guide(country_id) for country_id in compare_country_ids]
    image_prompt = [
        "This is the Street View panorama image that you are supposed to analyze:",
        _load_panorama_image(),
    ]
    async with agent.run_stream(
        user_prompt=image_prompt + guides,
        deps=AgentDependency(
            compare_country_ids=compare_country_ids, user_questions=user_questions
        ),
    ) as result:
        async for text in result.stream_text(delta=True):
            yield text
