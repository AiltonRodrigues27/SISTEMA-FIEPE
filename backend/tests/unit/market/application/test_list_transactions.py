from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.clubs.application.public_operations import ClubAccount
from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.market.application.list_transactions import ListTransactions
from app.modules.market.domain.calculations import calculate_sale_outcome
from app.modules.market.domain.history import TransactionFilters
from app.modules.market.domain.transaction import Transaction, TransactionType
from app.modules.players.domain.errors import PlayerNotFound
from app.shared.domain.brasilia_time import BRASILIA

MOMENT = datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA)


def build_use_case(players_operations, clubs_operations, transactions):
    return ListTransactions(players_operations, clubs_operations, transactions)


def add_purchase_and_sale(transactions, club_id=1, player_id=2):
    outcome = calculate_sale_outcome(Decimal("40.00"), Decimal("37.00"), Decimal("4.00"))
    transactions.add(
        Transaction.purchase(
            club_id=club_id,
            player_id=player_id,
            player_name="Meia Lua",
            value=Decimal("37.00"),
            fee=Decimal("1.85"),
            created_at=MOMENT,
        )
    )
    transactions.add(
        Transaction.sale(
            club_id=club_id,
            player_id=player_id,
            player_name="Meia Lua",
            outcome=outcome,
            created_at=MOMENT + timedelta(days=3),
        )
    )


def test_list_transactions_returns_the_most_recent_first_with_the_summary(
    players_operations, clubs_operations, transactions
) -> None:
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal("296.85"))
    add_purchase_and_sale(transactions)

    history = build_use_case(players_operations, clubs_operations, transactions).execute(
        1, TransactionFilters()
    )

    assert [item.type for item in history.transactions] == [
        TransactionType.VENDA,
        TransactionType.COMPRA,
    ]
    assert history.summary.total_spent == Decimal("38.85")
    assert history.summary.total_received == Decimal("35.70")


def test_list_transactions_summary_respects_the_type_filter(
    players_operations, clubs_operations, transactions
) -> None:
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal("296.85"))
    add_purchase_and_sale(transactions)
    filters = TransactionFilters(types=(TransactionType.VENDA,))

    history = build_use_case(players_operations, clubs_operations, transactions).execute(
        1, filters
    )

    assert [item.type for item in history.transactions] == [TransactionType.VENDA]
    assert history.summary.total_spent == Decimal("0.00")
    assert history.summary.total_fees == Decimal("0.30")


def test_list_transactions_filters_by_an_existing_player(
    players_operations, clubs_operations, transactions, make_view
) -> None:
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal("300.00"))
    players_operations.views[2] = make_view(2)
    players_operations.views[3] = make_view(3, "Beto Souza")
    add_purchase_and_sale(transactions, player_id=2)
    add_purchase_and_sale(transactions, player_id=3)

    history = build_use_case(players_operations, clubs_operations, transactions).execute(
        1, TransactionFilters(player_id=3)
    )

    assert {item.player_id for item in history.transactions} == {3}


def test_list_transactions_of_a_club_without_transactions_is_empty_with_zero_totals(
    players_operations, clubs_operations, transactions
) -> None:
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal("300.00"))

    history = build_use_case(players_operations, clubs_operations, transactions).execute(
        1, TransactionFilters()
    )

    assert history.transactions == []
    assert history.summary.total_spent == Decimal("0.00")


def test_list_transactions_raises_not_found_for_unknown_club(
    players_operations, clubs_operations, transactions
) -> None:
    with pytest.raises(ClubNotFound):
        build_use_case(players_operations, clubs_operations, transactions).execute(
            1, TransactionFilters()
        )


def test_list_transactions_raises_not_found_for_unknown_player_filter(
    players_operations, clubs_operations, transactions
) -> None:
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal("300.00"))

    with pytest.raises(PlayerNotFound):
        build_use_case(players_operations, clubs_operations, transactions).execute(
            1, TransactionFilters(player_id=99)
        )
