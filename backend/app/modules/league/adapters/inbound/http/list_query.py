import re
from collections.abc import Mapping

from fastapi import Request

from app.api.strict_types import MAX_ID
from app.modules.league.domain.errors import InvalidMatchQuery

POSITIVE_INTEGER = re.compile(r"[1-9][0-9]*")


def get_match_club_id(request: Request) -> int | None:
    return parse_match_club_id(request.query_params)


def parse_match_club_id(params: Mapping[str, str]) -> int | None:
    value = params.get("club_id")
    if value is None:
        return None
    if value == "":
        raise InvalidMatchQuery("club_id: não pode ser vazio.")
    if not POSITIVE_INTEGER.fullmatch(value) or int(value) > MAX_ID:
        raise InvalidMatchQuery("club_id: deve ser um inteiro positivo, só com dígitos.")
    return int(value)
