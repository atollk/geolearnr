import pytest

from guess_explainr import state
from guess_explainr.model_provider import ModelProvider


@pytest.fixture(autouse=True)
def use_tmp_config(tmp_path, monkeypatch):
    """Redirect all config reads/writes to a temp directory."""
    monkeypatch.setattr(state, "_config_file", str(tmp_path / "config.json"))


# ---------------------------------------------------------------------------
# get_config
# ---------------------------------------------------------------------------


def test_get_config_missing_file():
    cfg = state.get_config()
    assert cfg.ai_provider is None
    assert cfg.ai_model is None
    assert cfg.api_key is None
    assert cfg.maps_api_key is None


def test_get_config_corrupt_json(tmp_path, monkeypatch):
    p = tmp_path / "config.json"
    p.write_text("not-valid-json{{{")
    monkeypatch.setattr(state, "_config_file", str(p))
    assert state.get_config().ai_provider is None


def test_get_config_missing_keys(tmp_path, monkeypatch):
    # Valid JSON but missing required fields → KeyError → fallback
    p = tmp_path / "config.json"
    p.write_text('{"ai_provider": "anthropic"}')
    monkeypatch.setattr(state, "_config_file", str(p))
    assert state.get_config().ai_provider is None


# ---------------------------------------------------------------------------
# set_config / get_config roundtrip
# ---------------------------------------------------------------------------


def test_roundtrip_full_config():
    cfg = state.StateConfig(
        ai_provider=ModelProvider.Anthropic,
        ai_model="claude-sonnet-4-6",
        api_key="sk-ant-test",
        maps_api_key="maps-key",
    )
    state.set_config(cfg)
    loaded = state.get_config()
    assert loaded.ai_provider == ModelProvider.Anthropic
    assert loaded.ai_model == "claude-sonnet-4-6"
    assert loaded.api_key == "sk-ant-test"
    assert loaded.maps_api_key == "maps-key"


def test_roundtrip_openai():
    cfg = state.StateConfig(
        ai_provider=ModelProvider.OpenAI,
        ai_model="gpt-4o",
        api_key="sk-openai",
    )
    state.set_config(cfg)
    loaded = state.get_config()
    assert loaded.ai_provider == ModelProvider.OpenAI
    assert loaded.ai_model == "gpt-4o"


def test_maps_api_key_empty_string_stored_as_none():
    state.set_config(state.StateConfig(maps_api_key=""))
    assert state.get_config().maps_api_key is None


def test_maps_api_key_none_stored_as_none():
    state.set_config(state.StateConfig(maps_api_key=None))
    assert state.get_config().maps_api_key is None


# ---------------------------------------------------------------------------
# modify_config context manager
# ---------------------------------------------------------------------------


def test_modify_config_persists_changes():
    with state.modify_config() as cfg:
        cfg.ai_model = "gpt-4o"
        cfg.ai_provider = ModelProvider.OpenAI
        cfg.api_key = "sk-x"
    loaded = state.get_config()
    assert loaded.ai_model == "gpt-4o"
    assert loaded.ai_provider == ModelProvider.OpenAI


def test_modify_config_reads_existing():
    state.set_config(
        state.StateConfig(ai_provider=ModelProvider.Google, ai_model="gemini-pro", api_key="key")
    )
    with state.modify_config() as cfg:
        assert cfg.ai_provider == ModelProvider.Google
        cfg.ai_model = "gemini-ultra"
    assert state.get_config().ai_model == "gemini-ultra"
