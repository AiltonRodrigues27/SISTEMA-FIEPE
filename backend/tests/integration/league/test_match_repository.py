from datetime import datetime, timedelta

from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.domain.entities import Club
from app.modules.league.adapters.outbound.persistence.match_repository import (
    SqlAlchemyMatchRepository,
)
from app.modules.league.domain.duels import Starter, Team
from app.modules.league.domain.match import Match
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.brasilia_time import BRASILIA

PLAYED_AT = datetime(2026, 11, 12, 15, 0, tzinfo=BRASILIA)
POSITIONS = (Position.GOL, Position.ZAG, Position.LAT, Position.MEI, Position.ATA)


def register_players(session, quantity: int) -> list[Player]:
    players = SqlAlchemyPlayerRepository(session)
    return [
        players.add(
            Player.register(
                PlayerRegistration(
                    name="Jogador Teste",
                    position=POSITIONS[index % 5],
                    agility=85,
                    age=25,
                    attributes=Attributes(70, 68, 82, 79, 55, 64),
                    potential=86,
                )
            )
        )
        for index in range(quantity)
    ]


def build_team(club: Club, players: list[Player], condition=PhysicalCondition.APTO) -> Team:
    starters = [
        Starter(
            player_id=player.id,
            name=f"Titular {index}",
            position=POSITIONS[index],
            condition=condition if index == 2 else PhysicalCondition.APTO,
            shooting=75 + index,
            passing=70 + index,
            dribbling=74 + index,
            defending=60 + index * 5,
        )
        for index, player in enumerate(players)
    ]
    return Team.from_starters(club.id, "2-1-1", starters)


def two_teams(session) -> tuple[Club, Club, Team, Team]:
    clubs = SqlAlchemyClubRepository(session)
    eagles = clubs.add(Club.register("Águias FC", "AGU"))
    delta = clubs.add(Club.register("Delta FC", "DFC"))
    players = register_players(session, 10)
    home = build_team(eagles, players[:5], PhysicalCondition.MAL_CONDICIONADO)
    away = build_team(delta, players[5:])
    return eagles, delta, home, away


def test_add_stores_the_match_and_the_six_duels_and_get_returns_them(session):
    _, _, home, away = two_teams(session)
    repository = SqlAlchemyMatchRepository(session)

    saved = repository.add(Match.play(home, away, PLAYED_AT))
    session.expire_all()

    found = repository.get(saved.id)
    assert saved.id is not None
    assert found == saved
    assert [duel.order for duel in found.duels] == [1, 2, 3, 4, 5, 6]


def test_get_keeps_the_names_conditions_and_values_of_the_moment(session):
    _, _, home, away = two_teams(session)
    repository = SqlAlchemyMatchRepository(session)
    saved = repository.add(Match.play(home, away, PLAYED_AT))
    session.expire_all()

    duel = repository.get(saved.id).duels[2]

    assert duel.attacker.player_name == "Titular 2"
    assert duel.attacker.condition is PhysicalCondition.MAL_CONDICIONADO
    assert (duel.attacker.attribute, duel.defender.attribute) == ("dribbling", "defending")
    assert duel.attacker.value == 65  # dribbling 76 com 15% a menos: 64,6 arredondado


def test_get_returns_none_for_an_unknown_match(session):
    assert SqlAlchemyMatchRepository(session).get(999) is None


def test_list_matches_orders_from_the_most_recent_and_breaks_ties_by_id(session):
    _, _, home, away = two_teams(session)
    repository = SqlAlchemyMatchRepository(session)
    first = repository.add(Match.play(home, away, PLAYED_AT))
    same_moment = repository.add(Match.play(home, away, PLAYED_AT))
    latest = repository.add(Match.play(away, home, PLAYED_AT + timedelta(days=1)))
    session.expire_all()

    found = repository.list_matches(None)

    assert [match.id for match in found] == [latest.id, same_moment.id, first.id]


def test_list_matches_returns_the_matches_without_the_duels(session):
    _, _, home, away = two_teams(session)
    repository = SqlAlchemyMatchRepository(session)
    saved = repository.add(Match.play(home, away, PLAYED_AT))
    session.expire_all()

    found = repository.list_matches(None)

    assert found[0].duels == ()
    assert (found[0].home_goals, found[0].away_goals) == (saved.home_goals, saved.away_goals)


def test_list_matches_filters_by_a_club_that_was_home_or_away(session):
    eagles, delta, home, away = two_teams(session)
    gama = SqlAlchemyClubRepository(session).add(Club.register("Gama SC", "GSC"))
    third_players = register_players(session, 5)
    third = build_team(gama, third_players)
    repository = SqlAlchemyMatchRepository(session)
    first = repository.add(Match.play(home, away, PLAYED_AT))
    second = repository.add(Match.play(away, third, PLAYED_AT + timedelta(hours=1)))
    session.expire_all()

    eagles_matches = repository.list_matches(eagles.id)
    delta_matches = repository.list_matches(delta.id)
    gama_matches = repository.list_matches(gama.id)

    assert [match.id for match in eagles_matches] == [first.id]
    assert [match.id for match in delta_matches] == [second.id, first.id]
    assert [match.id for match in gama_matches] == [second.id]


def test_list_matches_of_a_club_without_matches_is_empty(session):
    eagles, _, _, _ = two_teams(session)

    assert SqlAlchemyMatchRepository(session).list_matches(eagles.id) == []
