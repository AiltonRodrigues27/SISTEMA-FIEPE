from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sqlalchemy_base import Base


class TransacaoModel(Base):
    __tablename__ = "transacoes"
    __table_args__ = (
        CheckConstraint("tipo IN ('COMPRA', 'VENDA')", name="ck_transacoes_tipo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    clube_id: Mapped[int] = mapped_column(ForeignKey("clubes.id"))
    jogador_id: Mapped[int] = mapped_column(ForeignKey("jogadores.id"))
    nome_jogador: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str] = mapped_column(String(6))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    taxa: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    multa: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    lucro: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    variacao_caixa: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
