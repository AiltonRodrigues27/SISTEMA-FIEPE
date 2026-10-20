from typing import Protocol

from app.modules.clubs.domain.contract import Contract


class ContractRepository(Protocol):
    def list_active_by_club(self, club_id: int) -> list[Contract]:
        """Devolve os contratos ATIVOS dos jogadores do elenco de um clube."""
