import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.domain.entities import Club
from app.modules.league.adapters.outbound.persistence.repository import SqlAlchemyLineupRepository
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import Position

REGISTRATION = PlayerRegistration(
    name="Meia Lua",
    position=Position.MEI,
    agility=85,
    age=25,
    attributes=Attributes(70, 68, 82, 79, 55, 64),
    potential=86,
)


def add_players(session, quantity: int) -> list[int]:
    players = SqlAlchemyPlayerRepository(session)
    return [players.add(Player.register(REGISTRATION)).id for _ in range(quantity)]


def add_clubs(session) -> tuple[int, int]:
    clubs = SqlAlchemyClubRepository(session)
    eagles = clubs.add(Club.register("Águias FC", "AGU"))
    delta = clubs.add(Club.register("Delta FC", "DFC"))
    return eagles.id, delta.id


def test_list_player_ids_of_a_club_without_lineup_is_empty(session):
    club_id, _ = add_clubs(session)

    assert SqlAlchemyLineupRepository(session).list_player_ids(club_id) == []


def test_replace_stores_the_starters_of_the_club(session):
    club_id, _ = add_clubs(session)
    player_ids = add_players(session, 5)
    repository = SqlAlchemyLineupRepository(session)

    repository.replace(club_id, player_ids)
    session.expire_all()

    assert sorted(repository.list_player_ids(club_id)) == sorted(player_ids)


def test_replace_swaps_the_whole_lineup_and_leaves_other_clubs_alone(session):
    eagles_id, delta_id = add_clubs(session)
    player_ids = add_players(session, 7)
    repository = SqlAlchemyLineupRepository(session)
    repository.replace(eagles_id, player_ids[:5])
    repository.replace(delta_id, player_ids[5:])

    repository.replace(eagles_id, player_ids[1:5] + [player_ids[0]])
    repository.replace(eagles_id, player_ids[2:5])
    session.expire_all()

    assert sorted(repository.list_player_ids(eagles_id)) == sorted(player_ids[2:5])
    assert sorted(repository.list_player_ids(delta_id)) == sorted(player_ids[5:])


def test_replace_can_put_back_a_player_that_was_already_in_the_lineup(session):
    club_id, _ = add_clubs(session)
    player_ids = add_players(session, 5)
    repository = SqlAlchemyLineupRepository(session)
    repository.replace(club_id, player_ids)

    repository.replace(club_id, player_ids)
    session.expire_all()

    assert sorted(repository.list_player_ids(club_id)) == sorted(player_ids)


def test_remove_player_takes_out_only_that_player(session):
    club_id, _ = add_clubs(session)
    player_ids = add_players(session, 5)
    repository = SqlAlchemyLineupRepository(session)
    repository.replace(club_id, player_ids)

    repository.remove_player(player_ids[0])
    session.expire_all()

    assert sorted(repository.list_player_ids(club_id)) == sorted(player_ids[1:])


def test_remove_player_who_is_not_a_starter_changes_nothing(session):
    club_id, _ = add_clubs(session)
    player_ids = add_players(session, 6)
    repository = SqlAlchemyLineupRepository(session)
    repository.replace(club_id, player_ids[:5])

    repository.remove_player(player_ids[5])
    session.expire_all()

    assert sorted(repository.list_player_ids(club_id)) == sorted(player_ids[:5])


def test_the_database_refuses_a_player_in_two_lineups(session):
    eagles_id, delta_id = add_clubs(session)
    player_id = add_players(session, 1)[0]
    repository = SqlAlchemyLineupRepository(session)
    repository.replace(eagles_id, [player_id])

    with pytest.raises(IntegrityError):
        repository.replace(delta_id, [player_id])
