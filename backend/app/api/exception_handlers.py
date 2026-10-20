import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.domain.errors import ConflictError, DomainError, InvalidDataError, NotFoundError

logger = logging.getLogger(__name__)

STATUS_BY_ERROR_FAMILY = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidDataError: status.HTTP_400_BAD_REQUEST,
    ConflictError: status.HTTP_409_CONFLICT,
}
MESSAGE_BY_STATUS = {
    status.HTTP_404_NOT_FOUND: "Recurso não encontrado.",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Método não permitido.",
}
MESSAGE_BY_VALIDATION_ERROR = {
    "missing": "campo obrigatório",
    "enum": "valor não permitido",
    "greater_than_equal": "abaixo do limite permitido",
    "less_than_equal": "acima do limite permitido",
    "json_invalid": "JSON inválido",
    "model_type": "deve ser um objeto JSON",
    "model_attributes_type": "deve ser um objeto JSON",
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return _message_response(_status_code_for(exc), str(exc))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _message_response(status.HTTP_400_BAD_REQUEST, _describe_validation_errors(exc))

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = MESSAGE_BY_STATUS.get(exc.status_code, str(exc.detail))
        return _message_response(exc.status_code, message, exc.headers)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro nao tratado em %s", request.url.path)
        return _message_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "Erro interno do servidor.")


def _status_code_for(error: DomainError) -> int:
    for family, status_code in STATUS_BY_ERROR_FAMILY.items():
        if isinstance(error, family):
            return status_code
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _message_response(
    status_code: int, message: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"message": message}, headers=headers)


def _describe_validation_errors(exc: RequestValidationError) -> str:
    return "; ".join(_describe_validation_error(error) for error in exc.errors())


def _describe_validation_error(error: dict) -> str:
    field = ".".join(str(part) for part in error["loc"][1:]) or "corpo"
    if error["type"] == "value_error":
        text = str(error["ctx"]["error"])
    else:
        text = MESSAGE_BY_VALIDATION_ERROR.get(error["type"], "valor inválido")
    return f"{field}: {text}"
