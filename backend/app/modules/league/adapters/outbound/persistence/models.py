from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sqlalchemy_base import Base

FORMACOES = "('3-1', '2-2', '2-1-1', '1-2-1')"


class EscalacaoModel(Base):
    __tablename__ = "escalacoes"
    __table_args__ = (UniqueConstraint("jogador_id", name="uq_escalacoes_jogador"),)

    clube_id: Mapped[int] = mapped_column(ForeignKey("clubes.id"), primary_key=True)
    jogador_id: Mapped[int] = mapped_column(ForeignKey("jogadores.id"), primary_key=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PartidaModel(Base):
    __tablename__ = "partidas"
    __table_args__ = (
        CheckConstraint("mandante_id <> visitante_id", name="ck_partidas_clubes_distintos"),
        CheckConstraint("gols_mandante BETWEEN 0 AND 3", name="ck_partidas_gols_mandante"),
        CheckConstraint("gols_visitante BETWEEN 0 AND 3", name="ck_partidas_gols_visitante"),
        CheckConstraint(f"formacao_mandante IN {FORMACOES}", name="ck_partidas_formacao_mandante"),
        CheckConstraint(
            f"formacao_visitante IN {FORMACOES}", name="ck_partidas_formacao_visitante"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mandante_id: Mapped[int] = mapped_column(ForeignKey("clubes.id"))
    visitante_id: Mapped[int] = mapped_column(ForeignKey("clubes.id"))
    gols_mandante: Mapped[int]
    gols_visitante: Mapped[int]
    formacao_mandante: Mapped[str] = mapped_column(String(5))
    formacao_visitante: Mapped[str] = mapped_column(String(5))
    jogada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DueloPartidaModel(Base):
    __tablename__ = "duelos_partida"
    __table_args__ = (
        UniqueConstraint("partida_id", "ordem", name="uq_duelos_partida_ordem"),
        CheckConstraint("ordem BETWEEN 1 AND 6", name="ck_duelos_partida_ordem"),
        CheckConstraint(
            "atributo_ataque IN ('shooting', 'passing', 'dribbling', 'defending')",
            name="ck_duelos_partida_atributo_ataque",
        ),
        CheckConstraint(
            "atributo_defesa IN ('shooting', 'passing', 'dribbling', 'defending')",
            name="ck_duelos_partida_atributo_defesa",
        ),
        CheckConstraint(
            "condicao_atacante IN ('APTO', 'MAL_CONDICIONADO')",
            name="ck_duelos_partida_condicao_atacante",
        ),
        CheckConstraint(
            "condicao_defensor IN ('APTO', 'MAL_CONDICIONADO')",
            name="ck_duelos_partida_condicao_defensor",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    partida_id: Mapped[int] = mapped_column(ForeignKey("partidas.id"))
    ordem: Mapped[int]
    clube_atacante_id: Mapped[int] = mapped_column(ForeignKey("clubes.id"))
    atacante_id: Mapped[int] = mapped_column(ForeignKey("jogadores.id"))
    defensor_id: Mapped[int] = mapped_column(ForeignKey("jogadores.id"))
    nome_atacante: Mapped[str] = mapped_column(String(100))
    nome_defensor: Mapped[str] = mapped_column(String(100))
    posicao_atacante: Mapped[str] = mapped_column(String(3))
    posicao_defensor: Mapped[str] = mapped_column(String(3))
    condicao_atacante: Mapped[str] = mapped_column(String(20))
    condicao_defensor: Mapped[str] = mapped_column(String(20))
    atributo_ataque: Mapped[str] = mapped_column(String(10))
    atributo_defesa: Mapped[str] = mapped_column(String(10))
    valor_ataque: Mapped[int]
    valor_defesa: Mapped[int]
    gol: Mapped[bool]
