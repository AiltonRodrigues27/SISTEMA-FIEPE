import pytest

from app.modules.players.application.delete_player import DeletePlayer
from app.modules.players.domain.errors import PlayerHasClub, PlayerNotFound


def test_delete_player_removes_a_free_player_and_commits(
    player_repository, unit_of_work, saved_player
) -> None:
    DeletePlayer(player_repository, unit_of_work).execute(saved_player.id)

    assert player_repository.get(saved_player.id) is None
    assert unit_of_work.commits == 1


def test_delete_player_rejects_player_with_club_without_deleting_or_committing(
    player_repository, unit_of_work, saved_player
) -> None:
    saved_player.club_id = 7

    with pytest.raises(PlayerHasClub):
        DeletePlayer(player_repository, unit_of_work).execute(saved_player.id)

    assert player_repository.get(saved_player.id) is saved_player
    assert unit_of_work.commits == 0


def test_delete_player_raises_not_found_for_unknown_id(player_repository, unit_of_work) -> None:
    with pytest.raises(PlayerNotFound):
        DeletePlayer(player_repository, unit_of_work).execute(999)

    assert unit_of_work.commits == 0


def test_delete_player_twice_raises_not_found_the_second_time(
    player_repository, unit_of_work, saved_player
) -> None:
    use_case = DeletePlayer(player_repository, unit_of_work)
    use_case.execute(saved_player.id)

    with pytest.raises(PlayerNotFound):
        use_case.execute(saved_player.id)

    assert unit_of_work.commits == 1
