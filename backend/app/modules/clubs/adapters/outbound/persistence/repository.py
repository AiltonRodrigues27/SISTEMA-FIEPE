from sqlalchemy import exists, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.clubs.adapters.outbound.persistence.models import ClubModel
from app.modules.clubs.domain.entities import Club
from app.modules.clubs.domain.errors import AcronymAlreadyExists, ClubNameAlreadyExists
from app.modules.clubs.ports.repositories import ClubRepository
from app.shared.domain.errors import DomainError

NAME_UNIQUE_INDEX = "uq_clubes_nome_lower"
ACRONYM_UNIQUE_CONSTRAINT = "clubes_sigla_key"


class SqlAlchemyClubRepository(ClubRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, club: Club) -> Club:
        model = ClubModel(
            name=club.name, acronym=club.acronym, cash=club.cash, formation=club.formation
        )
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as error:
            domain_error = _domain_error_for(error)
            if domain_error is None:
                raise
            raise domain_error from error
        club.id = model.id
        return club

    def get(self, club_id: int) -> Club | None:
        model = self._session.get(ClubModel, club_id)
        return _to_entity(model) if model is not None else None

    def list_all(self) -> list[Club]:
        return [_to_entity(model) for model in self._session.scalars(select(ClubModel))]

    def count(self) -> int:
        return self._session.scalar(select(func.count()).select_from(ClubModel)) or 0

    def name_exists(self, name: str) -> bool:
        statement = select(exists().where(func.lower(ClubModel.name) == func.lower(name)))
        return bool(self._session.scalar(statement))

    def acronym_exists(self, acronym: str) -> bool:
        return bool(self._session.scalar(select(exists().where(ClubModel.acronym == acronym))))


def _domain_error_for(error: IntegrityError) -> DomainError | None:
    constraint = error.orig.diag.constraint_name
    if constraint == NAME_UNIQUE_INDEX:
        return ClubNameAlreadyExists("Já existe um clube com esse nome.")
    if constraint == ACRONYM_UNIQUE_CONSTRAINT:
        return AcronymAlreadyExists("Já existe um clube com essa sigla.")
    return None


def _to_entity(model: ClubModel) -> Club:
    return Club(
        id=model.id,
        name=model.name,
        acronym=model.acronym,
        cash=model.cash,
        formation=model.formation,
    )
