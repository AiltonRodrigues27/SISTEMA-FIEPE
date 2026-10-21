from app.shared.domain.errors import ConflictError


class PlayerNotInSquad(ConflictError):
    """Jogador escalado que não é do elenco do clube."""


class PlayerUnavailable(ConflictError):
    """Jogador escalado que não pode jogar (DOENTE)."""


class PositionsDoNotFormFormation(ConflictError):
    """Posições dos titulares que não fecham a formação escolhida."""
