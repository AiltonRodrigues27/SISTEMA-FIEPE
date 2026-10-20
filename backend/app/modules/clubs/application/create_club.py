from decimal import Decimal

from app.modules.clubs.domain.entities import MAX_CLUBS, Club, ClubView
from app.modules.clubs.domain.errors import (
    AcronymAlreadyExists,
    ClubLimitReached,
    ClubNameAlreadyExists,
)
from app.modules.clubs.ports.repositories import ClubRepository
from app.shared.application.unit_of_work import UnitOfWork


class CreateClub:
    def __init__(self, clubs: ClubRepository, unit_of_work: UnitOfWork) -> None:
        self._clubs = clubs
        self._unit_of_work = unit_of_work

    def execute(self, name: str, acronym: str) -> ClubView:
        club = Club.register(name, acronym)
        if self._clubs.name_exists(club.name):
            raise ClubNameAlreadyExists("Já existe um clube com esse nome.")
        if self._clubs.acronym_exists(club.acronym):
            raise AcronymAlreadyExists("Já existe um clube com essa sigla.")
        if self._clubs.count() >= MAX_CLUBS:
            raise ClubLimitReached(f"A liga aceita no máximo {MAX_CLUBS} clubes.")
        saved_club = self._clubs.add(club)
        self._unit_of_work.commit()
        return ClubView(saved_club, Decimal("0.00"))
