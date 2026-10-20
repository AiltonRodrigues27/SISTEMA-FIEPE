# Define o formato dos dados que são recebidos e enviados pela API, incluindo validação e serialização.
import string
import unicodedata
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field

from app.modules.players.application.update_player import PlayerProfileChanges
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import PhysicalCondition, Position

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


def _has_letter(word: str) -> bool:
    return any(unicodedata.category(char).startswith("L") for char in word)


def _clean_player_name(value: str) -> str:
    if any(unicodedata.category(char) == "Cc" for char in value):
        raise ValueError("não pode ter caracteres de controle")
    parts = [part for part in value.split(" ") if part]
    name = " ".join(parts)
    if not MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH:
        raise ValueError(f"deve ter de {MIN_NAME_LENGTH} a {MAX_NAME_LENGTH} caracteres")
    if any(char in string.digits for char in name):
        raise ValueError("não pode ter dígitos")
    if sum(_has_letter(part) for part in parts) < MIN_NAME_WORDS:
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
    def from_entity(cls, player: Player) -> Self:
        return cls(
            id=player.id,
            name=player.name,
            position=player.position,
            agility=player.agility,
            age=player.age,
            condition=player.condition,
            base_value=float(player.base_value),
            market_value=float(player.market_value),
            pace=player.attributes.pace,
            shooting=player.attributes.shooting,
            passing=player.attributes.passing,
            dribbling=player.attributes.dribbling,
            defending=player.attributes.defending,
            physical=player.attributes.physical,
            potential=player.potential,
            overall=player.overall,
            club_id=player.club_id,
        )
