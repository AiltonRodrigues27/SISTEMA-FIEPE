class DomainError(Exception):
    """Classe base de todo erro de regra de negócio."""


class NotFoundError(DomainError):
    """Recurso que não existe."""


class InvalidDataError(DomainError):
    """Dado inválido, que cruza campos ou depende do contexto."""


class ConflictError(DomainError):
    """Regra de negócio violada pelo estado atual."""
