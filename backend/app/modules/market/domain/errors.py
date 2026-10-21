from app.shared.domain.errors import ConflictError


class CashLimitExceeded(ConflictError):
    """O custo total da compra passa de 50% do caixa do clube (RN13)."""


class PlayerAlreadySoldByClub(ConflictError):
    """O clube não pode comprar de volta um jogador que ele mesmo vendeu (RN12)."""
