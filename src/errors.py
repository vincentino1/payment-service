from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class ApiError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict | None = None

    def to_payload(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details or {},
                "traceId": str(uuid.uuid4()),
            }
        }

