# Define o formato dos dados que são recebidos e enviados pela API, incluindo validação e serialização.
import string
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field

from app.modules.players.application.list_players import PlayersPage
from app.modules.players.application.public_operations import PlayerView
from app.modules.players.application.update_player import PlayerProfileChanges
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.text import clean_text, has_letter

MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 100
MIN_NAME_WORDS = 2


def _to_strict_integer(value: object) -> object:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError("deve ser um número inteiro")
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError("deve ser um número inteiro, sem parte fracionária")
        return int(value)
    return value


def _clean_player_name(value: str) -> str:
    name = clean_text(value)
    if not MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH:
        raise ValueError(f"deve ter de {MIN_NAME_LENGTH} a {MAX_NAME_LENGTH} caracteres")
    if any(char in string.digits for char in name):
        raise ValueError("não pode ter dígitos")
    if sum(has_letter(part) for part in name.split(" ")) < MIN_NAME_WORDS:
        raise ValueError(f"deve ter pelo menos {MIN_NAME_WORDS} palavras")
    return name


StrictInt = Annotated[int, BeforeValidator(_to_strict_integer)]
PlayerName = Annotated[str, AfterValidator(_clean_player_name)]
Agility = Annotated[StrictInt, Field(ge=1, le=100)]
Age = Annotated[StrictInt, Field(ge=16, le=45)]
Rating = Annotated[StrictInt, Field(ge=1, le=99)]


class CreatePlayerRequest(BaseModel):
    name: PlayerName
    position: Position
    agility: Agility
    age: Age
    pace: Rating
    shooting: Rating
    passing: Rating
    dribbling: Rating
    defending: Rating
    physical: Rating
    potential: Rating

    def to_registration(self) -> PlayerRegistration:
        return PlayerRegistration(
            name=self.name,
            position=self.position,
            agility=self.agility,
            age=self.age,
            attributes=Attributes(
                pace=self.pace,
                shooting=self.shooting,
                passing=self.passing,
                dribbling=self.dribbling,
                defending=self.defending,
                physical=self.physical,
            ),
            potential=self.potential,
        )


class UpdatePlayerRequest(BaseModel):
    name: PlayerName
    position: Position
    agility: Agility
    age: Age

    def to_changes(self) -> PlayerProfileChanges:
        return PlayerProfileChanges(
            name=self.name, position=self.position, agility=self.agility, age=self.age
        )


class ChangeConditionRequest(BaseModel):
    condition: PhysicalCondition


class PlayerResponse(BaseModel):
    id: int
    name: str
    position: Position
    agility: int
    age: int
    condition: PhysicalCondition
    base_value: float
    market_value: float
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physical: int
    potential: int
    overall: int
    club_id: int | None

    @classmethod
    def from_view(cls, view: PlayerView) -> Self:
        return cls(
            id=view.id,
            name=view.name,
            position=view.position,
            agility=view.agility,
            age=view.age,
            condition=view.condition,
            base_value=float(view.base_value),
            market_value=float(view.market_value),
            pace=view.attributes.pace,
            shooting=view.attributes.shooting,
            passing=view.attributes.passing,
            dribbling=view.attributes.dribbling,
            defending=view.attributes.defending,
            physical=view.attributes.physical,
            potential=view.potential,
            overall=view.overall,
            club_id=view.club_id,
        )

    @classmethod
    def from_entity(cls, player: Player) -> Self:
        return cls.from_view(PlayerView.from_entity(player))


class PageMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int


class PlayersPageResponse(BaseModel):
    data: list[PlayerResponse]
    meta: PageMeta

    @classmethod
    def from_page(cls, page: PlayersPage) -> Self:
        return cls(
            data=[PlayerResponse.from_entity(player) for player in page.players],
            meta=PageMeta(
                page=page.page,
                limit=page.limit,
                total_items=page.total_items,
                total_pages=page.total_pages,
            ),
        )
