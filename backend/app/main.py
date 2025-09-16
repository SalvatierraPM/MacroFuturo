from __future__ import annotations

from fastapi import FastAPI

from .api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="MacroFuturo — Novel Generator API",
        version="0.3.0",
        description="Pipeline que genera narrativa auditada y ledger explicativo.",
    )

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(router)
    return app


app = create_app()
