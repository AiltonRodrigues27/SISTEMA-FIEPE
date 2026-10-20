import re
import unicodedata
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel

from app.modules.clubs.application.get_club import ClubDetails, ContractView, SquadMember
from app.modules.clubs.domain.entities import ClubView
from app.modules.players.adapters.inbound.http.schemas import PlayerResponse
from app.shared.domain.brasilia_time import format_api_datetime
from app.shared.domain.text import clean_text, has_letter

MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 60
MIN_NAME_WORDS = 2
MAX_NAME_WORDS = 5
ALLOWED_SYMBOLS = " -."
ACRONYM_FORMAT = re.compile(r"[A-Z]{3}")


def _clean_club_name(value: str) -> str:
    name = clean_text(value)
    if not MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH:
        raise ValueError(f"deve ter de {MIN_NAME_LENGTH} a {MAX_NAME_LENGTH} caracteres")
    if not all(
        unicodedata.category(char).startswith("L") or char in ALLOWED_SYMBOLS for char in name
    ):
        raise ValueError("só pode ter letras, espaços, hífen e ponto")
    words = sum(has_letter(part) for part in name.split(" "))
    if not MIN_NAME_WORDS <= words <= MAX_NAME_WORDS:
        raise ValueError(f"deve ter de {MIN_NAME_WORDS} a {MAX_NAME_WORDS} palavras")
    return name


def _check_acronym(value: str) -> str:
    if not ACRONYM_FORMAT.fullmatch(value):
        raise ValueError("deve ter exatamente 3 letras maiúsculas de A a Z")
    return value


ClubName = Annotated[str, AfterValidator(_clean_club_name)]
Acronym = Annotated[str, AfterValidator(_check_acronym)]


class CreateClubRequest(BaseModel):
    name: ClubName
    acronym: Acronym


class ClubResponse(BaseModel):
    id: int
    name: str
    acronym: str
    cash: float
    squad_value: float
    net_worth: float

    @classmethod
    def from_view(cls, view: ClubView) -> Self:
        return cls(
            id=view.club.id,
            name=view.club.name,
            acronym=view.club.acronym,
            cash=float(view.club.cash),
            squad_value=float(view.squad_value),
            net_worth=float(view.net_worth),
        )


class ContractResponse(BaseModel):
    purchase_value: float
    loyalty_until: str
    remaining_days: int
    penalty_rate: int

    @classmethod
    def from_view(cls, view: ContractView) -> Self:
        return cls(
            purchase_value=float(view.purchase_value),
            loyalty_until=format_api_datetime(view.loyalty_until),
            remaining_days=view.remaining_days,
            penalty_rate=view.penalty_percent,
        )


class SquadMemberResponse(PlayerResponse):
    contract: ContractResponse | None

    @classmethod
    def from_member(cls, member: SquadMember) -> Self:
        contract = ContractResponse.from_view(member.contract) if member.contract else None
        player = PlayerResponse.from_view(member.player)
        return cls(**player.model_dump(), contract=contract)


class ClubDetailResponse(ClubResponse):
    players: list[SquadMemberResponse]

    @classmethod
    def from_details(cls, details: ClubDetails) -> Self:
        club = ClubResponse.from_view(details.view)
        squad = [SquadMemberResponse.from_member(member) for member in details.squad]
        return cls(**club.model_dump(), players=squad)
