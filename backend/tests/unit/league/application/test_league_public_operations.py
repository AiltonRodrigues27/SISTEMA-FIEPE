from app.modules.league.application.public_operations import LeaguePublicOperations


def test_remove_player_takes_the_player_out_of_the_lineup(lineups) -> None:
    lineups.replace(1, [30, 31, 32, 33, 34])

    LeaguePublicOperations(lineups).remove_player(34)

    assert lineups.list_player_ids(1) == [30, 31, 32, 33]


def test_remove_player_who_is_not_a_starter_changes_nothing(lineups) -> None:
    lineups.replace(1, [30, 31, 32, 33, 34])

    LeaguePublicOperations(lineups).remove_player(99)

    assert lineups.list_player_ids(1) == [30, 31, 32, 33, 34]
