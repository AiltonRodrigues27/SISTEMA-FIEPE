from dataclasses import dataclass

from app.modules.players.domain.entities import Player
from app.modules.players.domain.errors import ClubFilterNotFound
from app.modules.players.domain.listing import PlayerFilters, SortKey, matches, sort_players
from app.modules.players.ports.club_lookup import ClubLookup
from app.modules.players.ports.repositories import PlayerRepository


@dataclass(frozen=True)
class ListPlayersQuery:
    filters: PlayerFilters
    sort: tuple[SortKey, ...]
    page: int
    limit: int


@dataclass(frozen=True)
class PlayersPage:
    players: list[Player]
    page: int
    limit: int
    total_items: int

    @property
    def total_pages(self) -> int:
        return (self.total_items + self.limit - 1) // self.limit


class ListPlayers:
    def __init__(self, players: PlayerRepository, clubs: ClubLookup) -> None:
        self._players = players
        self._clubs = clubs

    def execute(self, query: ListPlayersQuery) -> PlayersPage:
        club_id = query.filters.club_id
        if club_id is not None and not self._clubs.exists(club_id):
            raise ClubFilterNotFound("Clube não encontrado.")
        found = [player for player in self._players.list_active() if matches(player, query.filters)]
        ordered = sort_players(found, query.sort)
        start = (query.page - 1) * query.limit
        return PlayersPage(
            players=ordered[start : start + query.limit],
            page=query.page,
            limit=query.limit,
            total_items=len(ordered),
        )
