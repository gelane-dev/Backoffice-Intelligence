from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Operacao(Base):
    __tablename__ = "operacoes"
    __table_args__ = (UniqueConstraint("codigo", name="uq_operacoes_codigo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), index=True)
    cliente_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    valor: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    data_operacao: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    data_vencimento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status_validacao: Mapped[str] = mapped_column(String(20), default="ok", index=True)
    status_operacao: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cliente: Mapped[Optional[Cliente]] = relationship(back_populates="operacoes")
    pendencias: Mapped[list[Pendencia]] = relationship(
        back_populates="operacao", cascade="all, delete-orphan"
    )
