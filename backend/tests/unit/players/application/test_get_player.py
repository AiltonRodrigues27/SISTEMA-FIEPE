import pytest

from app.modules.players.application.create_player import CreatePlayer
from app.modules.players.application.get_player import GetPlayer
from app.modules.players.domain.errors import PlayerNotFound


def test_get_player_returns_the_existing_player(
    player_repository, unit_of_work, registration
) -> None:
    saved = CreatePlayer(player_repository, unit_of_work).execute(registration)

    assert GetPlayer(player_repository).execute(saved.id) is saved


def test_get_player_raises_not_found_for_unknown_id(player_repository) -> None:
    with pytest.raises(PlayerNotFound):
        GetPlayer(player_repository).execute(999)
