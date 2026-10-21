from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.clubs.application.public_operations import ClubAccount
from app.modules.clubs.domain.errors import ClubNotFound, SquadFull
from app.modules.market.application.buy_player import BuyPlayer
from app.modules.market.domain.errors import CashLimitExceeded, PlayerAlreadySoldByClub
from app.modules.market.domain.transaction import TransactionType
from app.modules.players.domain.errors import PlayerNotFound, PlayerNotFree
from app.shared.domain.brasilia_time import BRASILIA

LOYALTY_UNTIL = datetime(2027, 3, 2, 10, 15, tzinfo=BRASILIA)


def build_use_case(players_operations, clubs_operations, transactions, clock, unit_of_work):
    return BuyPlayer(players_operations, clubs_operations, transactions, clock, unit_of_work)


def prepare(players_operations, clubs_operations, make_view, market_value="37.00", cash="300.00"):
    players_operations.views[2] = make_view(2, market_value=market_value)
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal(cash))


def assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work):
    assert players_operations.assigned == []
    assert clubs_operations.signed == []
    assert transactions.added == []
    assert unit_of_work.commits == 0


def test_buy_player_charges_value_and_fee_signs_and_records_the_purchase(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view)
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    result = use_case.execute(2, 1, LOYALTY_UNTIL)

    transaction = result.transaction
    assert transaction.type is TransactionType.COMPRA
    assert (transaction.value, transaction.fee) == (Decimal("37.00"), Decimal("1.85"))
    assert transaction.cash_change == Decimal("-38.85")
    assert transaction.player_name == "Meia Lua"
    assert transaction.created_at == clock.now()
    assert result.club_cash == Decimal("261.15")
    assert result.contract.status == "ATIVO"
    signing = clubs_operations.signed[0]
    assert (signing.club_id, signing.player_id) == (1, 2)
    assert (signing.purchase_value, signing.total_cost) == (Decimal("37.00"), Decimal("38.85"))
    assert signing.loyalty_until == LOYALTY_UNTIL
    assert players_operations.assigned == [(2, 1)]
    assert transactions.added == [transaction]
    assert unit_of_work.commits == 1


def test_buy_player_has_no_fee_up_to_thirty(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view, market_value="28.00")
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    result = use_case.execute(2, 1, LOYALTY_UNTIL)

    assert result.transaction.fee == Decimal("0.00")
    assert result.club_cash == Decimal("272.00")


def test_buy_player_raises_not_found_for_unknown_player(
    players_operations, clubs_operations, transactions, clock, unit_of_work
) -> None:
    clubs_operations.accounts[1] = ClubAccount(club_id=1, cash=Decimal("300.00"))
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(PlayerNotFound):
        use_case.execute(2, 1, LOYALTY_UNTIL)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)


def test_buy_player_rejects_a_player_that_already_has_a_club(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view)
    players_operations.views[2] = make_view(2, club_id=3)
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(PlayerNotFree):
        use_case.execute(2, 1, LOYALTY_UNTIL)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)


def test_buy_player_raises_not_found_for_unknown_club(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    players_operations.views[2] = make_view(2)
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(ClubNotFound):
        use_case.execute(2, 1, LOYALTY_UNTIL)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)


def test_buy_player_rejects_the_club_that_already_sold_the_player(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view)
    transactions.sold.add((1, 2))
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(PlayerAlreadySoldByClub):
        use_case.execute(2, 1, LOYALTY_UNTIL)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)


def test_buy_player_lets_another_club_buy_a_player_that_a_club_sold(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view)
    transactions.sold.add((3, 2))
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    use_case.execute(2, 1, LOYALTY_UNTIL)

    assert unit_of_work.commits == 1


def test_buy_player_rejects_a_cost_above_half_of_the_cash(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view, market_value="48.00", cash="100.00")
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(CashLimitExceeded):
        use_case.execute(2, 1, LOYALTY_UNTIL)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)


def test_buy_player_accepts_a_cost_equal_to_half_of_the_cash(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view, market_value="47.62", cash="100.00")
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    result = use_case.execute(2, 1, LOYALTY_UNTIL)

    assert result.transaction.cash_change == Decimal("-50.00")
    assert result.club_cash == Decimal("50.00")


def test_buy_player_writes_nothing_when_signing_fails(
    players_operations, clubs_operations, transactions, clock, unit_of_work, make_view
) -> None:
    prepare(players_operations, clubs_operations, make_view)
    clubs_operations.sign_error = SquadFull("O elenco já tem 12 jogadores.")
    use_case = build_use_case(
        players_operations, clubs_operations, transactions, clock, unit_of_work
    )

    with pytest.raises(SquadFull):
        use_case.execute(2, 1, LOYALTY_UNTIL)

    assert_nothing_was_written(players_operations, clubs_operations, transactions, unit_of_work)
