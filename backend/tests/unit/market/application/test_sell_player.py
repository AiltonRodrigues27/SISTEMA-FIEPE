from decimal import Decimal

import pytest

from app.modules.clubs.application.public_operations import ClubAccount, ContractTermination
from app.modules.clubs.domain.errors import ContractNotFound
from app.modules.market.application.sell_player import SellPlayer
from app.modules.market.domain.transaction import TransactionType
from app.modules.players.domain.errors import PlayerIsFree, PlayerNotFound


def build_use_case(players_operations, clubs_operations, transactions, clock, unit_of_work):
    return SellPlayer(players_operations, clubs_operations, transactions, clock, unit_of_work)


def termination(purchase: str, penalty: str, percent: int, days: int) -> ContractTermination:
    return ContractTermination(
        purchase_value=Decimal(purchase),
        remaining_days=days,
        penalty_percent=percent,
        penalty=Decimal(penalty),
        status="RESCINDIDO" if Decimal(penalty) > 0 else "ENCERRADO",
    )


def prepare(players_operations, clubs_operations, make_view, market_value, contract):
    players_operations.views[2] = make_view(2, club_id=1, market_value=market_value)
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal("261.15"))
    clubs_operations.termination = contract


def assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work):
    assert players_operations.released == []
    assert clubs_operations.credits == []
    assert transactions.added == []
    assert unit_of_work.commits == 0


def test_sell_player_frees_the_player_credits_the_cash_and_records_the_sale(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(
        players_operations,
        clubs_operations,
        make_view,
        "40.00",
        termination("37.00", "4.00", 10, 117),
    )
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    result = use_case.execute(2)

    transaction = result.transaction
    assert transaction.type is TransactionType.VENDA
    assert (transaction.value, transaction.fee, transaction.penalty) == (
        Decimal("40.00"),
        Decimal("0.30"),
        Decimal("4.00"),
    )
    assert transaction.profit == Decimal("3.00")
    assert transaction.cash_change == Decimal("35.70")
    assert transaction.created_at == clock.now()
    assert result.club_cash == Decimal("296.85")
    assert result.termination.remaining_days == 117
    assert players_operations.released == [2]
    assert clubs_operations.credits == [(1, Decimal("35.70"))]
    assert transactions.added == [transaction]
    assert unit_of_work.commits == 1


def test_sell_player_at_a_loss_pays_no_commission(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(
        players_operations,
        clubs_operations,
        make_view,
        "42.50",
        termination("50.00", "8.50", 20, 200),
    )
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    result = use_case.execute(2)

    assert result.transaction.profit == Decimal("-7.50")
    assert result.transaction.fee == Decimal("0.00")
    assert result.transaction.cash_change == Decimal("34.00")


def test_sell_player_after_the_loyalty_end_has_no_penalty(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(
        players_operations,
        clubs_operations,
        make_view,
        "25.00",
        termination("25.00", "0.00", 0, 0),
    )
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    result = use_case.execute(2)

    assert result.transaction.penalty == Decimal("0.00")
    assert result.transaction.cash_change == Decimal("25.00")
    assert result.termination.status == "ENCERRADO"


def test_sell_player_rejects_a_free_player(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    players_operations.views[2] = make_view(2, club_id=None)
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(PlayerIsFree):
        use_case.execute(2)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)


def test_sell_player_raises_not_found_for_unknown_player(
    players_operations, clubs_operations, transactions, clock, unit_of_work
) -> None:
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(PlayerNotFound):
        use_case.execute(2)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)


def test_sell_player_writes_nothing_when_the_contract_cannot_be_terminated(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(
        players_operations,
        clubs_operations,
        make_view,
        "40.00",
        termination("37.00", "4.00", 10, 117),
    )
    clubs_operations.termination_error = ContractNotFound("O jogador não tem contrato ativo.")
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(ContractNotFound):
        use_case.execute(2)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)
