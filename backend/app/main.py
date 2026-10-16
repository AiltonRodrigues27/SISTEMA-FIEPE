from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router
from app.infrastructure.settings import settings

app = FastAPI(
    title="Passe API",
    description="API do mercado de jogadores da liga ficticia Passe (desafio tecnico SENAI/FIEPE).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
