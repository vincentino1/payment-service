import os
import sys
from pathlib import Path

import pytest

# Ensure `import src.*` works when running pytest from project root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app import create_app  # noqa: E402


@pytest.fixture()
def app(monkeypatch):
    # For unit tests we don't actually hit Postgres. We just need Settings to load.
    monkeypatch.setenv(
        "DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/db"),
    )
    return create_app()


@pytest.fixture()
def client(app):
    return app.test_client()
