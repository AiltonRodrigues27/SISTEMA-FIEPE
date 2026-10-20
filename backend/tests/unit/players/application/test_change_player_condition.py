import pytest

from app.modules.players.application.change_player_condition import ChangePlayerCondition
from app.modules.players.domain.enums import PhysicalCondition
from app.modules.players.domain.errors import InvalidConditionTransition, PlayerNotFound


@pytest.mark.parametrize(
    ("current", "new"),
    [
        pytest.param(PhysicalCondition.APTO, PhysicalCondition.MAL_CONDICIONADO, id="apto_to_mal"),
        pytest.param(PhysicalCondition.APTO, PhysicalCondition.DOENTE, id="apto_to_doente"),
        pytest.param(
            PhysicalCondition.DOENTE, PhysicalCondition.MAL_CONDICIONADO, id="doente_to_mal"
        ),
        pytest.param(PhysicalCondition.MAL_CONDICIONADO, PhysicalCondition.APTO, id="mal_to_apto"),
        pytest.param(PhysicalCondition.APTO, PhysicalCondition.APTO, id="same_condition"),
    ],
)
def test_change_player_condition_accepts_allowed_transitions_and_commits(
    player_repository, unit_of_work, saved_player, current, new
) -> None:
    saved_player.condition = current

    player = ChangePlayerCondition(player_repository, unit_of_work).execute(saved_player.id, new)

    assert player.condition is new
    assert unit_of_work.commits == 1


def test_change_player_condition_rejects_doente_straight_to_apto(
    player_repository, unit_of_work, saved_player
) -> None:
    saved_player.condition = PhysicalCondition.DOENTE

    with pytest.raises(InvalidConditionTransition):
        ChangePlayerCondition(player_repository, unit_of_work).execute(
            saved_player.id, PhysicalCondition.APTO
        )

    assert saved_player.condition is PhysicalCondition.DOENTE
    assert unit_of_work.commits == 0


def test_change_player_condition_raises_not_found_for_unknown_id(
    player_repository, unit_of_work
) -> None:
    with pytest.raises(PlayerNotFound):
        ChangePlayerCondition(player_repository, unit_of_work).execute(
            999, PhysicalCondition.DOENTE
        )

    assert unit_of_work.commits == 0
