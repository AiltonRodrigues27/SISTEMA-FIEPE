from dataclasses import replace

import pytest

from app.modules.players.application.public_operations import PlayersPublicOperations
from app.modules.players.domain.entities import Player
from app.modules.players.domain.enums import Position
from app.modules.players.domain.errors import PlayerIsFree, PlayerNotFound, PlayerNotFree


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


def test_get_view_returns_the_player(player_repository, registration, saved_player) -> None:
    view = PlayersPublicOperations(player_repository).get_view(saved_player.id)

    assert (view.id, view.name, view.club_id) == (saved_player.id, "Vini Jr", None)


def test_get_view_raises_not_found_for_unknown_id(player_repository) -> None:
    with pytest.raises(PlayerNotFound):
        PlayersPublicOperations(player_repository).get_view(999)


def test_get_free_player_returns_a_player_without_club(player_repository, saved_player) -> None:
    view = PlayersPublicOperations(player_repository).get_free_player(saved_player.id)

    assert view.club_id is None


def test_get_free_player_rejects_a_player_that_has_a_club(player_repository, saved_player) -> None:
    saved_player.club_id = 1

    with pytest.raises(PlayerNotFree):
        PlayersPublicOperations(player_repository).get_free_player(saved_player.id)


def test_get_free_player_raises_not_found_for_unknown_id(player_repository) -> None:
    with pytest.raises(PlayerNotFound):
        PlayersPublicOperations(player_repository).get_free_player(999)


def test_get_player_with_club_returns_a_player_that_has_a_club(
    player_repository, saved_player
) -> None:
    saved_player.club_id = 1

    view = PlayersPublicOperations(player_repository).get_player_with_club(saved_player.id)

    assert view.club_id == 1


def test_get_player_with_club_rejects_a_free_player(player_repository, saved_player) -> None:
    with pytest.raises(PlayerIsFree):
        PlayersPublicOperations(player_repository).get_player_with_club(saved_player.id)


def test_assign_to_club_puts_a_free_player_in_the_squad(player_repository, saved_player) -> None:
    PlayersPublicOperations(player_repository).assign_to_club(saved_player.id, 3)

    assert player_repository.get(saved_player.id).club_id == 3


def test_assign_to_club_rejects_a_player_that_already_has_a_club(
    player_repository, saved_player
) -> None:
    saved_player.club_id = 1

    with pytest.raises(PlayerNotFree):
        PlayersPublicOperations(player_repository).assign_to_club(saved_player.id, 3)

    assert player_repository.get(saved_player.id).club_id == 1


def test_release_from_club_frees_the_player_and_returns_the_previous_club(
    player_repository, saved_player
) -> None:
    saved_player.club_id = 3

    previous_club_id = PlayersPublicOperations(player_repository).release_from_club(saved_player.id)

    assert previous_club_id == 3
    assert player_repository.get(saved_player.id).club_id is None


def test_release_from_club_rejects_a_free_player(player_repository, saved_player) -> None:
    with pytest.raises(PlayerIsFree):
        PlayersPublicOperations(player_repository).release_from_club(saved_player.id)


def test_view_carries_the_calculated_fields(player_repository, registration) -> None:
    add_to_club(player_repository, registration, "Ana Lima", 1)

    view = PlayersPublicOperations(player_repository).list_by_club(1)[0]

    assert view.overall == 75
    assert str(view.market_value) == "40.00"
    assert view.club_id == 1
