from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.sqlalchemy_base import Base


class PlayerModel(Base):
    __tablename__ = "jogadores"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column("nome", String(100))
    position: Mapped[str] = mapped_column("posicao", String(3))
    agility: Mapped[int] = mapped_column("agilidade")
    age: Mapped[int] = mapped_column("idade")
    base_value: Mapped[Decimal] = mapped_column("valor_base", Numeric(12, 2))
    condition: Mapped[str] = mapped_column("condicao", String(20))
    club_id: Mapped[int | None] = mapped_column("clube_id", ForeignKey("clubes.id"))
    pace: Mapped[int] = mapped_column("velocidade")
    shooting: Mapped[int] = mapped_column("finalizacao")
    passing: Mapped[int] = mapped_column("passe")
    dribbling: Mapped[int] = mapped_column("drible")
    defending: Mapped[int] = mapped_column("defesa")
    physical: Mapped[int] = mapped_column("fisico")
    potential: Mapped[int] = mapped_column("potencial")
    deleted_at: Mapped[datetime | None] = mapped_column("excluido_em", DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        "criado_em", DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "atualizado_em", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
