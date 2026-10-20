from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from app.modules.players.domain.entities import Attributes, Player
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.listing import SortKey, sort_players
from app.modules.players.ports.repositories import PlayerRepository


@dataclass(frozen=True)
class PlayerView:
    id: int
    name: str
    position: Position
    agility: int
    age: int
    condition: PhysicalCondition
    base_value: Decimal
    market_value: Decimal
    attributes: Attributes
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
            base_value=player.base_value,
            market_value=player.market_value,
            attributes=player.attributes,
            potential=player.potential,
            overall=player.overall,
            club_id=player.club_id,
        )


class PlayersPublicOperations:
    def __init__(self, players: PlayerRepository) -> None:
        self._players = players

    def list_by_club(self, club_id: int) -> list[PlayerView]:
        squad = sort_players(self._players.list_by_club(club_id), (SortKey.POSITION,))
        return [PlayerView.from_entity(player) for player in squad]

    def list_in_clubs(self) -> list[PlayerView]:
        return [PlayerView.from_entity(player) for player in self._players.list_in_clubs()]
