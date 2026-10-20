import re
from collections.abc import Mapping
from decimal import Decimal
from enum import Enum
from typing import TypeVar

from fastapi import Request

from app.modules.players.application.list_players import ListPlayersQuery
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import InvalidListQuery
from app.modules.players.domain.listing import PlayerFilters, SortKey
from app.shared.domain.text import clean_text

MAX_ID = 2_147_483_647
MIN_AGE = 16
MAX_AGE = 45
MAX_MARKET_VALUE = Decimal(550)
MIN_SEARCH_LENGTH = 2
MAX_SEARCH_LENGTH = 100
DEFAULT_PAGE = 1
DEFAULT_LIMIT = 10
MAX_LIMIT = 50
MAX_SORT_CRITERIA = 2

EnumType = TypeVar("EnumType", bound=Enum)

POSITIVE_INTEGER = re.compile(r"[1-9][0-9]*")
DECIMAL = re.compile(r"(0|[1-9][0-9]*)(\.[0-9]{1,2})?")


def get_list_players_query(request: Request) -> ListPlayersQuery:
    return parse_list_players_query(request.query_params)


def parse_list_players_query(params: Mapping[str, str]) -> ListPlayersQuery:
    filters = PlayerFilters(
        search=_parse_search(params),
        position=_parse_enum(params, "position", Position),
        condition=_parse_enum(params, "condition", PhysicalCondition),
        free=_parse_free(params),
        club_id=_parse_integer(params, "club_id", 1, MAX_ID),
        min_age=_parse_integer(params, "min_age", MIN_AGE, MAX_AGE),
        max_age=_parse_integer(params, "max_age", MIN_AGE, MAX_AGE),
        min_value=_parse_decimal(params, "min_value"),
        max_value=_parse_decimal(params, "max_value"),
    )
    _ensure_consistent(filters)
    return ListPlayersQuery(
        filters=filters,
        sort=_parse_sort(params),
        page=_parse_integer(params, "page", 1, MAX_ID, DEFAULT_PAGE),
        limit=_parse_integer(params, "limit", 1, MAX_LIMIT, DEFAULT_LIMIT),
    )


def _present(params: Mapping[str, str], name: str) -> str | None:
    value = params.get(name)
    if value == "":
        raise InvalidListQuery(f"{name}: não pode ser vazio.")
    return value


def _parse_search(params: Mapping[str, str]) -> str | None:
    value = _present(params, "search")
    if value is None:
        return None
    try:
        text = clean_text(value)
    except ValueError as error:
        raise InvalidListQuery(f"search: {error}.") from error
    if not MIN_SEARCH_LENGTH <= len(text) <= MAX_SEARCH_LENGTH:
        raise InvalidListQuery(
            f"search: deve ter de {MIN_SEARCH_LENGTH} a {MAX_SEARCH_LENGTH} caracteres."
        )
    return text


def _parse_enum(params: Mapping[str, str], name: str, enum_type: type[EnumType]) -> EnumType | None:
    value = _present(params, name)
    if value is None:
        return None
    try:
        return enum_type(value)
    except ValueError as error:
        raise InvalidListQuery(f"{name}: valor não permitido.") from error


def _parse_free(params: Mapping[str, str]) -> bool | None:
    value = _present(params, "free")
    if value is None:
        return None
    if value not in ("true", "false"):
        raise InvalidListQuery("free: use true ou false.")
    return value == "true"


def _parse_integer(
    params: Mapping[str, str], name: str, minimum: int, maximum: int, default: int | None = None
) -> int | None:
    value = _present(params, name)
    if value is None:
        return default
    if not POSITIVE_INTEGER.fullmatch(value):
        raise InvalidListQuery(f"{name}: deve ser um inteiro positivo, só com dígitos.")
    number = int(value)
    if not minimum <= number <= maximum:
        raise InvalidListQuery(f"{name}: deve estar entre {minimum} e {maximum}.")
    return number


def _parse_decimal(params: Mapping[str, str], name: str) -> Decimal | None:
    value = _present(params, name)
    if value is None:
        return None
    if not DECIMAL.fullmatch(value):
        raise InvalidListQuery(f"{name}: use o formato 10, 10.5 ou 10.55.")
    number = Decimal(value)
    if number > MAX_MARKET_VALUE:
        raise InvalidListQuery(f"{name}: deve estar entre 0 e {MAX_MARKET_VALUE}.")
    return number


def _parse_sort(params: Mapping[str, str]) -> tuple[SortKey, ...]:
    value = _present(params, "sort")
    if value is None:
        return (SortKey.NAME,)
    criteria = []
    for item in value.split(","):
        try:
            criteria.append(SortKey(item))
        except ValueError as error:
            raise InvalidListQuery("sort: valor não permitido.") from error
    fields = {criterion.value.split("_")[0] for criterion in criteria}
    if len(criteria) > MAX_SORT_CRITERIA or len(fields) != len(criteria):
        raise InvalidListQuery("sort: use até dois critérios, sem repetir o campo.")
    return tuple(criteria)


def _ensure_consistent(filters: PlayerFilters) -> None:
    if (
        filters.min_age is not None
        and filters.max_age is not None
        and filters.min_age > filters.max_age
    ):
        raise InvalidListQuery("min_age: não pode ser maior que max_age.")
    if (
        filters.min_value is not None
        and filters.max_value is not None
        and filters.min_value > filters.max_value
    ):
        raise InvalidListQuery("min_value: não pode ser maior que max_value.")
    if filters.free is True and filters.club_id is not None:
        raise InvalidListQuery("free: free=true não combina com club_id.")
