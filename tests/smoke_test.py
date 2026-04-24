"""
Smoke test for an installed guess_explainr wheel or sdist.

Runs as a plain script (no test framework) via:
  uv run --isolated --no-project --with dist/*.whl tests/smoke_test.py
  uv run --isolated --no-project --with dist/*.tar.gz tests/smoke_test.py

Checks that the package is importable and its core objects are wired up
correctly.  This deliberately avoids anything that requires network access,
LLM credentials, or Street View API keys.
"""

import sys


def ok(msg: str) -> None:
    print(f" OK  {msg}")


def fail(msg: str) -> None:
    print(f"FAIL {msg}", file=sys.stderr)
    sys.exit(1)


print("=== guess_explainr smoke test ===\n")

# ---------------------------------------------------------------------------
# Package import
# ---------------------------------------------------------------------------
try:
    import guess_explainr  # noqa: F401

    ok("import guess_explainr")
except ImportError as e:
    fail(f"import guess_explainr: {e}")

# ---------------------------------------------------------------------------
# ModelProvider enum
# ---------------------------------------------------------------------------
try:
    from guess_explainr.model_provider import ModelProvider

    assert ModelProvider("openai") is ModelProvider.OpenAI
    assert ModelProvider("anthropic") is ModelProvider.Anthropic
    assert ModelProvider("google") is ModelProvider.Google
    assert len(list(ModelProvider)) == 3
    ok("ModelProvider enum (3 providers)")
except Exception as e:
    fail(f"ModelProvider: {e}")

# ---------------------------------------------------------------------------
# State module — config read/write round-trip (no real file required)
# ---------------------------------------------------------------------------
try:
    from guess_explainr import state

    # get_config must return a StateConfig regardless of whether a config file
    # exists on the smoke-test machine.
    cfg = state.get_config()
    assert isinstance(cfg, state.StateConfig), f"expected StateConfig, got {type(cfg)}"
    ok("state.get_config()")
except Exception as e:
    fail(f"state module: {e}")

# ---------------------------------------------------------------------------
# Litestar app object
# ---------------------------------------------------------------------------
try:
    from litestar import Litestar

    from guess_explainr.app import app

    assert isinstance(app, Litestar), f"expected Litestar instance, got {type(app)}"
    ok("app is a Litestar instance")
except Exception as e:
    fail(f"app object: {e}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
try:
    from guess_explainr.__main__ import main

    assert callable(main)
    ok("main() entry point is callable")
except Exception as e:
    fail(f"entry point: {e}")

print("\nAll checks passed.")
