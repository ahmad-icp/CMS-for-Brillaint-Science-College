from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from redis import Redis
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.observability import RequestObservabilityMiddleware
from app.db.session import engine


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


def create_app() -> FastAPI:
    """Create and configure the College ERP FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description="Multi-tenant College ERP Platform API",
        docs_url="/docs" if settings.ENVIRONMENT.lower() != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT.lower() != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT.lower() != "production" else None,
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(
        RequestObservabilityMiddleware,
        security_headers=SECURITY_HEADERS,
    )

    @app.get("/health", tags=["health"])
    @app.get("/health/live", tags=["health"])
    def liveness() -> dict[str, str]:
        return {"status": "ok", "environment": settings.ENVIRONMENT}

    @app.get("/health/ready", tags=["health"])
    def readiness():
        checks: dict[str, str] = {}
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "unavailable"

        redis_client: Redis | None = None
        try:
            redis_client = Redis.from_url(
                settings.REDIS_URL,
                socket_connect_timeout=settings.READINESS_TIMEOUT_SECONDS,
                socket_timeout=settings.READINESS_TIMEOUT_SECONDS,
            )
            redis_client.ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "unavailable"
        finally:
            if redis_client is not None:
                redis_client.close()

        ready = all(value == "ok" for value in checks.values())
        payload = {"status": "ready" if ready else "not_ready", "checks": checks}
        if not ready:
            return JSONResponse(status_code=503, content=payload)
        return payload

    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
