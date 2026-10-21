from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.clubs.application.public_operations import (
    ClubsPublicOperations,
    PlayerSigning,
)
from app.modules.clubs.domain.contract import Contract, ContractStatus
from app.modules.clubs.domain.errors import (
    ClubNotFound,
    ContractNotFound,
    InvalidLoyaltyDate,
    SquadFull,
)
from app.shared.domain.brasilia_time import BRASILIA

NOW = datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA)
LOYALTY_UNTIL = datetime(2027, 3, 2, 10, 15, tzinfo=BRASILIA)


def build_operations(club_repository, contract_repository, players_operations):
    return ClubsPublicOperations(club_repository, contract_repository, players_operations)


def build_signing(club_id: int, loyalty_until: datetime = LOYALTY_UNTIL) -> PlayerSigning:
    return PlayerSigning(
        club_id=club_id,
        player_id=2,
        purchase_value=Decimal("37.00"),
        total_cost=Decimal("38.85"),
        loyalty_until=loyalty_until,
    )


def test_exists_tells_if_the_club_is_registered(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU")
    operations = build_operations(club_repository, contract_repository, players_operations)

    assert operations.exists(club.id) is True
    assert operations.exists(999) is False


def test_get_account_returns_the_cash(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU", cash="261.15")
    operations = build_operations(club_repository, contract_repository, players_operations)

    account = operations.get_account(club.id)

    assert (account.club_id, account.cash) == (club.id, Decimal("261.15"))


def test_get_account_raises_not_found_for_unknown_club(
    club_repository, contract_repository, players_operations
) -> None:
    operations = build_operations(club_repository, contract_repository, players_operations)

    with pytest.raises(ClubNotFound):
        operations.get_account(999)


def test_sign_player_debits_the_total_cost_and_opens_an_active_contract(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU")
    operations = build_operations(club_repository, contract_repository, players_operations)

    signed = operations.sign_player(build_signing(club.id), NOW)

    assert club_repository.get(club.id).cash == Decimal("261.15")
    assert (signed.purchase_value, signed.loyalty_until, signed.status) == (
        Decimal("37.00"),
        LOYALTY_UNTIL,
        "ATIVO",
    )
    stored = contract_repository.stored[0]
    assert (stored.player_id, stored.club_id, stored.started_at) == (2, club.id, NOW)


def test_sign_player_rejects_a_full_squad_without_charging(
    club_repository, contract_repository, players_operations, add_club, make_view
) -> None:
    club = add_club("Águias FC", "AGU")
    players_operations.views = [
        make_view(number, f"Jogador {number}", club.id) for number in range(12)
    ]
    operations = build_operations(club_repository, contract_repository, players_operations)

    with pytest.raises(SquadFull):
        operations.sign_player(build_signing(club.id), NOW)

    assert club_repository.get(club.id).cash == Decimal("300.00")
    assert contract_repository.stored == []


@pytest.mark.parametrize(
    "offset",
    [
        pytest.param(timedelta(0), id="exactly_now"),
        pytest.param(timedelta(days=-1), id="in_the_past"),
        pytest.param(timedelta(days=1095, minutes=1), id="beyond_one_thousand_ninety_five_days"),
    ],
)
def test_sign_player_rejects_a_loyalty_end_out_of_the_window_without_charging(
    club_repository, contract_repository, players_operations, add_club, offset
) -> None:
    club = add_club("Águias FC", "AGU")
    operations = build_operations(club_repository, contract_repository, players_operations)

    with pytest.raises(InvalidLoyaltyDate):
        operations.sign_player(build_signing(club.id, NOW + offset), NOW)

    assert club_repository.get(club.id).cash == Decimal("300.00")
    assert contract_repository.stored == []


def test_sign_player_raises_not_found_for_unknown_club(
    club_repository, contract_repository, players_operations
) -> None:
    operations = build_operations(club_repository, contract_repository, players_operations)

    with pytest.raises(ClubNotFound):
        operations.sign_player(build_signing(999), NOW)


def active_contract(club_id: int) -> Contract:
    return Contract(
        id=1,
        player_id=2,
        club_id=club_id,
        purchase_value=Decimal("37.00"),
        loyalty_until=LOYALTY_UNTIL,
        status=ContractStatus.ATIVO,
        started_at=NOW,
        ended_at=None,
    )


def test_terminate_contract_applies_the_penalty_and_marks_it_rescinded(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU")
    contract_repository.stored = [active_contract(club.id)]
    operations = build_operations(club_repository, contract_repository, players_operations)
    sale_moment = datetime(2026, 11, 5, 16, 40, tzinfo=BRASILIA)

    termination = operations.terminate_contract(2, Decimal("40.00"), sale_moment)

    assert termination.purchase_value == Decimal("37.00")
    assert termination.remaining_days == 117
    assert termination.penalty_percent == 10
    assert termination.penalty == Decimal("4.00")
    assert termination.status == "RESCINDIDO"
    stored = contract_repository.stored[0]
    assert (stored.status, stored.ended_at) == (ContractStatus.RESCINDIDO, sale_moment)


def test_terminate_contract_after_the_loyalty_end_has_no_penalty(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU")
    contract_repository.stored = [active_contract(club.id)]
    operations = build_operations(club_repository, contract_repository, players_operations)

    termination = operations.terminate_contract(2, Decimal("40.00"), LOYALTY_UNTIL)

    assert termination.remaining_days == 0
    assert termination.penalty == Decimal("0.00")
    assert termination.status == "ENCERRADO"


def test_terminate_contract_without_an_active_contract_raises_not_found(
    club_repository, contract_repository, players_operations
) -> None:
    operations = build_operations(club_repository, contract_repository, players_operations)

    with pytest.raises(ContractNotFound):
        operations.terminate_contract(2, Decimal("40.00"), NOW)


def test_credit_cash_adds_the_amount_and_returns_the_new_cash(
    club_repository, contract_repository, players_operations, add_club
) -> None:
    club = add_club("Águias FC", "AGU", cash="261.15")
    operations = build_operations(club_repository, contract_repository, players_operations)

    new_cash = operations.credit_cash(club.id, Decimal("35.70"))

    assert new_cash == Decimal("296.85")
    assert club_repository.get(club.id).cash == Decimal("296.85")
