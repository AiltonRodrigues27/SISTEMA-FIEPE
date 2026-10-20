from app.shared.domain.errors import ConflictError, InvalidDataError, NotFoundError


class ClubNotFound(NotFoundError):
    """Clube inexistente."""


class InvalidClubData(InvalidDataError):
    """Dados do clube que cruzam campos e não são aceitos (sigla que não corresponde ao nome)."""


class InvalidClubQuery(InvalidDataError):
    """Parâmetro de listagem de clubes inválido."""


class ClubNameAlreadyExists(ConflictError):
    """Já existe um clube com esse nome (RN10)."""


class AcronymAlreadyExists(ConflictError):
    """Já existe um clube com essa sigla."""


class ClubLimitReached(ConflictError):
    """A liga já tem o máximo de clubes."""
