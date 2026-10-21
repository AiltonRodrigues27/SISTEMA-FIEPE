import re
from collections.abc import Mapping

from fastapi import Request

from app.modules.market.domain.errors import InvalidTransactionQuery
from app.modules.market.domain.history import TransactionFilters
from app.modules.market.domain.transaction import TransactionType

MAX_ID = 2_147_483_647
POSITIVE_INTEGER = re.compile(r"[1-9][0-9]*")


def get_transaction_filters(request: Request) -> TransactionFilters:
    return parse_transaction_filters(request.query_params)


def parse_transaction_filters(params: Mapping[str, str]) -> TransactionFilters:
    return TransactionFilters(
        types=_parse_types(params.get("type")),
        player_id=_parse_player_id(params.get("player_id")),
    )


def _parse_types(value: str | None) -> tuple[TransactionType, ...] | None:
    if value is None:
        return None
    if value == "":
        raise InvalidTransactionQuery("type: não pode ser vazio.")
    types = []
    for item in value.split(","):
        try:
            types.append(TransactionType(item))
        except ValueError as error:
            raise InvalidTransactionQuery("type: use COMPRA e VENDA, sem espaços.") from error
    if len(set(types)) != len(types):
        raise InvalidTransactionQuery("type: não repita o mesmo tipo.")
    return tuple(types)


def _parse_player_id(value: str | None) -> int | None:
    if value is None:
        return None
    if value == "":
        raise InvalidTransactionQuery("player_id: não pode ser vazio.")
    if not POSITIVE_INTEGER.fullmatch(value) or int(value) > MAX_ID:
        raise InvalidTransactionQuery("player_id: deve ser um inteiro positivo, só com dígitos.")
    return int(value)
