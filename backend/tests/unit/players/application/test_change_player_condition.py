import pytest

from app.modules.players.application.change_player_condition import ChangePlayerCondition
from app.modules.players.domain.enums import PhysicalCondition
from app.modules.players.domain.errors import InvalidConditionTransition, PlayerNotFound


def build_use_case(player_repository, unit_of_work, lineup_gateway) -> ChangePlayerCondition:
    return ChangePlayerCondition(player_repository, unit_of_work, lineup_gateway)


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
    player_repository, unit_of_work, lineup_gateway, saved_player, current, new
) -> None:
    saved_player.condition = current

    player = build_use_case(player_repository, unit_of_work, lineup_gateway).execute(
        saved_player.id, new
    )

    assert player.condition is new
    assert unit_of_work.commits == 1


def test_change_player_condition_rejects_doente_straight_to_apto(
    player_repository, unit_of_work, lineup_gateway, saved_player
) -> None:
    saved_player.condition = PhysicalCondition.DOENTE

    with pytest.raises(InvalidConditionTransition):
        build_use_case(player_repository, unit_of_work, lineup_gateway).execute(
            saved_player.id, PhysicalCondition.APTO
        )

    assert saved_player.condition is PhysicalCondition.DOENTE
    assert unit_of_work.commits == 0
    assert lineup_gateway.removed == []


def test_change_player_condition_raises_not_found_for_unknown_id(
    player_repository, unit_of_work, lineup_gateway
) -> None:
    with pytest.raises(PlayerNotFound):
        build_use_case(player_repository, unit_of_work, lineup_gateway).execute(
            999, PhysicalCondition.DOENTE
        )

    assert unit_of_work.commits == 0
    assert lineup_gateway.removed == []


def test_change_player_condition_to_doente_takes_the_player_out_of_the_lineup(
    player_repository, unit_of_work, lineup_gateway, saved_player
) -> None:
    build_use_case(player_repository, unit_of_work, lineup_gateway).execute(
        saved_player.id, PhysicalCondition.DOENTE
    )

    assert lineup_gateway.removed == [saved_player.id]


@pytest.mark.parametrize(
    "new",
    [PhysicalCondition.APTO, PhysicalCondition.MAL_CONDICIONADO],
)
def test_change_player_condition_to_a_condition_that_can_play_keeps_the_lineup(
    player_repository, unit_of_work, lineup_gateway, saved_player, new
) -> None:
    build_use_case(player_repository, unit_of_work, lineup_gateway).execute(saved_player.id, new)

    assert lineup_gateway.removed == []
