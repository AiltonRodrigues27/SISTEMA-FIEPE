from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from app.modules.clubs.domain.errors import InvalidClubData
from app.shared.domain.text import normalize_text

INITIAL_CASH = Decimal("300.00")
MAX_CLUBS = 20


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
