from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sqlalchemy_base import Base


class TransactionModel(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column("clube_id", ForeignKey("clubes.id"))
    player_id: Mapped[int] = mapped_column("jogador_id", ForeignKey("jogadores.id"))
    player_name: Mapped[str] = mapped_column("nome_jogador", String(100))
    type: Mapped[str] = mapped_column("tipo", String(6))
    value: Mapped[Decimal] = mapped_column("valor", Numeric(12, 2))
    fee: Mapped[Decimal] = mapped_column("taxa", Numeric(12, 2))
    penalty: Mapped[Decimal] = mapped_column("multa", Numeric(12, 2))
    profit: Mapped[Decimal | None] = mapped_column("lucro", Numeric(12, 2))
    cash_change: Mapped[Decimal] = mapped_column("variacao_caixa", Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(
        "criado_em", DateTime(timezone=True), server_default=func.now()
    )
