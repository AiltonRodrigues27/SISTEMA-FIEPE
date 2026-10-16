from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sqlalchemy_base import Base


class ClubeModel(Base):
    __tablename__ = "clubes"
    __table_args__ = (
        CheckConstraint(
            "formacao IN ('3-1', '2-2', '2-1-1', '1-2-1')", name="ck_clubes_formacao"
        ),
        Index("uq_clubes_nome_lower", text("lower(nome)"), unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(60))
    sigla: Mapped[str] = mapped_column(CHAR(3), unique=True)
    caixa: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="300.00")
    formacao: Mapped[str | None] = mapped_column(String(5))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ContratoModel(Base):
    __tablename__ = "contratos"
    __table_args__ = (
        CheckConstraint(
            "situacao IN ('ATIVO', 'ENCERRADO', 'RESCINDIDO')", name="ck_contratos_situacao"
        ),
        Index(
            "uq_contratos_jogador_ativo",
            "jogador_id",
            unique=True,
            postgresql_where=text("situacao = 'ATIVO'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    jogador_id: Mapped[int] = mapped_column(ForeignKey("jogadores.id"))
    clube_id: Mapped[int] = mapped_column(ForeignKey("clubes.id"))
    valor_compra: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fidelidade_ate: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    situacao: Mapped[str] = mapped_column(String(12))
    iniciado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    encerrado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
