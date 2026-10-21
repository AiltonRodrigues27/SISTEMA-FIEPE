from app.shared.domain.errors import ConflictError, InvalidDataError, NotFoundError


class PlayerNotInSquad(ConflictError):
    """Jogador escalado que não é do elenco do clube."""


class PlayerUnavailable(ConflictError):
    """Jogador escalado que não pode jogar (DOENTE)."""


class PositionsDoNotFormFormation(ConflictError):
    """Posições dos titulares que não fecham a formação escolhida."""


class LineupIncomplete(ConflictError):
    """Clube sem os 5 titulares, que por isso não pode jogar."""


class SameClubMatch(InvalidDataError):
    """Partida com o mesmo clube como mandante e visitante."""


class InvalidMatchQuery(InvalidDataError):
    """Filtro do histórico de partidas inválido."""


class MatchNotFound(NotFoundError):
    """Partida que não existe."""
