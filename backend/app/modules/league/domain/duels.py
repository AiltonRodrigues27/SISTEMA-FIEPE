from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.rounding import round_half_up

TIRED_PLAYER_FACTOR = Decimal("0.85")
DEFENSE_ATTRIBUTE = "defending"
ATTACK_ATTRIBUTE_BY_POSITION = {
    Position.ATA: "shooting",
    Position.MEI: "passing",
    Position.ZAG: "dribbling",
    Position.LAT: "dribbling",
}
# Cada ataque de um time: (jogador de linha que ataca, adversário que defende). Os jogadores de
# linha são numerados de 0 (o mais recuado) a 3 (o mais avançado); None é o goleiro.
ATTACK_PAIRINGS = ((3, None), (2, 0), (1, 1))
HOME_FIRST_DUEL = 1
AWAY_FIRST_DUEL = 4


@dataclass(frozen=True)
class Starter:
    player_id: int
    name: str
    position: Position
    condition: PhysicalCondition
    shooting: int
    passing: int
    dribbling: int
    defending: int

    def value_of(self, attribute: str) -> int:
        value = getattr(self, attribute)
        if self.condition is PhysicalCondition.MAL_CONDICIONADO:
            return int(round_half_up(Decimal(value) * TIRED_PLAYER_FACTOR, 0))
        return value


@dataclass(frozen=True)
class Team:
    club_id: int
    formation: str
    goalkeeper: Starter
    field_players: tuple[Starter, ...]

    @classmethod
    def from_starters(cls, club_id: int, formation: str, starters: Sequence[Starter]) -> Self:
        goalkeeper, *field_players = starters
        return cls(club_id, formation, goalkeeper, tuple(field_players))


@dataclass(frozen=True)
class DuelPlayer:
    player_id: int
    player_name: str
    position: Position
    condition: PhysicalCondition
    attribute: str
    value: int


@dataclass(frozen=True)
class Duel:
    order: int
    attacking_club_id: int
    attacker: DuelPlayer
    defender: DuelPlayer
    goal: bool


def play_duels(home: Team, away: Team) -> list[Duel]:
    return [
        *_attacks(home, away, HOME_FIRST_DUEL),
        *_attacks(away, home, AWAY_FIRST_DUEL),
    ]


def count_goals(duels: Sequence[Duel], club_id: int) -> int:
    return sum(1 for duel in duels if duel.goal and duel.attacking_club_id == club_id)


def _attacks(attacking: Team, defending: Team, first_order: int) -> list[Duel]:
    duels = []
    for offset, (attacker_index, defender_index) in enumerate(ATTACK_PAIRINGS):
        attacker = attacking.field_players[attacker_index]
        defender = (
            defending.goalkeeper
            if defender_index is None
            else defending.field_players[defender_index]
        )
        duels.append(_duel(first_order + offset, attacking.club_id, attacker, defender))
    return duels


def _duel(order: int, attacking_club_id: int, attacker: Starter, defender: Starter) -> Duel:
    attack = _duel_player(attacker, ATTACK_ATTRIBUTE_BY_POSITION[attacker.position])
    defense = _duel_player(defender, DEFENSE_ATTRIBUTE)
    return Duel(order, attacking_club_id, attack, defense, goal=attack.value > defense.value)


def _duel_player(starter: Starter, attribute: str) -> DuelPlayer:
    return DuelPlayer(
        player_id=starter.player_id,
        player_name=starter.name,
        position=starter.position,
        condition=starter.condition,
        attribute=attribute,
        value=starter.value_of(attribute),
    )
