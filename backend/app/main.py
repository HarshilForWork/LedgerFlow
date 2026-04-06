import sys
import time
import uuid
import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

# Support running this module directly: `python app/main.py`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.users import router as users_router
from app.core.config import get_settings
from app.utils.response import (
	build_error_response,
	build_success_response,
	decode_json_body,
	should_wrap_response_envelope,
)


def _configure_logging() -> None:
	settings = get_settings()
	logging.basicConfig(
		level=getattr(logging, settings.log_level, logging.INFO),
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
	)


_configure_logging()
logger = logging.getLogger(__name__)


OPENAPI_TAGS = [
	{"name": "auth", "description": "Authentication and token management endpoints."},
	{
		"name": "transactions",
		"description": "Create, update, list, filter, and soft-delete transaction records.",
	},
	{
		"name": "dashboard",
		"description": "Dashboard analytics, category breakdowns, and financial trends.",
	},
	{"name": "users", "description": "User and role management endpoints."},
]


app = FastAPI(
	title="LedgerFlow API",
	version="1.1.0",
	description="LedgerFlow backend API for authentication, RBAC, transactions, and analytics.",
	openapi_tags=OPENAPI_TAGS,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
	request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
	start = time.perf_counter()

	try:
		response = await call_next(request)
	except Exception:
		elapsed_ms = (time.perf_counter() - start) * 1000
		logger.exception(
			"Request failed | method=%s path=%s duration_ms=%.2f request_id=%s",
			request.method,
			request.url.path,
			elapsed_ms,
			request_id,
		)
		raise

	elapsed_ms = (time.perf_counter() - start) * 1000
	response.headers["X-Request-ID"] = request_id
	logger.info(
		"Request handled | method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
		request.method,
		request.url.path,
		response.status_code,
		elapsed_ms,
		request_id,
	)
	return response


@app.middleware("http")
async def success_envelope_middleware(request: Request, call_next):
	response = await call_next(request)
	docs_paths = {"/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"}

	if not should_wrap_response_envelope(request):
		return response

	if request.url.path in docs_paths:
		return response

	if response.status_code >= 400 or response.status_code == 204:
		return response

	content_type = response.headers.get("content-type", "")
	if "application/json" not in content_type.lower():
		return response

	body = b""
	async for chunk in response.body_iterator:
		body += chunk

	try:
		payload = decode_json_body(body)
	except Exception:
		return Response(
			content=body,
			status_code=response.status_code,
			headers=dict(response.headers),
			media_type=response.media_type,
		)

	if isinstance(payload, dict) and {"success", "message", "data"}.issubset(payload.keys()):
		wrapped_payload = payload
	else:
		wrapped_payload = build_success_response(payload)

	headers = dict(response.headers)
	headers.pop("content-length", None)

	return JSONResponse(
		status_code=response.status_code,
		content=wrapped_payload,
		headers=headers,
		background=response.background,
	)


@app.exception_handler(HTTPException)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
	message = exc.detail if isinstance(exc.detail, str) else "Request failed."
	data = exc.detail if isinstance(exc.detail, (dict, list)) else None
	payload = build_error_response(message=message, data=data)
	return JSONResponse(
		status_code=exc.status_code,
		content=payload,
		headers=exc.headers,
	)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
	payload = build_error_response(message="Validation error.", data=exc.errors())
	return JSONResponse(status_code=422, content=payload)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
	logger.exception("Unhandled application error", exc_info=exc)
	payload = build_error_response(message="Internal server error.")
	return JSONResponse(status_code=500, content=payload)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
	return {"status": "ok"}


if __name__ == "__main__":
	uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

