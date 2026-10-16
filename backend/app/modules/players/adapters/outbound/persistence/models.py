from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sqlalchemy_base import Base


class JogadorModel(Base):
    __tablename__ = "jogadores"
    __table_args__ = (
        CheckConstraint("posicao IN ('GOL', 'ZAG', 'LAT', 'MEI', 'ATA')", name="ck_jogadores_posicao"),
        CheckConstraint(
            "condicao IN ('APTO', 'MAL_CONDICIONADO', 'DOENTE')", name="ck_jogadores_condicao"
        ),
        CheckConstraint("agilidade BETWEEN 1 AND 100", name="ck_jogadores_agilidade"),
        CheckConstraint("idade BETWEEN 16 AND 45", name="ck_jogadores_idade"),
        CheckConstraint("velocidade BETWEEN 1 AND 99", name="ck_jogadores_velocidade"),
        CheckConstraint("finalizacao BETWEEN 1 AND 99", name="ck_jogadores_finalizacao"),
        CheckConstraint("passe BETWEEN 1 AND 99", name="ck_jogadores_passe"),
        CheckConstraint("drible BETWEEN 1 AND 99", name="ck_jogadores_drible"),
        CheckConstraint("defesa BETWEEN 1 AND 99", name="ck_jogadores_defesa"),
        CheckConstraint("fisico BETWEEN 1 AND 99", name="ck_jogadores_fisico"),
        CheckConstraint("potencial BETWEEN 1 AND 99", name="ck_jogadores_potencial"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    posicao: Mapped[str] = mapped_column(String(3))
    agilidade: Mapped[int]
    idade: Mapped[int]
    valor_base: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    condicao: Mapped[str] = mapped_column(String(20))
    clube_id: Mapped[int | None] = mapped_column(ForeignKey("clubes.id"))
    velocidade: Mapped[int]
    finalizacao: Mapped[int]
    passe: Mapped[int]
    drible: Mapped[int]
    defesa: Mapped[int]
    fisico: Mapped[int]
    potencial: Mapped[int]
    excluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
