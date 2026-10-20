from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.clubs.application.get_club import GetClub
from app.modules.clubs.domain.contract import Contract, ContractStatus
from app.modules.clubs.domain.errors import ClubNotFound
from app.shared.domain.brasilia_time import BRASILIA


def build_contract(
    player_id: int, club_id: int, loyalty_until: datetime, purchase: str
) -> Contract:
    return Contract(
        id=player_id,
        player_id=player_id,
        club_id=club_id,
        purchase_value=Decimal(purchase),
        loyalty_until=loyalty_until,
        status=ContractStatus.ATIVO,
        started_at=datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA),
        ended_at=None,
    )


def test_get_club_raises_not_found_for_unknown_id(
    club_repository, contract_repository, players_operations, clock
) -> None:
    use_case = GetClub(club_repository, contract_repository, players_operations, clock)

    with pytest.raises(ClubNotFound):
        use_case.execute(999)


def test_get_club_without_players_has_an_empty_squad(
    club_repository, contract_repository, players_operations, clock, add_club
) -> None:
    club = add_club("Águias FC", "AGU")

    details = GetClub(club_repository, contract_repository, players_operations, clock).execute(
        club.id
    )

    assert details.squad == []
    assert str(details.view.squad_value) == "0.00"
    assert str(details.view.net_worth) == "300.00"


def test_get_club_shows_the_squad_with_the_contract_calculated_at_query_time(
    club_repository, contract_repository, players_operations, clock, add_club, make_view
) -> None:
    club = add_club("Águias FC", "AGU", cash="261.15")
    players_operations.views = [make_view(2, "Meia Lua", club.id, "37.00")]
    contract_repository.stored = [
        build_contract(2, club.id, datetime(2027, 3, 2, 10, 15, tzinfo=BRASILIA), "37.00")
    ]

    details = GetClub(club_repository, contract_repository, players_operations, clock).execute(
        club.id
    )

    contract = details.squad[0].contract
    assert details.squad[0].player.name == "Meia Lua"
    assert str(contract.purchase_value) == "37.00"
    assert contract.remaining_days == 120
    assert contract.penalty_percent == 10
    assert str(details.view.squad_value) == "37.00"
    assert str(details.view.net_worth) == "298.15"


def test_get_club_shows_a_player_without_an_active_contract_with_no_contract(
    club_repository, contract_repository, players_operations, clock, add_club, make_view
) -> None:
    club = add_club("Águias FC", "AGU")
    players_operations.views = [make_view(2, "Meia Lua", club.id)]

    details = GetClub(club_repository, contract_repository, players_operations, clock).execute(
        club.id
    )

    assert details.squad[0].contract is None


def test_get_club_ignores_the_squad_of_other_clubs(
    club_repository, contract_repository, players_operations, clock, add_club, make_view
) -> None:
    eagles = add_club("Águias FC", "AGU")
    delta = add_club("Delta FC", "DFC")
    players_operations.views = [
        make_view(1, "Ana Lima", eagles.id),
        make_view(2, "Beto Souza", delta.id),
    ]

    details = GetClub(club_repository, contract_repository, players_operations, clock).execute(
        eagles.id
    )

    assert [member.player.name for member in details.squad] == ["Ana Lima"]
