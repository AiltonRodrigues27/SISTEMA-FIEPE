from typing import Protocol

from app.modules.clubs.domain.contract import Contract


class ContractRepository(Protocol):
    def add(self, contract: Contract) -> Contract:
        """Grava o contrato novo e o devolve com o id preenchido."""

    def get_active_by_player(self, player_id: int) -> Contract | None:
        """Devolve o contrato ATIVO do jogador, ou None se ele não tiver."""

    def list_active_by_club(self, club_id: int) -> list[Contract]:
        """Devolve os contratos ATIVOS dos jogadores do elenco de um clube."""

    def update(self, contract: Contract) -> None:
        """Grava a situação e a data de encerramento de um contrato que já existe."""
