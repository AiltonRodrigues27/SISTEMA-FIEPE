import re
from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator, Field

from app.shared.domain.brasilia_time import BRASILIA

MAX_ID = 2_147_483_647
BRASILIA_DATETIME_FORMAT = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2})-03:00"
)


def _to_strict_integer(value: object) -> object:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError("deve ser um número inteiro")
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError("deve ser um número inteiro, sem parte fracionária")
        return int(value)
    return value


def _parse_brasilia_datetime(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("deve ser um texto no formato AAAA-MM-DDTHH:MM-03:00")
    match = BRASILIA_DATETIME_FORMAT.fullmatch(value)
    if match is None:
        raise ValueError("use o formato AAAA-MM-DDTHH:MM-03:00")
    year, month, day, hour, minute = (int(part) for part in match.groups())
    try:
        return datetime(year, month, day, hour, minute, tzinfo=BRASILIA)
    except ValueError as error:
        raise ValueError("data ou hora inexistente") from error


StrictInt = Annotated[int, BeforeValidator(_to_strict_integer)]
ResourceId = Annotated[StrictInt, Field(ge=1, le=MAX_ID)]
BrasiliaDateTime = Annotated[datetime, BeforeValidator(_parse_brasilia_datetime)]
