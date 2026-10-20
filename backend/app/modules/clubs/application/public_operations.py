from app.modules.clubs.ports.repositories import ClubRepository


class ClubsPublicOperations:
    def __init__(self, clubs: ClubRepository) -> None:
        self._clubs = clubs

    def exists(self, club_id: int) -> bool:
        return self._clubs.get(club_id) is not None
