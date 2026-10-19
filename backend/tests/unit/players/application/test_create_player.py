from dataclasses import replace

import pytest

from app.modules.players.application.create_player import CreatePlayer
from app.modules.players.domain.errors import InvalidPlayerData


def test_create_player_saves_the_player_and_commits(
    player_repository, unit_of_work, registration
) -> None:
    player = CreatePlayer(player_repository, unit_of_work).execute(registration)

    assert player.id == 1
    assert player_repository.get(1) is player
    assert unit_of_work.commits == 1


def test_create_player_rejects_invalid_data_without_saving_or_committing(
    player_repository, unit_of_work, registration
) -> None:
    invalid_registration = replace(registration, age=35, agility=86)

    with pytest.raises(InvalidPlayerData):
        CreatePlayer(player_repository, unit_of_work).execute(invalid_registration)

    assert player_repository.stored == {}
    assert unit_of_work.commits == 0
