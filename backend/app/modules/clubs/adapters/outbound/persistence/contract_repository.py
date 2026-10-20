from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clubs.adapters.outbound.persistence.models import ContractModel
from app.modules.clubs.domain.contract import Contract, ContractStatus
from app.modules.clubs.ports.contracts import ContractRepository


class SqlAlchemyContractRepository(ContractRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_active_by_club(self, club_id: int) -> list[Contract]:
        statement = select(ContractModel).where(
            ContractModel.club_id == club_id, ContractModel.status == ContractStatus.ATIVO.value
        )
        return [_to_entity(model) for model in self._session.scalars(statement)]


def _to_entity(model: ContractModel) -> Contract:
    return Contract(
        id=model.id,
        player_id=model.player_id,
        club_id=model.club_id,
        purchase_value=model.purchase_value,
        loyalty_until=model.loyalty_until,
        status=ContractStatus(model.status),
        started_at=model.started_at,
        ended_at=model.ended_at,
    )
