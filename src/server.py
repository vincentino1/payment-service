from __future__ import annotations

import os

from dotenv import load_dotenv

from .app import create_app


def main():
    load_dotenv()

    if not os.environ.get("DATABASE_URL"):
        raise SystemExit(
            "DATABASE_URL is required. Example:\n"
            "  export DATABASE_URL='postgresql+psycopg://devEccomerce:devEccomerce$@localhost:5432/vogueThreads'\n"
            "Then run:\n"
            "  alembic upgrade head\n"
            "  python -m src.server\n"
        )

    app = create_app()

    port = int(os.environ.get("PORT", "5002"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
