from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

ERROR_DESCRIPTIONS = {
    400: "Dado, formato ou parâmetro inválido.",
    404: "Recurso não encontrado.",
    409: "Regra de negócio não atendida.",
}
VALIDATION_SCHEMAS = ("HTTPValidationError", "ValidationError")


class ErrorResponse(BaseModel):
    message: str = Field(description="Explicação do erro, em português.")


def error_responses(*status_codes: int) -> dict[int | str, dict[str, Any]]:
    return {
        status_code: {"model": ErrorResponse, "description": ERROR_DESCRIPTIONS[status_code]}
        for status_code in status_codes
    }


def hide_validation_error_docs(app: FastAPI) -> None:
    """O FastAPI documenta 422 em toda rota com parâmetros, mas esta API responde 400."""
    build_schema = app.openapi

    def openapi() -> dict[str, Any]:
        schema = build_schema()
        for path_item in schema["paths"].values():
            for operation in path_item.values():
                operation.get("responses", {}).pop("422", None)
        for name in VALIDATION_SCHEMAS:
            schema.get("components", {}).get("schemas", {}).pop(name, None)
        return schema

    app.openapi = openapi
