from dataclasses import replace

from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.domain.entities import Club
from app.modules.players.adapters.outbound.persistence.models import PlayerModel
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import PhysicalCondition, Position

REGISTRATION = PlayerRegistration(
    name="Vini Jr",
    position=Position.MEI,
    agility=85,
    age=25,
    attributes=Attributes(
        pace=70, shooting=68, passing=82, dribbling=79, defending=55, physical=64
    ),
    potential=86,
)


def test_add_assigns_id_and_get_returns_the_same_player(session):
    repository = SqlAlchemyPlayerRepository(session)

    saved = repository.add(Player.register(REGISTRATION))
    session.expire_all()

    assert saved.id is not None
    assert repository.get(saved.id) == saved


def test_get_returns_none_for_unknown_id(session):
    assert SqlAlchemyPlayerRepository(session).get(999_999) is None


def test_update_persists_the_changes(session):
    repository = SqlAlchemyPlayerRepository(session)
    saved = repository.add(Player.register(REGISTRATION))

    saved.update_profile("Vinicius Junior", Position.ATA, 80, 26)
    saved.change_condition(PhysicalCondition.DOENTE)
    repository.update(saved)
    session.expire_all()

    assert repository.get(saved.id) == saved


def test_mark_deleted_hides_the_player_but_keeps_the_row(session):
    repository = SqlAlchemyPlayerRepository(session)
    saved = repository.add(Player.register(REGISTRATION))

    repository.mark_deleted(saved.id)
    session.expire_all()

    assert repository.get(saved.id) is None
    row = session.get(PlayerModel, saved.id)
    assert row is not None
    assert row.deleted_at is not None


def test_list_by_club_and_list_in_clubs_return_only_players_with_a_club(session):
    clubs = SqlAlchemyClubRepository(session)
    repository = SqlAlchemyPlayerRepository(session)
    eagles = clubs.add(Club.register("Águias FC", "AGU"))
    delta = clubs.add(Club.register("Delta FC", "DFC"))
    in_eagles = repository.add(Player.register(REGISTRATION))
    in_delta = repository.add(Player.register(replace(REGISTRATION, name="Beto Souza")))
    repository.add(Player.register(replace(REGISTRATION, name="Caio Dias")))
    for player, club in [(in_eagles, eagles), (in_delta, delta)]:
        player.assign_to(club.id)
        repository.update(player)
    session.expire_all()

    assert [player.id for player in repository.list_by_club(eagles.id)] == [in_eagles.id]
    assert sorted(player.id for player in repository.list_in_clubs()) == sorted(
        [in_eagles.id, in_delta.id]
    )


def test_list_by_club_does_not_return_deleted_players(session):
    clubs = SqlAlchemyClubRepository(session)
    repository = SqlAlchemyPlayerRepository(session)
    eagles = clubs.add(Club.register("Águias FC", "AGU"))
    player = repository.add(Player.register(REGISTRATION))
    player.assign_to(eagles.id)
    repository.update(player)
    repository.mark_deleted(player.id)
    session.expire_all()

    assert repository.list_by_club(eagles.id) == []
    assert repository.list_in_clubs() == []


def test_list_active_returns_only_the_players_that_were_not_deleted(session):
    repository = SqlAlchemyPlayerRepository(session)
    kept = repository.add(Player.register(REGISTRATION))
    deleted = repository.add(Player.register(replace(REGISTRATION, name="Beto Souza")))
    repository.mark_deleted(deleted.id)
    session.expire_all()

    assert repository.list_active() == [kept]
