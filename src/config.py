from __future__ import annotations

import os


def _require(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"{name} env var is required")
    return value


class Settings:
    def __init__(self):
        self.service_name: str = os.environ.get("SERVICE_NAME", "checkout-payment-service")
        self.port: int = int(os.environ.get("PORT", "5002"))
        self.log_level: str = os.environ.get("LOG_LEVEL", "INFO")
        self.database_url: str = _require("DATABASE_URL")
        self.jwt_jwks_url: str | None = os.environ.get("JWT_JWKS_URL") or None


def get_settings() -> Settings:
    return Settings()
