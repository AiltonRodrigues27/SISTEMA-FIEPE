from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal

from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.domain.entities import Club
from app.modules.market.adapters.outbound.persistence.models import TransactionModel
from app.modules.market.adapters.outbound.persistence.repository import (
    SqlAlchemyTransactionRepository,
)
from app.modules.market.domain.calculations import calculate_sale_outcome
from app.modules.market.domain.history import TransactionFilters
from app.modules.market.domain.transaction import Transaction, TransactionType
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import Position
from app.shared.domain.brasilia_time import BRASILIA

MOMENT = datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA)
REGISTRATION = PlayerRegistration(
    name="Meia Lua",
    position=Position.MEI,
    agility=85,
    age=25,
    attributes=Attributes(70, 68, 82, 79, 55, 64),
    potential=86,
)


def purchase(club, player) -> Transaction:
    return Transaction.purchase(
        club_id=club.id,
        player_id=player.id,
        player_name="Meia Lua",
        value=Decimal("37.00"),
        fee=Decimal("1.85"),
        created_at=MOMENT,
    )


def sale(club, player) -> Transaction:
    outcome = calculate_sale_outcome(Decimal("40.00"), Decimal("37.00"), Decimal("4.00"))
    return Transaction.sale(
        club_id=club.id,
        player_id=player.id,
        player_name="Meia Lua",
        outcome=outcome,
        created_at=MOMENT,
    )


def test_add_stores_a_purchase_with_every_field(session):
    club = SqlAlchemyClubRepository(session).add(Club.register("Águias FC", "AGU"))
    player = SqlAlchemyPlayerRepository(session).add(Player.register(REGISTRATION))

    saved = SqlAlchemyTransactionRepository(session).add(purchase(club, player))
    session.expire_all()

    row = session.get(TransactionModel, saved.id)
    assert saved.id is not None
    assert (row.club_id, row.player_id, row.player_name, row.type) == (
        club.id,
        player.id,
        "Meia Lua",
        "COMPRA",
    )
    assert (row.value, row.fee, row.penalty) == (Decimal("37.00"), Decimal("1.85"), Decimal("0.00"))
    assert row.profit is None
    assert row.cash_change == Decimal("-38.85")
    assert row.created_at == MOMENT


def test_add_stores_a_sale_with_profit_and_penalty(session):
    club = SqlAlchemyClubRepository(session).add(Club.register("Águias FC", "AGU"))
    player = SqlAlchemyPlayerRepository(session).add(Player.register(REGISTRATION))

    saved = SqlAlchemyTransactionRepository(session).add(sale(club, player))
    session.expire_all()

    row = session.get(TransactionModel, saved.id)
    assert row.type == "VENDA"
    assert (row.value, row.fee, row.penalty, row.profit, row.cash_change) == (
        Decimal("40.00"),
        Decimal("0.30"),
        Decimal("4.00"),
        Decimal("3.00"),
        Decimal("35.70"),
    )


def test_list_by_club_orders_from_the_most_recent_and_breaks_ties_by_id(session):
    club = SqlAlchemyClubRepository(session).add(Club.register("Águias FC", "AGU"))
    player = SqlAlchemyPlayerRepository(session).add(Player.register(REGISTRATION))
    repository = SqlAlchemyTransactionRepository(session)
    first = repository.add(purchase(club, player))
    same_moment = repository.add(purchase(club, player))
    sold = repository.add(replace(sale(club, player), created_at=MOMENT + timedelta(days=3)))
    session.expire_all()

    found = repository.list_by_club(club.id, TransactionFilters())

    assert [item.id for item in found] == [sold.id, same_moment.id, first.id]
    assert found[0].profit == Decimal("3.00")


def test_list_by_club_filters_by_type_player_and_club(session):
    clubs = SqlAlchemyClubRepository(session)
    eagles = clubs.add(Club.register("Águias FC", "AGU"))
    delta = clubs.add(Club.register("Delta FC", "DFC"))
    players = SqlAlchemyPlayerRepository(session)
    player = players.add(Player.register(REGISTRATION))
    other_player = players.add(Player.register(REGISTRATION))
    repository = SqlAlchemyTransactionRepository(session)
    bought = repository.add(purchase(eagles, player))
    sold = repository.add(sale(eagles, player))
    other = repository.add(purchase(eagles, other_player))
    repository.add(purchase(delta, player))

    only_sales = repository.list_by_club(
        eagles.id, TransactionFilters(types=(TransactionType.VENDA,))
    )
    only_player = repository.list_by_club(eagles.id, TransactionFilters(player_id=other_player.id))
    everything = repository.list_by_club(eagles.id, TransactionFilters())

    assert [item.id for item in only_sales] == [sold.id]
    assert [item.id for item in only_player] == [other.id]
    assert sorted(item.id for item in everything) == sorted([bought.id, sold.id, other.id])


def test_list_by_club_keeps_the_transactions_of_a_deleted_player(session):
    club = SqlAlchemyClubRepository(session).add(Club.register("Águias FC", "AGU"))
    players = SqlAlchemyPlayerRepository(session)
    player = players.add(Player.register(REGISTRATION))
    repository = SqlAlchemyTransactionRepository(session)
    repository.add(purchase(club, player))
    players.mark_deleted(player.id)
    session.expire_all()

    found = repository.list_by_club(club.id, TransactionFilters())

    assert [item.player_name for item in found] == ["Meia Lua"]


def test_club_sold_player_is_true_only_after_that_club_sold_that_player(session):
    clubs = SqlAlchemyClubRepository(session)
    eagles = clubs.add(Club.register("Águias FC", "AGU"))
    delta = clubs.add(Club.register("Delta FC", "DFC"))
    players = SqlAlchemyPlayerRepository(session)
    player = players.add(Player.register(REGISTRATION))
    other_player = players.add(Player.register(REGISTRATION))
    repository = SqlAlchemyTransactionRepository(session)

    repository.add(purchase(eagles, player))
    assert repository.club_sold_player(eagles.id, player.id) is False

    repository.add(sale(eagles, player))
    assert repository.club_sold_player(eagles.id, player.id) is True
    assert repository.club_sold_player(delta.id, player.id) is False
    assert repository.club_sold_player(eagles.id, other_player.id) is False
