import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import health, scan, result, market

_REQUEST_LOGGER = logging.getLogger("pokeauthai.request")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.service_name, version=settings.version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def observe_requests_and_attach_correlation_id(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        started_at = time.perf_counter()
        path = request.url.path
        method = request.method.upper()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration_ms = (time.perf_counter() - started_at) * 1000.0
            _REQUEST_LOGGER.error(
                "http_request_exception request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f client_host=%s",
                request_id,
                method,
                path,
                status_code,
                duration_ms,
                request.client.host if request.client else "unknown",
            )
            raise

        duration_ms = (time.perf_counter() - started_at) * 1000.0
        _REQUEST_LOGGER.info(
            "http_request request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f client_host=%s",
            request_id,
            method,
            path,
            status_code,
            duration_ms,
            request.client.host if request.client else "unknown",
        )

        response.headers["X-Request-Id"] = request_id
        return response

    app.include_router(health.router)
    app.include_router(scan.router)
    app.include_router(result.router)
    app.include_router(market.router)
    return app


app = create_app()
