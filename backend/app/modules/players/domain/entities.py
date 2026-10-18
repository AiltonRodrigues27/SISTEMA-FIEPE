# Conceitos e regras de negócio relacionados a entidade Player
from dataclasses import dataclass
from decimal import Decimal
from typing import NamedTuple, Self

from app.modules.players.domain.calculations import calculate_base_value, calculate_overall
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import (
    AgeCannotDecrease,
    InvalidConditionTransition,
    InvalidPlayerData,
    PlayerHasClub,
    PlayerIsFree,
    PlayerNotFree,
    PositionChangeNotAllowed,
)

SENIOR_AGILITY_MIN_AGE = 35
SENIOR_MAX_AGILITY = 85
MAX_ATTRIBUTES_SUM = 480
POTENTIAL_EQUALS_MAX_ATTRIBUTE_MIN_AGE = 33


class Attributes(NamedTuple):
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physical: int


@dataclass(frozen=True)
class PlayerRegistration:
    name: str
    position: Position
    agility: int
    age: int
    attributes: Attributes
    potential: int


@dataclass
class Player:
    id: int | None
    name: str
    position: Position
    agility: int
    age: int
    condition: PhysicalCondition
    club_id: int | None
    base_value: Decimal
    attributes: Attributes
    potential: int

    @property
    def is_free(self) -> bool:
        return self.club_id is None

    @classmethod
    def register(cls, registration: PlayerRegistration) -> Self:
        _ensure_agility_fits_age(registration.agility, registration.age)
        _ensure_attributes_are_consistent(
            registration.attributes, registration.potential, registration.age
        )
        overall = calculate_overall(registration.position, registration.attributes)
        base_value = calculate_base_value(overall, registration.potential, registration.age)
        return cls(
            id=None,
            name=registration.name,
            position=registration.position,
            agility=registration.agility,
            age=registration.age,
            condition=PhysicalCondition.APTO,
            club_id=None,
            base_value=base_value,
            attributes=registration.attributes,
            potential=registration.potential,
        )

    def update_profile(self, name: str, position: Position, agility: int, age: int) -> None:
        _ensure_agility_fits_age(agility, age)
        if position != self.position and not self.is_free:
            raise PositionChangeNotAllowed("Jogador com clube não pode mudar de posição.")
        if age < self.age:
            raise AgeCannotDecrease("A idade do jogador não pode diminuir.")
        self.name = name
        self.position = position
        self.agility = agility
        self.age = age

    def change_condition(self, new_condition: PhysicalCondition) -> None:
        if self.condition is PhysicalCondition.DOENTE and new_condition is PhysicalCondition.APTO:
            raise InvalidConditionTransition("Jogador DOENTE não pode passar direto para APTO.")
        self.condition = new_condition

    def assign_to(self, club_id: int) -> None:
        if not self.is_free:
            raise PlayerNotFree("O jogador já tem clube.")
        self.club_id = club_id

    def release(self) -> int:
        if self.club_id is None:
            raise PlayerIsFree("Jogador livre não pode ser vendido.")
        previous_club_id = self.club_id
        self.club_id = None
        return previous_club_id

    def ensure_can_be_deleted(self) -> None:
        if not self.is_free:
            raise PlayerHasClub("Só jogador livre pode ser excluído.")


def _ensure_agility_fits_age(agility: int, age: int) -> None:
    if age >= SENIOR_AGILITY_MIN_AGE and agility > SENIOR_MAX_AGILITY:
        raise InvalidPlayerData(
            f"Com {SENIOR_AGILITY_MIN_AGE} anos ou mais, a agilidade é no máximo {SENIOR_MAX_AGILITY}."
        )


def _ensure_attributes_are_consistent(attributes: Attributes, potential: int, age: int) -> None:
    if sum(attributes) > MAX_ATTRIBUTES_SUM:
        raise InvalidPlayerData(
            f"A soma dos seis atributos não pode passar de {MAX_ATTRIBUTES_SUM}."
        )
    highest = max(attributes)
    if potential < highest:
        raise InvalidPlayerData("O potencial não pode ser menor que o maior atributo.")
    if age >= POTENTIAL_EQUALS_MAX_ATTRIBUTE_MIN_AGE and potential != highest:
        raise InvalidPlayerData(
            f"Com {POTENTIAL_EQUALS_MAX_ATTRIBUTE_MIN_AGE} anos ou mais, o potencial é igual ao maior atributo."
        )
