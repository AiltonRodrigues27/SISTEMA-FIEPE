from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, DateTime, ForeignKey, Index, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sqlalchemy_base import Base


class ClubModel(Base):
    __tablename__ = "clubes"
    __table_args__ = (Index("uq_clubes_nome_lower", text("lower(nome)"), unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column("nome", String(60))
    acronym: Mapped[str] = mapped_column("sigla", CHAR(3), unique=True)
    cash: Mapped[Decimal] = mapped_column("caixa", Numeric(12, 2), server_default="300.00")
    formation: Mapped[str | None] = mapped_column("formacao", String(5))
    created_at: Mapped[datetime] = mapped_column(
        "criado_em", DateTime(timezone=True), server_default=func.now()
    )


class ContractModel(Base):
    __tablename__ = "contratos"
    __table_args__ = (
        Index(
            "uq_contratos_jogador_ativo",
            "jogador_id",
            unique=True,
            postgresql_where=text("situacao = 'ATIVO'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column("jogador_id", ForeignKey("jogadores.id"))
    club_id: Mapped[int] = mapped_column("clube_id", ForeignKey("clubes.id"))
    purchase_value: Mapped[Decimal] = mapped_column("valor_compra", Numeric(12, 2))
    loyalty_until: Mapped[datetime] = mapped_column("fidelidade_ate", DateTime(timezone=True))
    status: Mapped[str] = mapped_column("situacao", String(12))
    started_at: Mapped[datetime] = mapped_column("iniciado_em", DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column("encerrado_em", DateTime(timezone=True))
