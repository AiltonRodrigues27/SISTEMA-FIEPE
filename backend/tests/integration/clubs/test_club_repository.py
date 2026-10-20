from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.clubs.adapters.outbound.persistence.contract_repository import (
    SqlAlchemyContractRepository,
)
from app.modules.clubs.adapters.outbound.persistence.models import ContractModel
from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.domain.contract import ContractStatus
from app.modules.clubs.domain.entities import Club
from app.modules.clubs.domain.errors import AcronymAlreadyExists, ClubNameAlreadyExists
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import Position
from app.shared.domain.brasilia_time import BRASILIA

REGISTRATION = PlayerRegistration(
    name="Meia Lua",
    position=Position.MEI,
    agility=85,
    age=25,
    attributes=Attributes(70, 68, 82, 79, 55, 64),
    potential=86,
)


def test_add_assigns_id_and_get_returns_the_same_club(session):
    repository = SqlAlchemyClubRepository(session)

    saved = repository.add(Club.register("Águias FC", "AGU"))
    session.expire_all()

    assert saved.id is not None
    assert repository.get(saved.id) == saved
    assert saved.cash == Decimal("300.00")


def test_get_returns_none_for_unknown_id(session):
    assert SqlAlchemyClubRepository(session).get(999_999) is None


def test_list_all_and_count(session):
    repository = SqlAlchemyClubRepository(session)
    repository.add(Club.register("Águias FC", "AGU"))
    repository.add(Club.register("Delta FC", "DFC"))

    assert sorted(club.name for club in repository.list_all()) == ["Delta FC", "Águias FC"]
    assert repository.count() == 2


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        pytest.param("Águias FC", True, id="same_name"),
        pytest.param("águias fc", True, id="lowercase"),
        pytest.param("ÁGUIAS FC", True, id="uppercase"),
        pytest.param("Aguias FC", False, id="accent_makes_it_a_different_name"),
        pytest.param("Delta FC", False, id="other_name"),
    ],
)
def test_name_exists_ignores_case_but_not_accents(session, name, expected):
    repository = SqlAlchemyClubRepository(session)
    repository.add(Club.register("Águias FC", "AGU"))

    assert repository.name_exists(name) is expected


def test_acronym_exists(session):
    repository = SqlAlchemyClubRepository(session)
    repository.add(Club.register("Águias FC", "AGU"))

    assert repository.acronym_exists("AGU") is True
    assert repository.acronym_exists("DFC") is False


def test_the_database_refuses_a_name_that_differs_only_by_case(session):
    repository = SqlAlchemyClubRepository(session)
    repository.add(Club.register("Águias FC", "AGU"))

    with pytest.raises(ClubNameAlreadyExists):
        repository.add(Club.register("águias fc", "AFC"))


def test_the_database_refuses_a_repeated_acronym(session):
    repository = SqlAlchemyClubRepository(session)
    repository.add(Club.register("Águias FC", "AGU"))

    with pytest.raises(AcronymAlreadyExists):
        repository.add(Club.register("Aguias Futebol", "AGU"))


def test_the_database_accepts_a_name_that_differs_by_accent(session):
    repository = SqlAlchemyClubRepository(session)
    repository.add(Club.register("Águias FC", "AGU"))

    saved = repository.add(Club.register("Aguias FC", "AFC"))

    assert saved.id is not None


def test_list_active_by_club_returns_only_the_active_contracts_of_that_club(session):
    clubs = SqlAlchemyClubRepository(session)
    players = SqlAlchemyPlayerRepository(session)
    eagles = clubs.add(Club.register("Águias FC", "AGU"))
    delta = clubs.add(Club.register("Delta FC", "DFC"))
    active = players.add(Player.register(REGISTRATION))
    ended = players.add(Player.register(REGISTRATION))
    elsewhere = players.add(Player.register(REGISTRATION))
    moment = datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA)
    loyalty = datetime(2027, 3, 2, 10, 15, tzinfo=BRASILIA)
    for player, club, status in [
        (active, eagles, ContractStatus.ATIVO),
        (ended, eagles, ContractStatus.ENCERRADO),
        (elsewhere, delta, ContractStatus.ATIVO),
    ]:
        session.add(
            ContractModel(
                player_id=player.id,
                club_id=club.id,
                purchase_value=Decimal("37.00"),
                loyalty_until=loyalty,
                status=status.value,
                started_at=moment,
            )
        )
    session.flush()

    contracts = SqlAlchemyContractRepository(session).list_active_by_club(eagles.id)

    assert [contract.player_id for contract in contracts] == [active.id]
    assert contracts[0].purchase_value == Decimal("37.00")
    assert contracts[0].status is ContractStatus.ATIVO
    assert contracts[0].loyalty_until == loyalty
