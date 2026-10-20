from dataclasses import replace

from app.modules.players.application.public_operations import PlayersPublicOperations
from app.modules.players.domain.entities import Player
from app.modules.players.domain.enums import Position


def add_to_club(player_repository, registration, name, club_id, **changes) -> Player:
    player = player_repository.add(Player.register(replace(registration, name=name, **changes)))
    player.club_id = club_id
    return player


def test_list_by_club_returns_only_that_club_in_squad_order(
    player_repository, registration
) -> None:
    add_to_club(player_repository, registration, "Zeca Lima", 1, position=Position.ATA)
    add_to_club(player_repository, registration, "Beto Souza", 1, position=Position.GOL)
    add_to_club(player_repository, registration, "Ana Lima", 1, position=Position.GOL)
    add_to_club(player_repository, registration, "Caio Dias", 2, position=Position.GOL)

    squad = PlayersPublicOperations(player_repository).list_by_club(1)

    assert [player.name for player in squad] == ["Ana Lima", "Beto Souza", "Zeca Lima"]


def test_list_by_club_without_players_is_empty(player_repository) -> None:
    assert PlayersPublicOperations(player_repository).list_by_club(1) == []


def test_list_in_clubs_returns_only_players_that_have_a_club(
    player_repository, registration
) -> None:
    add_to_club(player_repository, registration, "Ana Lima", 1)
    add_to_club(player_repository, registration, "Beto Souza", 2)
    add_to_club(player_repository, registration, "Caio Dias", None)

    players = PlayersPublicOperations(player_repository).list_in_clubs()

    assert sorted(player.name for player in players) == ["Ana Lima", "Beto Souza"]


def test_view_carries_the_calculated_fields(player_repository, registration) -> None:
    add_to_club(player_repository, registration, "Ana Lima", 1)

    view = PlayersPublicOperations(player_repository).list_by_club(1)[0]

    assert view.overall == 75
    assert str(view.market_value) == "40.00"
    assert view.club_id == 1
