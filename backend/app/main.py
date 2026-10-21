from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_docs import hide_validation_error_docs
from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router
from app.infrastructure.settings import settings

API_DESCRIPTION = """
API do mercado de jogadores da liga fictícia **Passe** (desafio técnico SENAI/FIEPE).

- **Base URL:** `/api/v1`. Nenhum endpoint exige autenticação.
- **Erros:** todo erro tem o corpo `{"message": "..."}`. `400` é dado, formato ou parâmetro
  inválido; `404` é recurso inexistente (inclusive id mal formado ou jogador excluído);
  `409` é regra de negócio não atendida.
- **Datas enviadas:** `AAAA-MM-DDTHH:MM-03:00`, no horário de Brasília
  (ex.: `2027-03-02T10:15-03:00`). As respostas trazem `AAAA-MM-DDTHH:MM:SS-03:00`.
- **Dinheiro:** números JSON (ex.: `41.44`).
- **Valores de lista** (`ATA`, `MAL_CONDICIONADO`, `value_desc`...) são aceitos exatamente como
  escritos, com as mesmas maiúsculas e minúsculas.
- **Filtros das listas:** os parâmetros aceitos e seus valores estão descritos em cada endpoint.
"""

app = FastAPI(
    title="Passe API",
    description=API_DESCRIPTION,
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
hide_validation_error_docs(app)

app.include_router(api_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
