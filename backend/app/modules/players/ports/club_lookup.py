from typing import Protocol


class ClubLookup(Protocol):
    def exists(self, club_id: int) -> bool:
        """Diz se existe um clube com esse id."""
