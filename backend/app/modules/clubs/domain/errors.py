from app.shared.domain.errors import ConflictError, InvalidDataError, NotFoundError


class ClubNotFound(NotFoundError):
    """Clube inexistente."""


class InvalidClubData(InvalidDataError):
    """Dados do clube que cruzam campos e não são aceitos (sigla que não corresponde ao nome)."""


class InvalidClubQuery(InvalidDataError):
    """Parâmetro de listagem de clubes inválido."""


class ContractNotFound(NotFoundError):
    """O jogador do clube não tem contrato ativo."""


class InvalidLoyaltyDate(InvalidDataError):
    """O fim da fidelidade não é futuro ou passa de 1.095 dias."""


class SquadFull(ConflictError):
    """O elenco do clube já tem o máximo de jogadores (RN14)."""


class InsufficientCash(ConflictError):
    """O caixa do clube não cobre o valor."""


class ClubNameAlreadyExists(ConflictError):
    """Já existe um clube com esse nome (RN10)."""


class AcronymAlreadyExists(ConflictError):
    """Já existe um clube com essa sigla."""


class ClubLimitReached(ConflictError):
    """A liga já tem o máximo de clubes."""
