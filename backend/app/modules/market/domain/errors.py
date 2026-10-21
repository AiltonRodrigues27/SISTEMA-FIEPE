from app.shared.domain.errors import ConflictError, InvalidDataError


class InvalidTransactionQuery(InvalidDataError):
    """Filtro do histórico de transações inválido (tipo ou jogador)."""


class CashLimitExceeded(ConflictError):
    """O custo total da compra passa de 50% do caixa do clube (RN13)."""


class PlayerAlreadySoldByClub(ConflictError):
    """O clube não pode comprar de volta um jogador que ele mesmo vendeu (RN12)."""
