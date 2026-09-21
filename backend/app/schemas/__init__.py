from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nome: str
    perfil: str


class LoginIn(BaseModel):
    email: str
    senha: str


class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str

    model_config = {"from_attributes": True}


class ClienteOut(BaseModel):
    id: int
    nome: str
    documento: str
    email: Optional[str] = None
    telefone: Optional[str] = None

    model_config = {"from_attributes": True}


class OperacaoBase(BaseModel):
    codigo: str
    cliente_id: Optional[int] = None
    tipo: Optional[str] = None
    valor: Optional[float] = None
    data_operacao: Optional[date] = None
    data_vencimento: Optional[date] = None
    status_operacao: Optional[str] = None
    observacao: Optional[str] = None


class OperacaoCreate(OperacaoBase):
    pass


class OperacaoUpdate(BaseModel):
    codigo: Optional[str] = None
    cliente_id: Optional[int] = None
    tipo: Optional[str] = None
    valor: Optional[float] = None
    data_operacao: Optional[date] = None
    data_vencimento: Optional[date] = None
    status_operacao: Optional[str] = None
    observacao: Optional[str] = None


class OperacaoOut(OperacaoBase):
    id: int
    status_validacao: str
    created_at: Optional[datetime] = None
    cliente: Optional[ClienteOut] = None

    model_config = {"from_attributes": True}


class PendenciaOut(BaseModel):
    id: int
    operacao_id: int
    tipo: str
    descricao: str
    prazo: Optional[date] = None
    status: str
    codigo_operacao: Optional[str] = None

    model_config = {"from_attributes": True}


class PendenciaUpdate(BaseModel):
    status: Optional[str] = None
    prazo: Optional[date] = None
    descricao: Optional[str] = None


class DashboardOut(BaseModel):
    total: int
    ok: int
    pendencias: int
    inconsistencias: int
    por_status: dict[str, int]


class ConsultaIAIn(BaseModel):
    pergunta: str = Field(min_length=3, max_length=500)


class ConsultaIAOut(BaseModel):
    pergunta: str
    resposta: str
    usado_llm: bool
    registros_considerados: int
