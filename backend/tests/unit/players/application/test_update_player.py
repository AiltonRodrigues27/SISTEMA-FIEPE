from dataclasses import replace

import pytest

from app.modules.players.application.update_player import PlayerProfileChanges, UpdatePlayer
from app.modules.players.domain.enums import Position
from app.modules.players.domain.errors import (
    AgeCannotDecrease,
    InvalidPlayerData,
    PlayerNotFound,
    PositionChangeNotAllowed,
)

CHANGES = PlayerProfileChanges(name="Vinicius Junior", position=Position.ATA, agility=80, age=26)


def test_update_player_changes_only_the_profile_and_commits(
    player_repository, unit_of_work, saved_player
) -> None:
    before = replace(saved_player)

    player = UpdatePlayer(player_repository, unit_of_work).execute(saved_player.id, CHANGES)

    assert player.name == "Vinicius Junior"
    assert player.position is Position.ATA
    assert player.agility == 80
    assert player.age == 26
    assert player.attributes == before.attributes
    assert player.potential == before.potential
    assert player.base_value == before.base_value
    assert unit_of_work.commits == 1


def test_update_player_raises_not_found_for_unknown_id(player_repository, unit_of_work) -> None:
    with pytest.raises(PlayerNotFound):
        UpdatePlayer(player_repository, unit_of_work).execute(999, CHANGES)

    assert unit_of_work.commits == 0


@pytest.mark.parametrize(
    ("club_id", "changes", "error"),
    [
        pytest.param(
            None,
            replace(CHANGES, age=35, agility=86),
            InvalidPlayerData,
            id="agility_above_limit_for_age",
        ),
        pytest.param(7, CHANGES, PositionChangeNotAllowed, id="position_change_with_club"),
        pytest.param(None, replace(CHANGES, age=24), AgeCannotDecrease, id="age_decrease"),
    ],
)
def test_update_player_rejects_invalid_change_without_saving_or_committing(
    player_repository, unit_of_work, saved_player, club_id, changes, error
) -> None:
    saved_player.club_id = club_id
    before = replace(saved_player)

    with pytest.raises(error):
        UpdatePlayer(player_repository, unit_of_work).execute(saved_player.id, changes)

    assert saved_player == before
    assert unit_of_work.commits == 0
