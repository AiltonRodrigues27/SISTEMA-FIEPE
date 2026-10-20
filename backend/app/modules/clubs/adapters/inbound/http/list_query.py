from collections.abc import Mapping

from fastapi import Request

from app.modules.clubs.domain.errors import InvalidClubQuery
from app.modules.clubs.domain.listing import ClubSortKey


def get_club_sort(request: Request) -> ClubSortKey:
    return parse_club_sort(request.query_params)


def parse_club_sort(params: Mapping[str, str]) -> ClubSortKey:
    value = params.get("sort")
    if value is None:
        return ClubSortKey.NAME
    if value == "":
        raise InvalidClubQuery("sort: não pode ser vazio.")
    try:
        return ClubSortKey(value)
    except ValueError as error:
        raise InvalidClubQuery("sort: valor não permitido.") from error
