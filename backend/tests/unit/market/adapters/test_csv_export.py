from datetime import datetime
from decimal import Decimal

from app.modules.market.adapters.inbound.http.csv_export import build_transactions_csv
from app.modules.market.domain.calculations import calculate_sale_outcome
from app.modules.market.domain.transaction import Transaction
from app.shared.domain.brasilia_time import BRASILIA

HEADER = "data_hora;tipo;jogador;valor;taxa_ou_comissao;multa;lucro;variacao_caixa\n"


def purchase(name: str = "Meia Lua") -> Transaction:
    return Transaction.purchase(
        club_id=1,
        player_id=2,
        player_name=name,
        value=Decimal("37.00"),
        fee=Decimal("1.85"),
        created_at=datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA),
    )


def sale(value: str, purchase_value: str, penalty: str) -> Transaction:
    outcome = calculate_sale_outcome(Decimal(value), Decimal(purchase_value), Decimal(penalty))
    return Transaction.sale(
        club_id=1,
        player_id=2,
        player_name="Meia Lua",
        outcome=outcome,
        created_at=datetime(2026, 11, 5, 16, 40, tzinfo=BRASILIA),
    )


def test_csv_without_transactions_has_only_the_header_line() -> None:
    assert build_transactions_csv([]) == HEADER


def test_csv_follows_the_example_of_the_statement() -> None:
    csv_text = build_transactions_csv([sale("40.00", "37.00", "4.00"), purchase()])

    assert csv_text == (
        HEADER
        + "2026-11-05T16:40:00-03:00;VENDA;Meia Lua;40,00;0,30;4,00;3,00;35,70\n"
        + "2026-11-02T10:15:00-03:00;COMPRA;Meia Lua;37,00;1,85;0,00;;-38,85\n"
    )


def test_csv_writes_a_negative_profit_with_a_minus_sign() -> None:
    csv_text = build_transactions_csv([sale("42.50", "50.00", "8.50")])

    assert csv_text.splitlines()[1].endswith(";42,50;0,00;8,50;-7,50;34,00")


def test_csv_leaves_the_profit_empty_on_a_purchase() -> None:
    line = build_transactions_csv([purchase()]).splitlines()[1]

    assert line.split(";")[6] == ""


def test_csv_puts_a_name_with_a_semicolon_between_double_quotes() -> None:
    line = build_transactions_csv([purchase("Zé; Foguete")]).splitlines()[1]

    assert ';COMPRA;"Zé; Foguete";37,00;' in line


def test_csv_doubles_the_quotes_inside_a_name() -> None:
    line = build_transactions_csv([purchase('Zé "Foguete" Lima')]).splitlines()[1]

    assert ';COMPRA;"Zé ""Foguete"" Lima";37,00;' in line


def test_csv_leaves_a_plain_name_without_quotes() -> None:
    line = build_transactions_csv([purchase()]).splitlines()[1]

    assert ";COMPRA;Meia Lua;" in line


def test_csv_ends_every_line_with_a_line_feed_and_has_no_byte_order_mark() -> None:
    csv_text = build_transactions_csv([purchase(), purchase()])

    assert csv_text.endswith("\n")
    assert "\r" not in csv_text
    assert csv_text.count("\n") == 3
    assert not csv_text.startswith("﻿")
