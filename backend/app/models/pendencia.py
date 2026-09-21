from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Pendencia(Base):
    __tablename__ = "pendencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    operacao_id: Mapped[int] = mapped_column(ForeignKey("operacoes.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(40))
    descricao: Mapped[str] = mapped_column(Text)
    prazo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pendente", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    operacao: Mapped[Operacao] = relationship(back_populates="pendencias")
