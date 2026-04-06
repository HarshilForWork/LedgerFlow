import json
from math import ceil
from typing import Any

from fastapi import Request

from app.core.config import get_settings


TRUTHY_VALUES = {"1", "true", "yes", "on"}


def should_wrap_response_envelope(request: Request | None = None) -> bool:
    settings = get_settings()
    if request is None:
        return settings.response_envelope_default

    raw_toggle = request.headers.get("x-response-envelope")
    if raw_toggle is None:
        return settings.response_envelope_default

    return raw_toggle.strip().lower() in TRUTHY_VALUES


def build_success_response(data: Any, message: str | None = None) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def build_error_response(message: str, data: Any = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": data,
    }


def build_paginated_payload(items: list[Any], page: int, limit: int, total: int) -> dict[str, Any]:
    total_pages = ceil(total / limit) if total > 0 else 0
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "data": items,
    }


def decode_json_body(body: bytes) -> Any:
    if not body:
        return None
    return json.loads(body.decode("utf-8"))
