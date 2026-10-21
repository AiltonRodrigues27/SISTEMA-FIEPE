from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from app.modules.clubs.domain.errors import InsufficientCash, InvalidClubData, SquadFull
from app.shared.domain.text import normalize_text

INITIAL_CASH = Decimal("300.00")
MAX_CLUBS = 20
MAX_SQUAD_SIZE = 12


@dataclass
class Club:
    id: int | None
    name: str
    acronym: str
    cash: Decimal
    formation: str | None

    @classmethod
    def register(cls, name: str, acronym: str) -> Self:
        _ensure_acronym_matches_name(name, acronym)
        return cls(id=None, name=name, acronym=acronym, cash=INITIAL_CASH, formation=None)

    def ensure_squad_has_room(self, squad_size: int) -> None:
        if squad_size >= MAX_SQUAD_SIZE:
            raise SquadFull(f"O elenco já tem {MAX_SQUAD_SIZE} jogadores.")

    def debit(self, amount: Decimal) -> None:
        if amount > self.cash:
            raise InsufficientCash("O caixa do clube não cobre o valor.")
        self.cash -= amount

    def credit(self, amount: Decimal) -> None:
        self.cash += amount


@dataclass(frozen=True)
class ClubView:
    club: Club
    squad_value: Decimal

    @property
    def net_worth(self) -> Decimal:
        return self.club.cash + self.squad_value


def _ensure_acronym_matches_name(name: str, acronym: str) -> None:
    letters = normalize_text(acronym)
    name_letters = normalize_text(name)
    if len(set(letters)) == 1:
        raise InvalidClubData("A sigla não pode ter as três letras iguais.")
    if not name_letters.startswith(letters[0]):
        raise InvalidClubData("A primeira letra da sigla deve ser a primeira letra do nome.")
    if not _appear_in_order(letters, name_letters):
        raise InvalidClubData("As letras da sigla devem aparecer no nome, nessa ordem.")


def _appear_in_order(letters: str, text: str) -> bool:
    remaining = iter(text)
    return all(letter in remaining for letter in letters)
