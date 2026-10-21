from dataclasses import replace

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clubs.adapters.outbound.persistence.models import ContractModel
from app.modules.clubs.domain.contract import Contract, ContractStatus
from app.modules.clubs.domain.errors import ContractNotFound
from app.modules.clubs.ports.contracts import ContractRepository


class SqlAlchemyContractRepository(ContractRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, contract: Contract) -> Contract:
        model = ContractModel(
            player_id=contract.player_id,
            club_id=contract.club_id,
            purchase_value=contract.purchase_value,
            loyalty_until=contract.loyalty_until,
            status=contract.status.value,
            started_at=contract.started_at,
            ended_at=contract.ended_at,
        )
        self._session.add(model)
        self._session.flush()
        return replace(contract, id=model.id)

    def get_active_by_player(self, player_id: int) -> Contract | None:
        statement = select(ContractModel).where(
            ContractModel.player_id == player_id,
            ContractModel.status == ContractStatus.ATIVO.value,
        )
        model = self._session.scalars(statement).first()
        return _to_entity(model) if model is not None else None

    def list_active_by_club(self, club_id: int) -> list[Contract]:
        statement = select(ContractModel).where(
            ContractModel.club_id == club_id, ContractModel.status == ContractStatus.ATIVO.value
        )
        return [_to_entity(model) for model in self._session.scalars(statement)]

    def update(self, contract: Contract) -> None:
        model = self._session.get(ContractModel, contract.id)
        if model is None:
            raise ContractNotFound("Contrato não encontrado.")
        model.status = contract.status.value
        model.ended_at = contract.ended_at
        self._session.flush()


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
