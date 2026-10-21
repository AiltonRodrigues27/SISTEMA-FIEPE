from typing import Protocol

from app.modules.clubs.domain.entities import Club


class ClubRepository(Protocol):
    def add(self, club: Club) -> Club:
        """Grava o clube novo e o devolve com o id preenchido."""

    def get(self, club_id: int) -> Club | None:
        """Devolve o clube, ou None se não existir."""

    def list_all(self) -> list[Club]:
        """Devolve todos os clubes, em qualquer ordem."""

    def update(self, club: Club) -> None:
        """Grava as mudanças de um clube que já existe (caixa e formação)."""

    def count(self) -> int:
        """Devolve quantos clubes existem."""

    def name_exists(self, name: str) -> bool:
        """Diz se já há clube com esse nome, sem diferenciar maiúsculas e minúsculas."""

    def acronym_exists(self, acronym: str) -> bool:
        """Diz se já há clube com essa sigla."""
