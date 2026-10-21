import pytest

from app.modules.market.adapters.inbound.http.list_query import parse_transaction_filters
from app.modules.market.domain.errors import InvalidTransactionQuery
from app.modules.market.domain.history import TransactionFilters
from app.modules.market.domain.transaction import TransactionType

INVALID_PARAMETERS = [
    ("type", ""),
    ("type", "compra"),
    ("type", "Venda"),
    ("type", "COMPRA,compra"),
    ("type", "COMPRA,COMPRA"),
    ("type", "COMPRA, VENDA"),
    ("type", "COMPRA,"),
    ("type", ",VENDA"),
    ("type", "COMPRA;VENDA"),
    ("type", "TROCA"),
    ("player_id", ""),
    ("player_id", "0"),
    ("player_id", "01"),
    ("player_id", "-1"),
    ("player_id", "+1"),
    ("player_id", "1.5"),
    ("player_id", "1e2"),
    ("player_id", "abc"),
    ("player_id", " 1"),
    ("player_id", "2147483648"),
]


def test_no_parameters_means_no_filters() -> None:
    assert parse_transaction_filters({}) == TransactionFilters()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("COMPRA", (TransactionType.COMPRA,), id="purchase_only"),
        pytest.param("VENDA", (TransactionType.VENDA,), id="sale_only"),
        pytest.param("COMPRA,VENDA", (TransactionType.COMPRA, TransactionType.VENDA), id="both"),
        pytest.param(
            "VENDA,COMPRA", (TransactionType.VENDA, TransactionType.COMPRA), id="both_reversed"
        ),
    ],
)
def test_type_accepts_one_or_both_values(value, expected) -> None:
    assert parse_transaction_filters({"type": value}).types == expected


def test_player_id_accepts_the_largest_id() -> None:
    assert parse_transaction_filters({"player_id": "2147483647"}).player_id == 2147483647


def test_both_filters_can_be_combined() -> None:
    filters = parse_transaction_filters({"type": "VENDA", "player_id": "7"})

    assert filters == TransactionFilters(types=(TransactionType.VENDA,), player_id=7)


def test_unknown_parameters_are_ignored() -> None:
    assert parse_transaction_filters({"foo": "bar", "Type": "xx"}) == TransactionFilters()


@pytest.mark.parametrize(
    ("name", "value"),
    [pytest.param(name, value, id=f"{name}={value!r}") for name, value in INVALID_PARAMETERS],
)
def test_invalid_parameter_is_rejected(name, value) -> None:
    with pytest.raises(InvalidTransactionQuery):
        parse_transaction_filters({name: value})
