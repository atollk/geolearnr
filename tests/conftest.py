import pytest

from guess_explainr import state


@pytest.fixture(autouse=True)
def reset_in_memory_state():
    state.in_memory_state.panorama_id = None
    state.in_memory_state.panorama_image_bytes = None
    yield
    state.in_memory_state.panorama_id = None
    state.in_memory_state.panorama_image_bytes = None
