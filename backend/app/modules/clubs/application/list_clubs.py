from collections import defaultdict
from decimal import Decimal

from app.modules.clubs.domain.entities import ClubView
from app.modules.clubs.domain.listing import ClubSortKey, calculate_squad_value, sort_clubs
from app.modules.clubs.ports.repositories import ClubRepository
from app.modules.players.application.public_operations import PlayersPublicOperations


class ListClubs:
    def __init__(self, clubs: ClubRepository, players: PlayersPublicOperations) -> None:
        self._clubs = clubs
        self._players = players

    def execute(self, sort: ClubSortKey) -> list[ClubView]:
        market_values_by_club: dict[int, list[Decimal]] = defaultdict(list)
        for player in self._players.list_in_clubs():
            market_values_by_club[player.club_id].append(player.market_value)
        views = [
            ClubView(club, calculate_squad_value(market_values_by_club[club.id]))
            for club in self._clubs.list_all()
        ]
        return sort_clubs(views, sort)
