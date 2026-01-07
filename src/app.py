from __future__ import annotations

import json
import logging

from flask import Flask
from flask_cors import CORS

from .config import get_settings
from .db import init_engine
from .errors import ApiError
from .routes.health import bp as health_bp
from .routes.payments import bp as payments_bp


def create_app() -> Flask:
    settings = get_settings()

    app = Flask(__name__)
    CORS(app)

    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    init_engine(settings.database_url)

    app.register_blueprint(health_bp)
    app.register_blueprint(payments_bp)

    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return err.to_payload(), err.status_code

    @app.errorhandler(404)
    def handle_not_found(_):
        return ApiError(code="NOT_FOUND", message="not found", status_code=404).to_payload(), 404

    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        app.logger.exception("Unhandled error")
        payload = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "unexpected error",
                "details": {"type": err.__class__.__name__},
            }
        }
        return payload, 500

    return app

