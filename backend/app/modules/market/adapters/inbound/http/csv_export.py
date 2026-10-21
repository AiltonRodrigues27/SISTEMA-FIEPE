import csv
import io
from collections.abc import Sequence
from decimal import Decimal

from app.modules.market.domain.transaction import Transaction
from app.shared.domain.brasilia_time import format_api_datetime

HEADER = (
    "data_hora",
    "tipo",
    "jogador",
    "valor",
    "taxa_ou_comissao",
    "multa",
    "lucro",
    "variacao_caixa",
)


def build_transactions_csv(transactions: Sequence[Transaction]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
    writer.writerow(HEADER)
    for transaction in transactions:
        writer.writerow(
            [
                format_api_datetime(transaction.created_at),
                transaction.type.value,
                transaction.player_name,
                _money(transaction.value),
                _money(transaction.fee),
                _money(transaction.penalty),
                _money(transaction.profit) if transaction.profit is not None else "",
                _money(transaction.cash_change),
            ]
        )
    return buffer.getvalue()


def _money(value: Decimal) -> str:
    return f"{value:.2f}".replace(".", ",")
