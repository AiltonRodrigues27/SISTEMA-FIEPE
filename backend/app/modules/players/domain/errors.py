from app.shared.domain.errors import ConflictError, InvalidDataError, NotFoundError


class PlayerNotFound(NotFoundError):
    """Jogador inexistente ou excluído."""


class InvalidPlayerData(InvalidDataError):
    """Dados do jogador que cruzam campos e não são aceitos."""


class PositionChangeNotAllowed(ConflictError):
    """Jogador com clube não muda de posição."""


class AgeCannotDecrease(ConflictError):
    """A idade do jogador não pode diminuir."""


class InvalidConditionTransition(ConflictError):
    """Mudança de condição não permitida (de DOENTE direto para APTO)."""


class PlayerHasClub(ConflictError):
    """Jogador com clube não pode ser excluído."""


class PlayerNotFree(ConflictError):
    """Jogador que já tem clube não pode ser comprado."""


class PlayerIsFree(ConflictError):
    """Jogador livre não pode ser vendido."""
